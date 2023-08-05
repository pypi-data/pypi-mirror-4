# Copyright 2012 Canonical Ltd.  All rights reserved.
#
# This file is part of lazr.jobrunner
#
# lazr.jobrunner is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# lazr.jobrunner is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with lazr.jobrunner. If not, see <http://www.gnu.org/licenses/>.

__metaclass__ = type

import contextlib
import logging
from unittest import TestCase

import oops
from zope.testing.loghandler import Handler

from lazr.jobrunner.jobrunner import (
    BaseJob,
    JobRunner,
    JobStatus,
    LeaseHeld,
    SuspendJobException,
    )


class FakeJob(BaseJob):

    retry_error_types = ()

    def __init__(self, job_id, failure=None, error_in_queue=False,
                 error_in_suspend=False, error_in_complete=False):
        super(FakeJob, self).__init__(job_id)
        self.unrun = True
        self.failure = failure
        self.notifyOops_called = False
        self.notifyUserError_called = False
        self.queue_call_count = 0
        self.lease_held = False
        self.error_in_queue = error_in_queue
        self.error_in_suspend = error_in_suspend
        self.error_in_complete = error_in_complete

    def save(self):
        pass

    def acquireLease(self):
        if self.lease_held:
            raise LeaseHeld
        self.lease_held = True

    def run(self):
        self.unrun = False
        if self.failure is not None:
            raise self.failure

    def start(self, manage_transaction=False):
        super(FakeJob, self).start(manage_transaction)
        self.save()

    def complete(self, manage_transaction=False):
        if self.error_in_complete:
            raise Exception('complete() failed')
        super(FakeJob, self).complete(manage_transaction)
        self.save()

    def fail(self, manage_transaction=False):
        super(FakeJob, self).fail(manage_transaction)
        self.save()

    def notifyOops(self, oops_report):
        self.notifyOops_called = True

    def queue(self, manage_transaction=False):
        if self.error_in_queue:
            raise Exception('queue() failed')
        super(FakeJob, self).queue(manage_transaction)
        self.queue_call_count += 1

    def suspend(self, manage_transaction=False):
        if self.error_in_suspend:
            raise Exception('suspend() failed')
        super(FakeJob, self).suspend(manage_transaction)

    def notifyUserError(self, exception):
        self.notifyUserError_called = True

    def getOopsVars(self):
        return [('foo', 'bar')]


class VolatileAttributesJob:

    def __init__(self, job_id):
        self.job = FakeJob(job_id)
        self.failed = False

    def run(self):
        self.failed = True
        raise Exception('foo')

    def __getattr__(self, name):
        if name == 'fail' and self.failed:
            raise AttributeError('no access')
        return getattr(self.job, name)


class OOPSTestRepository:
    """Record OOPSes in memory."""

    def __init__(self):
        self.oopses = {}
        self.oops_count = 0

    def publish(self, report):
        self.oops_count += 1
        oops_id = 'OOPS-%i' % self.oops_count
        # We will add an ID but don't want to change the original report.
        report = dict(report)
        report['id'] = oops_id
        self.oopses[oops_id] = report
        return oops_id


