#  zope_fixtures: Zope fixtures with cleanups for testing and convenience.
#
# Copyright (c) 2011, Robert Collins <robertc@robertcollins.net>
# 
# Licensed under either the Apache License, Version 2.0 or the BSD 3-clause
# license at the users choice. A copy of both licenses are available in the
# project source as Apache-2.0 and BSD. You may not use this file except in
# compliance with one of these two licences.
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under these licenses is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# license you chose for the specific language governing permissions and
# limitations under that license.

import doctest
import sys
import unittest


def test_suite():
    result = unittest.TestSuite()
    standard_tests = unittest.TestSuite()
    loader = unittest.TestLoader()
    return load_tests(loader, standard_tests, None)


def load_tests(loader, standard_tests, pattern):
    test_modules = [
        'components',
        ]
    prefix = "zope_fixtures.tests.test_"
    test_mod_names = [prefix + test_module for test_module in test_modules]
    standard_tests.addTests(loader.loadTestsFromNames(test_mod_names))
    doctest.set_unittest_reportflags(doctest.REPORT_ONLY_FIRST_FAILURE)
    standard_tests.addTest(doctest.DocFileSuite("../../../README"))
    return standard_tests
