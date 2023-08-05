# Copyright 2009 Canonical Ltd.  All rights reserved.
#
# This file is part of lazr.restful
#
# lazr.restful is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# lazr.restful is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with lazr.restful.  If not, see <http://www.gnu.org/licenses/>.
"Test harness for doctests."

# pylint: disable-msg=E0611,W0142

__metaclass__ = type
__all__ = [
    'additional_tests',
    ]

import atexit
import doctest
import os
from pkg_resources import (
    resource_filename, resource_exists, resource_listdir, cleanup_resources)
import unittest

from zope.testing.cleanup import cleanUp


DOCTEST_FLAGS = (
    doctest.ELLIPSIS |
    doctest.NORMALIZE_WHITESPACE |
    doctest.REPORT_NDIFF)


def tearDown(test):
    """Run registered clean-up function."""
    cleanUp()


def additional_tests():
    "Run the doc tests (README.txt and docs/*, if any exist)"
    doctest_files = [
        os.path.abspath(resource_filename('lazr.restful', 'README.txt'))]
    if resource_exists('lazr.restful', 'docs'):
        for name in resource_listdir('lazr.restful', 'docs'):
            if name.endswith('.txt'):
                doctest_files.append(
                    os.path.abspath(
                        resource_filename('lazr.restful', 'docs/%s' % name)))
    kwargs = dict(module_relative=False, optionflags=DOCTEST_FLAGS,
                  tearDown=tearDown)
    atexit.register(cleanup_resources)
    return unittest.TestSuite((
        doctest.DocFileSuite(*doctest_files, **kwargs)))
