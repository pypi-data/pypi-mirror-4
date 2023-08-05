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

__all__ = [
    'ComponentsFixture',
    'UtilityFixture',
    'AdapterFixture',
    ]

from fixtures import Fixture
from testtools.helpers import try_import

Components = try_import("zope.component.registry.Components")
getSiteManager = try_import("zope.component.getSiteManager")
_getUtilityProvided = try_import("zope.component.registry._getUtilityProvided")
_getAdapterProvided = try_import("zope.component.registry._getAdapterProvided")
_getAdapterRequired = try_import("zope.component.registry._getAdapterRequired")


class ComponentsFixture(Fixture):
    """Overlay the global Zope registry so that tests don't change it.

    :ivar registry: An alternate Zope registry that can be used to override
        registrations in the original registry. This isn't normally needed:
        once setUp you can access the registry by calling getSiteManager()
        as normal.

    Example::

        class TestSomething(TestCase):

            def test_registry(self):
                self.useFixture(ComponentsFixture())
                getSiteManager().registerUtility(...)
                # more code here
    """

    def __init__(self, bases=None):
        """Initialize the fixture.

        :param bases: The registries that should be used as bases for the
            fixture's registry. The default is to base on the current
            global site manager, as returned by getSiteManager().
        """
        super(ComponentsFixture, self).__init__()
        if bases is None:
            bases = (getSiteManager(),)
        self._bases = bases

    def setUp(self):
        super(ComponentsFixture, self).setUp()
        self.registry = Components(bases=self._bases)
        if getSiteManager.implementation is not getSiteManager.original:
            self.addCleanup(getSiteManager.sethook, getSiteManager.implementation)
        getSiteManager.sethook(lambda context=None: self.registry)
        self.addCleanup(getSiteManager.reset)


class UtilityFixture(Fixture):
    """Fixture for registering or overriding a single utility.

    The utility will be unregistered upon cleanUp, or the original utility
    will be restored if there was one.

    The registration is performed agaist the current site manager.
    """

    def __init__(self, component, provided=None, name=u""):
        """Create an UtilityFixture.

        The parameters are the same supported by registerUtility and will
        be passed to it.
        """
        super(UtilityFixture, self).__init__()
        self._component = component
        self._provided = provided or _getUtilityProvided(component)
        self._name = name

    def setUp(self):
        super(UtilityFixture, self).setUp()
        # We use the current site manager so we honor whatever hooks have
        # been set
        sm = getSiteManager()

        # Check if an utility for the same interface and name exists, if so
        # restore it upon cleanup, otherwise just unregister our one.
        original = sm.queryUtility(self._provided, self._name)
        if original is not None:
            self.addCleanup(sm.registerUtility, original, self._provided,
                            self._name)
        else:
            self.addCleanup(sm.unregisterUtility, self._component,
                            self._provided, self._name)

        # Register the utility
        sm.registerUtility(self._component, self._provided, self._name)


class AdapterFixture(Fixture):
    """Fixture for registering or overriding a single adapter.

    The adapter will be unregistered upon cleanUp, or the original adapter
    will be restored if there was one.

    The registration is performed agaist the current site manager.
    """

    def __init__(self, factory, required=None, provided=None, name=u""):
        """Create an AdapterFixture.

        The parameters are the same supported by registerAdpater and will
        be passed to it.
        """
        super(AdapterFixture, self).__init__()
        self._factory = factory
        self._required = _getAdapterRequired(factory, required)
        self._provided = provided or _getAdapterProvided(factory)
        self._name = name

    def setUp(self):
        super(AdapterFixture, self).setUp()
        # We use the current site manager so we honor whatever hooks have
        # been set
        sm = getSiteManager()

        # Check if an utility for the same interface and name exists, if so
        # restore it upon cleanup, otherwise just unregister our one.
        original = sm.adapters.registered(self._required, self._provided,
                                          self._name)
        if original is not None:
            self.addCleanup(sm.registerAdapter, original, self._required,
                            self._provided, self._name)
        else:
            self.addCleanup(sm.unregisterAdapter, self._factory, self._required,
                            self._provided, self._name)

        # Register the utility
        sm.registerAdapter(self._factory, self._required, self._provided,
                           self._name)
