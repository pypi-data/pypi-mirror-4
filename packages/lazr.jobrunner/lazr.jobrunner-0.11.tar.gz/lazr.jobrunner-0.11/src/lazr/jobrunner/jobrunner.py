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


from celery.exceptions import SoftTimeLimitExceeded
from contextlib import contextmanager
import logging
from resource import (
    getrlimit,
    RLIMIT_AS,
    setrlimit,
    )
import sys


class SuspendJobException(Exception):
    """Raised when a running job wants to suspend itself."""
    pass


class LeaseHeld(Exception):
    """Raised when attempting to acquire a lease that is already held."""

    def __init__(self):
        Exception.__init__(self, 'Lease is already held.')


class JobStatus:

    class COMPLETED:
        title = 'completed'
        value = 1

    class WAITING:
        title = 'waiting'
        value = 2

    class RUNNING:
        title = "running"
        value = 3

    class FAILED:
        title = "failed"
        value = 4

    class SUSPENDED:
        title = "suspended"
        value = 5

    by_value = dict(
        (cls.value, cls) for cls in [COMPLETED, WAITING, RUNNING,
        FAILED, SUSPENDED])


@contextmanager
def memory_limit(limit):
    if limit is not None:
        orig_soft_limit, hard_limit = getrlimit(RLIMIT_AS)
        setrlimit(RLIMIT_AS, (limit, hard_limit))
    try:
        yield
    finally:
        if limit is not None:
            setrlimit(RLIMIT_AS, (orig_soft_limit, hard_limit))


class NoJobSource(Exception):
    def __init__(self):
        Exception.__init__(self, 'No job source set up.')


class BaseJob:

    retry_error_types = ()
    user_error_types = ()
    max_retries = 0

    def __init__(self, job_id):
        self.job_id = job_id
        self.status = JobStatus.WAITING
        self.attempt_count = 0

    def run(self):
        raise NotImplementedError

    def start(self, manage_transaction=False):
        self.status = JobStatus.RUNNING
        self.attempt_count += 1

    def fail(self, manage_transaction=False):
        self.status = JobStatus.FAILED

    def complete(self, manage_transaction=False):
        self.status = JobStatus.COMPLETED

    def suspend(self, manage_transaction=False):
        self.status = JobStatus.SUSPENDED

    def makeOopsReport(self, oops_config, info):
        """Generate an OOPS report using the given OOPS configuration."""
        return oops_config.create(context=dict(exc_info=info))

    def notifyOops(self, oops_report):
        """Send notifications about an OOPS."""
        raise NotImplementedError

    def notifyUserError(self, exception):
        """Send notifications about a user error."""
        raise NotImplementedError

    def queue(self, manage_transaction=False, abort_transaction=False):
        self.status = JobStatus.WAITING

    def getOopsVars(self):
        return ()

    def __repr__(self):
        return '<%s>' % self.__class__.__name__


class JobRunner:

    def __init__(self, logger=None, oops_config=None, oopsMessage=None):
        # TODO Job source should be responsible for providing valid jobs.
        self.completed_jobs = []
        self.incomplete_jobs = []
        if logger is None:
            logger = logging.getLogger()
        self.logger = logger
        self.oops_config = oops_config
        if oopsMessage is not None:
            self.oopsMessage = oopsMessage

    @staticmethod
    def job_str(job):
        return '%r (ID %d)' % (job, job.job_id)

    def runJob(self, job, fallback=None):
        """Attempt to run a job, updating its status as appropriate."""
        self.logger.info(
            'Running %s in status %s' % (
                self.job_str(job), job.status.title))
        fail = job.fail
        job.start(manage_transaction=True)
        try:
            try:
                job.run()
            except self.retryErrorTypes(job), e:
                if job.attempt_count > job.max_retries:
                    raise
                self.logger.warning(
                    "Scheduling retry due to %s: %s." % (
                        e.__class__.__name__, e))
                job.queue(manage_transaction=True)
                self.incomplete_jobs.append(job)
            except SuspendJobException:
                self.logger.debug("Job suspended itself")
                job.suspend(manage_transaction=True)
                self.incomplete_jobs.append(job)
            except SoftTimeLimitExceeded:
                if fallback is not None:
                    job.queue(manage_transaction=True, abort_transaction=True)
                    fallback()
                else:
                    raise
            else:
                job.complete(manage_transaction=True)
                self.completed_jobs.append(job)
        except Exception:
            fail(manage_transaction=True)
            self.incomplete_jobs.append(job)
            raise

    def runJobHandleError(self, job, fallback=None):
        """Run the specified job, handling errors."""
        with self.oopsMessage(dict(job.getOopsVars())):
            try:
                try:
                    self.runJob(job, fallback)
                except self.userErrorTypes(job), e:
                    self.logger.info(
                        '%s failed with user error %r.'
                        % (self.job_str(job), e))
                    job.notifyUserError(e)
                except Exception:
                    info = sys.exc_info()
                    return self._doOops(job, info)
            except Exception, e:
                # This only happens if _doOops() fails.
                self.logger.exception("Failure in _doOops: %s" % e)
                info = sys.exc_info()
                report = job.makeOopsReport(self.oops_config, info)
                self.oops_config.publish(report)
                return report

    def retryErrorTypes(self, job):
        return job.retry_error_types

    def userErrorTypes(self, job):
        return job.user_error_types

    @staticmethod
    @contextmanager
    def oopsMessage(message):
        """Add an oops message to be included in oopses from this context."""
        yield

    def _doOops(self, job, info):
        """Report an OOPS for the provided job and info.

        :param job: The IRunnableJob whose run failed.
        :param info: The standard sys.exc_info() value.
        :return: the Oops that was reported.
        """
        if self.oops_config is not None:
            report = job.makeOopsReport(self.oops_config, info)
            oops_ids = self.oops_config.publish(report)
            self.logger.error(
                'OOPS while executing job %s: %s %r' % (
                    job.job_id, oops_ids, info[1]))
            job.notifyOops(report)
            return report
        return None
