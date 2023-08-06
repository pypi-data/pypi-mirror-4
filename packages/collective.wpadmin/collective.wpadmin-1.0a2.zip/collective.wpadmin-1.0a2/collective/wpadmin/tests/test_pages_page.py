import unittest2 as unittest
from collective.wpadmin.tests import base, utils
from ZPublisher.tests.testPublish import Request
from collective.wpadmin.pages import page


class UnitTestPage(base.UnitTestCase):
    """We tests the setup (install) of the addons. You should check all
    stuff in profile are well activated (browserlayer, js, content types, ...)
    """

    def setUp(self):
        super(UnitTestPage, self).setUp()
        self.context = utils.FakeContext()
        self.request = Request()
        self.view = page.Page(self.context, self.request)

    def test_main_title(self):
        self.assertEqual(self.view.main_title(), 'a title')

    def test_get_url(self):
        url = "http://nohost.com/myid/wp-admin-page"
        self.assertEqual(self.view.get_url(), url)

    def test_ipage(self):
        self.assertEqual(self.view.id, 'page')
        self.assertEqual(self.view.description, u'')
        self.assertEqual(self.view.title, u'Default page')


class IntegrationTestPage(base.IntegrationTestCase):
    def setUp(self):
        super(IntegrationTestPage, self).setUp()
        self.view = page.Page(self.folder, self.request)

    def test_get_menu(self):
        menu = self.view.get_menu()
        for item in menu:
            self.assertIn('id', item)
            self.assertIn('title', item)
            self.assertIn('icon', item)
        menu_ids = [item['id'] for item in menu]
        self.assertIn('edit', menu_ids)
        self.assertIn('upload', menu_ids)
        self.assertIn('dashboard', menu_ids)


class UnitTestWidgetContainer(base.UnitTestCase):
    def setUp(self):
        self.context = utils.FakeContext()
        self.request = Request()
        self.view = page.WidgetsContainer(self.context, self.request)

    def test_sort_widgets(self):
        self.view.left_widget_ids = ['first', 'second']
        self.view.right_widget_ids = []
        self.view.all_widgets = {'first': 'my-first-widget',
                                 'second': 'my-second-widget',
                                 'notpositioned': 'shouldnotbe'}
        self.assertTrue(not self.view.left_widgets)
        self.assertTrue(not self.view.right_widgets)
        self.view._sort_widgets()
        self.assertIn('my-first-widget', self.view.left_widgets)
        self.assertIn('my-second-widget', self.view.left_widgets)
        self.assertNotIn('notpositioned', self.view.left_widgets)
        self.assertTrue(not self.view.right_widgets)
        self.assertEqual(self.view.left_widgets, ['my-first-widget',
                                                  'my-second-widget'])


class IntegrationTestWidgetContainer(base.IntegrationTestCase):
    def setUp(self):
        super(IntegrationTestWidgetContainer, self).setUp()
        self.view = page.WidgetsContainer(self.folder, self.request)
        self.view.left_widget_ids = ["summary", "draft", "recentcomments"]
        #patch to not achieve rendering of contents
        self.view.content_template_name = False

    def test_update(self):
        self.assertFalse(self.view.all_widgets)  # empty
        self.view.update()
        self.assertTrue(self.view.all_widgets)
        self.assertEqual(len(self.view.left_widgets), 3)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
