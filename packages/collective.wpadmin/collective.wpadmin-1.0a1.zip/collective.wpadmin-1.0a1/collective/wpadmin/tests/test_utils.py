import unittest2 as unittest
from collective.wpadmin.tests import base, utils
from ZPublisher.tests.testPublish import Request
from collective.wpadmin.utils import Core
from collective.wpadmin.pages.page import IPage


class UnitTestCoreView(base.UnitTestCase):
    """We tests the setup (install) of the addons. You should check all
    stuff in profile are well activated (browserlayer, js, content types, ...)
    """

    def setUp(self):
        super(UnitTestCoreView, self).setUp()
        self.context = utils.FakeContext()
        self.request = Request()
        self.view = Core(self.context, self.request)

    def test_cached_tools(self):
        self.view.cached_tools['portal_catalog'] = 'catalog'
        self.assertEqual(self.view.get_tool('portal_catalog'), 'catalog')

    def test_cached_components(self):
        self.view.cached_components['views'] = 'my component'
        self.assertEqual(self.view.get_views(), 'my component')

        key = 'views.collective.wpadmin.pages.page.IPage'
        self.view.cached_components[key] = 'my views'
        self.assertEqual(self.view.get_views(interface=IPage), 'my views')

        self.view.cached_components['vocabulary_me'] = 'vocab'
        self.assertEqual(self.view.get_vocabulary(name='me'), 'vocab')

        self.view.cached_components['plone_portal_state'] = 'pstate'
        self.assertEqual(self.view.get_portal_state(), 'pstate')

        status = utils.FakeStatusMessage(self.request)
        status.add("message")
        self.view.cached_components['statusmessage'] = status
        self.assertEqual(self.view.get_messages(), ['<p>message</p>'])

    def test_query_catalog(self):
        query = self.view.get_query()
        self.view.cached_tools['portal_catalog'] = utils.FakeCatalog()
        res = self.view.query_catalog(query)
        self.assertEqual(len(res), 2)


class IntegrationTestCoreView(base.IntegrationTestCase):
    def setUp(self):
        super(IntegrationTestCoreView, self).setUp()
        self.setRole('Manager')
        self.view = self.folder.restrictedTraverse('wp-admin-dashboard')

    def test_cached_components(self):
        computed = self.view.get_views()
        cached = self.view.cached_components['views']
        self.assertEqual(computed, cached)

        computed = self.view.get_portal_state()
        cached = self.view.cached_components['plone_portal_state']
        self.assertEqual(computed, cached)

        name = "plone.app.vocabularies.ReallyUserFriendlyTypes"
        computed = self.view.get_vocabulary(name)
        cached = self.view.cached_components['vocabulary_%s' % name]
        self.assertEqual(computed, cached)

    def test_cached_tools(self):
        computed = self.view.get_tool('portal_catalog')
        cached = self.view.cached_tools['portal_catalog']
        self.assertEqual(computed, cached)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
