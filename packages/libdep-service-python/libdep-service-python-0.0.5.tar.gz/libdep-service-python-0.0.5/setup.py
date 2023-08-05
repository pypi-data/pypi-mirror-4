# Copyright (C) 2012  Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import distribute_setup
# What is specified here is the minimum version, and the version
# that will be installed if there isn't one already. We specify
# it so that we can update distribute_setup without it implying
# that we require the latest version, which can cause unnecessary
# updating, and can fail if there is a version conflict.
# If we do require a higher minimum version then update it here
# and ensure that distribute_setup is at least as new as that
# version.
distribute_setup.use_setuptools(version='0.6.10')

from setup_helpers import get_version
from setuptools import setup, find_packages


__version__ = get_version('libdep_service_client/__init__.py')


setup(
    name="libdep-service-python",
    version=__version__,
    author="Canonical Consumer Applications",
    author_email="canonical-consumer-applications@lists.launchpad.net",
    include_package_data=True,
    license="GPL3",
    url='https://launchpad.net/libdep-service-python/',
    install_requires=[
        ],
    scripts=[
        ],
    zip_safe=False,
    extras_require = {
        'testing': [
            'libdep-service[testing]',
            'pathod',
            'testtools',
            ],
        },
    packages=find_packages('.'),
)
