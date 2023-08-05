# Copyright 2009-2013 Canonical Ltd.  All rights reserved.
#
# This file is part of lazr.smtptest
#
# lazr.smtptest is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# lazr.smtptest is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with lazr.smtptest.  If not, see <http://www.gnu.org/licenses/>.

import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup, find_packages

__version__ = open('lazr/smtptest/version.txt').read().strip()

setup(
    name='lazr.smtptest',
    version=__version__,
    namespace_packages=['lazr'],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    maintainer='LAZR Developers',
    maintainer_email='lazr-developers@lists.launchpad.net',
    description='A test framework for SMTP based applications',
    long_description="""
This is LAZR smtptest, a framework for testing SMTP-based applications and
libraries.  It provides a real, live SMTP server that you can send messages
to, and from which you can read those test messages.  This can be used to
ensure proper operation of your applications which send email.
""",
    license='LGPL v3',
    install_requires=[
        'setuptools',
        'zope.interface',
        ],
    url='https://launchpad.net/lazr.smtptest',
    download_url= 'https://launchpad.net/lazr.smtptest/+download',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        ],
    test_suite='nose.collector',
    )