class TestJobRunner(TestCase):

    def setUp(self):
        self.logger = logging.getLogger('jobrunner')
        self.logger.setLevel(logging.DEBUG)
        self.log_handler = Handler(self)
        self.log_handler.add(self.logger.name)
        self.oops_config = oops.Config()
        self.oops_repository = OOPSTestRepository()
        self.oops_config.publishers.append(self.oops_repository.publish)
        self.runner = JobRunner(
            logger=self.logger, oops_config=self.oops_config)

    def test_runJob(self):
        """Ensure status is set to completed when a job runs to completion."""
        job_1 = FakeJob(10)
        self.runner.runJob(job_1)
        self.assertEqual(JobStatus.COMPLETED, job_1.status)
        self.assertEqual([job_1], self.runner.completed_jobs)
        # A log entry is recorded that tnhe job is executing.
        self.assertEqual(
            'Running <FakeJob> (ID 10) in status waiting',
            self.log_handler.records[0].msg)

    def test_runJobHandleError(self):
        """If a job finishes without any errors, runJobHandleError()
        works like runJob()."""
        job = FakeJob(1)
        self.runner.runJobHandleError(job)
        # A log entry is recorded that the job is executing.
        self.assertEqual(1, len(self.log_handler.records))
        self.assertEqual(
            'Running <FakeJob> (ID 1) in status waiting',
            self.log_handler.records[0].msg)

    def test_runJobHandleError_failing_job(self):
        """If a job raises an execption, runJobHandleError() logs an OOPS.
        """
        job = FakeJob(1, ValueError('forced error'))
        oops_report = self.runner.runJobHandleError(job)
        # A failing job has two log entries.
        self.assertEqual(2, len(self.log_handler.records))
        # The first entry shows that the job was started.
        self.assertEqual(
            "Running <FakeJob> (ID 1) in status waiting",
            self.log_handler.records[0].msg)
        # The second log entry shows the OOPS number and the exception.
        self.assertEqual(
            ("OOPS while executing job 1: ['OOPS-1'] "
             "ValueError('forced error',)"),
            self.log_handler.records[1].msg)

        # the OOPS is recorded.
        self.assertEqual(
            oops_report, self.oops_repository.oopses[oops_report['id']])
        # It contains some basic information about the failure.
        self.assertEqual('ValueError', oops_report['type'])
        self.assertEqual('forced error', oops_report['value'])
        self.assertTrue('tb_text' in oops_report)

    def test_initial_job_status(self):
        # When a job is created, it has the status WAITING.
        job = FakeJob(1)
        self.assertEqual(JobStatus.WAITING, job.status)

    def test_runJob_calls_fail_on_error(self):
        # If an exception is raised in Job.run(), runJob() calls
        # Job.fail()
        job = FakeJob(2, Exception('forced error'))
        try:
            self.runner.runJob(job)
        except:
            pass
        # Job.fail() changed the job's status,
        self.assertEqual(JobStatus.FAILED, job.status)

    def test_runJobHandleError_calls_notifyOops(self):
        job = FakeJob(1, ValueError('forced error'))
        self.runner.runJobHandleError(job)
        self.assertTrue(job.notifyOops_called)

    def test_runJob_raising_retry_error(self):
        # If a job raises a retry_error, it should be re-queued.
        class TryAgain(Exception):
            pass

        job = FakeJob(1, TryAgain('once more'))
        job.retry_error_types = (TryAgain, )
        job.max_retries = 1
        self.runner.runJob(job)
        self.assertEqual(1, job.queue_call_count)
        self.assertEqual(JobStatus.WAITING, job.status)
        self.assertEqual(
            'Scheduling retry due to TryAgain: once more.',
            self.log_handler.records[-1].msg)

        # Once job.attempt_count has reached job.max_retries,
        # another error from job.retry_error_types leads to a
        # failure like any other exception.
        self.assertEqual(job.attempt_count, job.max_retries)
        self.assertRaises(TryAgain, self.runner.runJob, job)
        self.assertEqual(JobStatus.FAILED, job.status)

    def test_runJob_with_SuspendJobException(self):
        # A job that raises SuspendJobError should end up suspended.
        job = FakeJob(1, SuspendJobException)
        self.runner.runJob(job)
        self.assertEqual(JobStatus.SUSPENDED, job.status)
        self.assertEqual(
            'Job suspended itself',
            self.log_handler.records[-1].msg)

    def test_runJobHandleError_UserError(self):
        # If a job raises an exception that is declared as a user error,
        # an OOPS is not created.
        class UserError(Exception):
            pass

        job = FakeJob(1, UserError('no OOPS expected'))
        job.user_error_types = (UserError, )
        self.assertFalse(job.notifyUserError_called)
        self.runner.runJobHandleError(job)
        self.assertEqual(0, self.oops_repository.oops_count)
        self.assertEqual(
            "<FakeJob> (ID 1) failed with user error "
            "UserError('no OOPS expected',).",
            self.log_handler.records[-1].msg)
        self.assertTrue(job.notifyUserError_called)

    def test_oopsMessage(self):
        # runJobHandleError() executes Job.run() in the context provided
        # by an context manager that may be specified as a constructor
        # parameter. The context manager calls Job.getOopsVars(); the data
        # returned by the latter method may be added to the OOPS report.

        class OopsMessageStorage:
            def __init__(self):
                self.data = None

            @contextlib.contextmanager
            def oopsMessage(self, data):
                self.data = data
                yield
                self.data = None

            def attachData(self, report, context):
                report['extra_data'] = self.data

        message_storage = OopsMessageStorage()
        self.oops_config.on_create.append(message_storage.attachData)
        job = FakeJob(1, Exception('This job is doomed'))
        runner = JobRunner(
            logger=self.logger, oops_config=self.oops_config,
            oopsMessage=message_storage.oopsMessage)
        report = runner.runJobHandleError(job)
        self.assertEqual({'foo': 'bar'}, report['extra_data'])

    def test_job_with_volatile_attributes(self):
        # Properties of jobs that are Storm objects may not be accessible
        # when a database transaction failed. In this case, even the
        # method Job.fail() may not be accessible. JobRUnner.run()
        # handles this by storing an early reference to job.fail().
        job = VolatileAttributesJob(1)
        self.runner.runJobHandleError(job)
        self.assertEqual(JobStatus.FAILED, job.status)

    def test_job_fails_in_complete(self):
        # If job.complete() fails, job.fail() is called.
        job = FakeJob(1, error_in_complete=True)
        self.runner.runJobHandleError(job)
        self.assertEqual(JobStatus.FAILED, job.status)

    def test_job_fails_in_suspend(self):
        # If job.suspend() fails, job.fail() is called.
        job = FakeJob(1, SuspendJobException, error_in_suspend=True)
        self.runner.runJobHandleError(job)
        self.assertEqual(JobStatus.FAILED, job.status)

    def test_job_fails_in_queue(self):
        # If job.queue() fails, job.fail() is called.
        class TryAgain(Exception):
            pass

        job = FakeJob(1, TryAgain('once more'), error_in_queue=True)
        job.retry_error_types = (TryAgain, )
        self.runner.runJobHandleError(job)
        self.assertEqual(JobStatus.FAILED, job.status)

    def test_runner_obeys_retry_error_types_method(self):

        class RetryAllRunner(JobRunner):

            def retryErrorTypes(self, job):
                return (Exception,)

        runner = RetryAllRunner(
            logger=self.logger, oops_config=self.oops_config)
        job = FakeJob(1, failure=Exception('Anything'))
        job.max_retries = 1
        runner.runJobHandleError(job)
        self.assertEqual(JobStatus.WAITING, job.status)
        self.assertEqual(1, job.attempt_count)

    def test_runner_obeys_user_error_types_method(self):

        class UserError(Exception):
            pass

        class UserErrorRunner(JobRunner):

            def userErrorTypes(self, job):
                return (UserError,)

        runner = UserErrorRunner(
            logger=self.logger, oops_config=self.oops_config)
        job = FakeJob(1, UserError('no OOPS expected'))
        self.assertFalse(job.notifyUserError_called)
        runner.runJobHandleError(job)
        self.assertEqual(0, self.oops_repository.oops_count)
        self.assertEqual(
            "<FakeJob> (ID 1) failed with user error "
            "UserError('no OOPS expected',).",
            self.log_handler.records[-1].msg)
        self.assertTrue(job.notifyUserError_called)
