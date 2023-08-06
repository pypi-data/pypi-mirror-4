# Copyright (c) 2012, Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# GNU Lesser General Public License version 3 (see the file LICENSE).

import os

from setuptools import setup, find_packages

setup(
    name='oops_dictconfig',
    version='0.0.3',
    packages=find_packages(),
    include_package_data=True,
    maintainer='Launchpad developers',
    maintainer_email='launchpad-devs@lists.launchpad.net',
    description='Create an oops Config from a definition encoded as a dict',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README')).read(),
    license='LGPLv3',
    url='http://launchpad.net/python-oops-dictconfig',
    download_url='https://launchpad.net/python-oops-dictconfig/+download',
    test_suite='oops_dictconfig.tests',
    install_requires = [
        'oops',
        ],
    tests_require = [
        'oops_amqp',
        'oops_datedir_repo',
        'testtools'
        ],
    extras_require=dict(
        amqp=['oops_amqp'],
        datedir=['oops_datedir_repo'],
        configglue=['configglue'],
        ),
    # Auto-conversion to Python 3.
    use_2to3=True,
    )
