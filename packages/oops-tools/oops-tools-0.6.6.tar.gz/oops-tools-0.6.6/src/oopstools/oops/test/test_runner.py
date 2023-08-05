# Copyright 2005-2011 Canonical Ltd.  All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import doctest
import imp
import os.path
import re
import unittest

from glob import glob
from os import path
from django.test.simple import DjangoTestSuiteRunner

DEFAULT_OPTIONS = (
    doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS |doctest.REPORT_NDIFF)

class CustomTestRunner(DjangoTestSuiteRunner):

    def __init__(self, verbosity=3, interactive=False, failfast=True):
        super(CustomTestRunner, self).__init__(verbosity=verbosity,
            interactive=interactive, failfast=failfast)

    def build_suite(self, test_labels, extra_tests=None, **kwargs):
        # XXX: matsubara 2010-02-19 bug 524440: Adding a sort here to
        # guarantee we'll have the doctests in the same order. Ideally tests
        # should be contained and not need to be run on a specific order.
        doctests = sorted(glob(path.join(path.dirname(__file__), '*.txt')))
        filtered_doctests = set([])
        for label in test_labels:
            # regular expression match.
            test_name = re.compile(label)
            filtered_doctests.update(filter(test_name.search, doctests))
        # XXX: According to Python Library Reference:
        # Changed in version 2.5: The global __file__ was added to the
        # globals provided to doctests loaded from a text file using
        # DocFileSuite(). This is a hack to make tests work on 2.4
        globs = {'__file__': __file__}
        filtered_doctests = sorted(list(filtered_doctests))
        suite = doctest.DocFileSuite(module_relative=False,
                                     optionflags=DEFAULT_OPTIONS, globs=globs,
                                     *filtered_doctests)

        # Add the unit tests as well.
        unittests = sorted(
            glob(path.join(path.dirname(__file__), 'test_*.py')))
        unittests = filter(lambda x: x != __file__, unittests)
        for test in unittests:
            mod_name, ext = os.path.splitext(os.path.basename(test))
            mod_data = imp.find_module(mod_name, [os.path.dirname(test)])
            test_module = imp.load_module(mod_name, *mod_data)
            suite.addTest(
                unittest.defaultTestLoader.loadTestsFromModule(test_module))
        return suite
