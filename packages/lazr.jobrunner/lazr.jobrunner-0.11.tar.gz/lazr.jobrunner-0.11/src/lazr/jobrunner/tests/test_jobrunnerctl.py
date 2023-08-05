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


from datetime import (
    datetime,
    timedelta,
    )
import os
from time import sleep
from unittest import TestCase

from celery.bin.celeryd_multi import NamespacedOptionParser
from lazr.jobrunner.bin.jobrunnerctl import JobRunnerCtl
from lazr.jobrunner.tests.test_celerytask import (
    FileJob,
    FileJobSource,
    RunFileJob,
    tempdir,
    )


class TestJobRunnerCtl(TestCase):
    """Tests for jobrunnerctl script."""

    def getController(self, config, file_job_dir=None):
        if file_job_dir is not None:
            env = dict(os.environ)
            env['FILE_JOB_DIR'] = file_job_dir
        else:
            env = None
        controller = JobRunnerCtl(env=env)
        # JobRunnerCtl instances are supposed to be used via
        # their method execute_via_commandline(); this method defines
        # some properties that are needed when other JobRUnnerCtl
        # methods are called in the tests below.
        controller.nosplash = True
        controller.quiet = True
        controller.verbose = False
        controller.FAILED = 'FAILED'
        controller.OK = 'OK'
        controller.DOWN = 'DOWN'
        return controller

    def makeJob(self, job_source, job_id, eta=None):
        job = FileJob(job_source, job_id, sleep=3)
        job.save()
        return RunFileJob.apply_async(args=(job_id, ), eta=eta)

    def test_JobRunnerCtl_starts_stops_celeryd(self):
        with tempdir() as temp_dir:
            config = 'lazr.jobrunner.tests.config_no_prefetch'
            control = self.getController(config, temp_dir)
            argv = [
                '--config=%s' % config, 'node_name', '-Q:node_name', 'celery',
                ]
            parser = NamespacedOptionParser(argv)
            # We may have a stale PID file.
            old_pids = [info[2] for info in control.getpids(parser, 'celeryd')]
            control.start(argv, 'celeryd')
            sleep(1)
            current_pids = [
                info[2] for info in control.getpids(parser, 'celeryd')]
            self.assertTrue(len(current_pids) > 0)
            self.assertNotEqual(old_pids, current_pids)
            for pid in current_pids:
                self.assertTrue(control.node_alive(pid))
            control.kill(argv, 'celeryd')
            sleep(1)
            for pid in current_pids:
                self.assertFalse(control.node_alive(pid))

    def test_JobRunnerCtl_kill_does_not_lose_jobs(self):
        # If a celeryd instance is killed while it executes a task
        # and if a new instance is started, the new instance executes
        # the aborted job again. Note that this behaviour requires late
        # acknowledgement of AMQP messages, as specified in
        # tests/config_no_prefetch.py.
        with tempdir() as temp_dir:
            job_source = FileJobSource(temp_dir)
            all_jobs = [self.makeJob(job_source, id) for id in range(3)]
            config = 'lazr.jobrunner.tests.config_no_prefetch'
            control = self.getController(config, temp_dir)
            argv = [
                '--config=%s' % config, 'node_name', '-Q:node_name', 'celery',
                '-c:node_name', '1',
                ]
            control.start(argv, 'celeryd')
            control.kill(argv, 'celeryd')
            sleep(1)
            control.start(argv, 'celeryd')
            for job in all_jobs:
                job.wait(10)
            control.kill(argv, 'celeryd')

    def test_JobRunnerCtl_kill_does_not_lose_jobs_with_eta(self):
        with tempdir() as temp_dir:
            job_source = FileJobSource(temp_dir)
            eta = datetime.now() + timedelta(seconds=3)
            all_jobs = [self.makeJob(job_source, job_id=0, eta=eta)]
            all_jobs.extend(
                self.makeJob(job_source, job_id) for job_id in range(1, 3))
            config = 'lazr.jobrunner.tests.config_no_prefetch'
            control = self.getController(config, temp_dir)
            argv = [
                '--config=%s' % config, 'node_name', '-Q:node_name', 'celery',
                '-c:node_name', '1',
                ]
            control.start(argv, 'celeryd')
            sleep(1)
            control.kill(argv, 'celeryd')
            sleep(1)
            control.start(argv, 'celeryd')
            for job in all_jobs:
                job.wait(10)
            control.kill(argv, 'celeryd')
