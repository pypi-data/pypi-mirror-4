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

from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()


version = '0.11'

install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
    'celery',
]


setup(
    name='lazr.jobrunner',
    version=version,
    description="A Celery based job runner",
    long_description=README + '\n\n' + NEWS,
    classifiers=[
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    keywords='',
    author='Launchpad Developers',
    author_email='launchpad-dev@lists.launchpad.net',
    url='https://launchpad.net/lazr.jobrunner',
    license='GPL v3',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages = ['lazr'],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'jobrunnerctl=lazr.jobrunner.bin.jobrunnerctl:main',
            'clear-queues=lazr.jobrunner.bin.clear_queues:main'
            ]
    },
    test_suite="lazr.jobrunner",
)
