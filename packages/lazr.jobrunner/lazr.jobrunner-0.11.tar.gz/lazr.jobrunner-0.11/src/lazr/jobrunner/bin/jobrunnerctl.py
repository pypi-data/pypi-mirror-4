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


import os
import sys

from celery.bin.celeryd_multi import MultiTool


class JobRunnerCtl(MultiTool):

    def __init__(self, env=None):
        # MultiTool starts "/usr/bin/python -m celery.bin.celeryd_detach"
        # in order to start a celeryd instance, and celeryd_detach wants
        # to import for example celery.base. This fails if these modules
        # are located in eggs outside the default module path used by
        # /bin/python.
        extended_path = [name for name in sys.path if '/eggs' in name]

        this_path = os.path.split(__file__)[0]
        last_part = 'lazr/jobrunner/bin'
        this_path = this_path[:-len(last_part)]
        if this_path not in extended_path:
            extended_path.append(this_path)
        needed_env = dict(os.environ)
        needed_env['PYTHONPATH'] = ':'.join(extended_path)
        if env is not None:
            needed_env.update(env)
        super(JobRunnerCtl, self).__init__(env=needed_env)


def main():
    try:
        sys.exit(JobRunnerCtl().execute_from_commandline(sys.argv))
    except KeyboardInterrupt:
        sys.exit(1)
