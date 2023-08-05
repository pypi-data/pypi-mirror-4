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

"The lazr.smtptest package."

import pkg_resources
__version__ = pkg_resources.resource_string(
    "lazr.smtptest", "version.txt").strip()

import sys
if sys.version_info[0] == 3:
    __version__ = __version__.decode('utf-8')
