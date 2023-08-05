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

import testtools

from zope.interface import Interface, implements
from zope.component import (
    provideUtility, queryUtility, getSiteManager, queryAdapter, adapts)
from zope.component.registry import Components

from zope_fixtures import (
    ComponentsFixture, UtilityFixture, AdapterFixture)


class ITestUtility(Interface):
    pass


class TestUtility(object):
    implements(ITestUtility)


class ITestContext(Interface):
    pass


class TestContext(object):
    implements(ITestContext)


class ITestAdapter(Interface):
    pass


class TestAdapter(object):
    implements(ITestAdapter)
    adapts(ITestContext)

    def __init__(self, context):
        self.context = context


class TestComponentsFixture(testtools.TestCase):

    def test_overlays_site_manager(self):
        # A custom site manager is installed.
        fixture = ComponentsFixture()
        original_registry = getSiteManager()
        self.useFixture(fixture)
        self.assertIs(fixture.registry, getSiteManager())
        self.assertIn(original_registry, fixture.registry.__bases__)

    def test_restores_site_manager(self):
        fixture = ComponentsFixture()
        original_registry = getSiteManager()
        with fixture:
            self.assertIs(fixture.registry, getSiteManager())
        self.assertIs(original_registry, getSiteManager())

    def test_provide_utility_against_fixture_registry(self):
        fixture = ComponentsFixture()
        original_registry = getSiteManager()
        self.useFixture(fixture)
        utility = TestUtility()
        fixture.registry.registerUtility(utility)
        self.assertIs(utility, queryUtility(ITestUtility))
        self.assertIs(utility, fixture.registry.queryUtility(ITestUtility))
        self.assertIs(None, original_registry.queryUtility(ITestUtility))

    def test_restores_original_registry(self):
        fixture = ComponentsFixture()
        original_registry = getSiteManager()
        original_utility = TestUtility()
        provideUtility(original_utility)
        self.addCleanup(original_registry.unregisterUtility, original_utility)
        with fixture:
            overridden_utility = TestUtility()
            fixture.registry.registerUtility(overridden_utility)
            self.assertIs(overridden_utility, queryUtility(ITestUtility))
        self.assertIs(original_utility, queryUtility(ITestUtility))

    def test_restores_original_implementation_hook(self):
        original = getSiteManager.original
        registry = Components()
        implementation = lambda context=None: registry
        getSiteManager.sethook(implementation)
        self.assertIs(registry, getSiteManager())
        with ComponentsFixture() as fixture:
            self.assertIs(fixture.registry, getSiteManager())
        self.assertIs(original, getSiteManager.original)
        self.assertIs(implementation, getSiteManager.implementation)
        self.assertIs(registry, getSiteManager())
        getSiteManager.reset()

    def test_use_alternate_bases(self):
        registry = Components()
        utility = TestUtility()
        registry.registerUtility(utility)
        self.useFixture(ComponentsFixture(bases=(registry,)))
        self.assertIs(utility, queryUtility(ITestUtility))


class TestUtilityFixture(testtools.TestCase):

    def test_provide_utility(self):
        utility = TestUtility()
        fixture = UtilityFixture(utility)
        self.useFixture(fixture)
        self.assertIs(utility, queryUtility(ITestUtility))

    def test_unregister_utility(self):
        utility = TestUtility()
        with UtilityFixture(utility):
            self.assertIs(utility, queryUtility(ITestUtility))
        self.assertIs(None, queryUtility(ITestUtility))

    def test_restore_original_utility(self):
        original = TestUtility()
        sm = getSiteManager()
        sm.registerUtility(original)
        self.addCleanup(sm.unregisterUtility, original)
        utility = TestUtility()
        with UtilityFixture(utility):
            self.assertIs(utility, queryUtility(ITestUtility))
        self.assertIs(original, queryUtility(ITestUtility))

    def test_arguments_passthrough(self):
        utility = TestUtility()
        fixture = UtilityFixture(utility, name="foo")
        self.useFixture(fixture)
        self.assertIs(utility, queryUtility(ITestUtility, name="foo"))


class TestAdapterFixture(testtools.TestCase):

    def test_provide_adapter(self):
        fixture = AdapterFixture(TestAdapter)
        self.useFixture(fixture)
        context = TestContext()
        adapter = queryAdapter(context)
        self.assertIs(context, adapter.context)

    def test_unregister_adapter(self):
        context = TestContext()
        with AdapterFixture(TestAdapter):
            adapter = queryAdapter(context)
            self.assertIs(context, adapter.context)
        self.assertIs(None, queryAdapter(context))

    def test_restore_original_adapter(self):

        class TestAdapter2(TestAdapter):
            pass

        sm = getSiteManager()
        sm.registerAdapter(TestAdapter2)
        self.addCleanup(sm.unregisterAdapter, TestAdapter2)
        context = TestContext()
        with AdapterFixture(TestAdapter):
            self.assertIsInstance(queryAdapter(context), TestAdapter)
        self.assertIsInstance(queryAdapter(context), TestAdapter2)

    def test_arguments_passthrough(self):
        fixture = AdapterFixture(TestAdapter, name="foo")
        self.useFixture(fixture)
        context = TestContext()
        self.assertIsInstance(queryAdapter(context, name="foo"), TestAdapter)
