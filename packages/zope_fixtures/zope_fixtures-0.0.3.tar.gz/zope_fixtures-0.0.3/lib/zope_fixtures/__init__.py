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


"""Zope Fixtures provide test support for zope environments.

See the README for a manual, and the docstrings on individual functions and
methods for details.
"""

# same format as sys.version_info: "A tuple containing the five components of
# the version number: major, minor, micro, releaselevel, and serial. All
# values except releaselevel are integers; the release level is 'alpha',
# 'beta', 'candidate', or 'final'. The version_info value corresponding to the
# Python version 2.0 is (2, 0, 0, 'final', 0)."  Additionally we use a
# releaselevel of 'dev' for unreleased under-development code.
#
# If the releaselevel is 'alpha' then the major/minor/micro components are not
# established at this point, and setup.py will use a version of next-$(revno).
# If the releaselevel is 'final', then the tarball will be major.minor.micro.
# Otherwise it is major.minor.micro~$(revno).
__version__ = (0, 0, 3, 'final', 0)

__all__ = [
    'AdapterFixture',
    'ComponentsFixture',
    'UtilityFixture',
    ]

from zope_fixtures.components import (
    AdapterFixture,
    ComponentsFixture,
    UtilityFixture,
    )


def test_suite():
    import unittest
    import zope_fixtures.tests
    return zope_fixtures.tests.test_suite()


def load_tests(loader, standard_tests, pattern):
    standard_tests.addTests(loader.loadTestsFromNames(["zope_fixtures.tests"]))
    return standard_tests
