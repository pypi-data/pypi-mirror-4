# Copyright 2009-2013 Canonical Ltd.  All rights reserved.
#
# This file is part of lazr.smtptest.
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

# This is a namespace package, however under >= Python 3.3, let it be a true
# namespace package (i.e. this cruft isn't necessary).
import sys

if sys.hexversion < 0x30300f0:
    try:
        import pkg_resources
        pkg_resources.declare_namespace(__name__)
    except ImportError:
        import pkgutil
        __path__ = pkgutil.extend_path(__path__, __name__)
