import logging

from zope import component
from zope.schema.interfaces import IVocabularyFactory
from zope.publisher.interfaces.browser import IBrowserRequest
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.customerize import registration
from plone import api

from collective.wpadmin import i18n, settings
from collective.configviews import ConfigurableBaseView

logger = logging.getLogger('collective.wpadmin')
_ = i18n.messageFactory


class Core(ConfigurableBaseView):
    """Default implementation of IPage"""
    template_name = ""
    settings_schema = settings.WPAdminSettings

    def __init__(self, context, request):
        super(Core, self).__init__(context, request)
        self.cached_components = {}
        self.cached_tools = {}

    @property
    def index(self):
        return ViewPageTemplateFile('templates/%s' % self.template_name)

    def __call__(self):
        if self.context.portal_type not in ('Plone Site', 'Folder'):
            context_state = component.getMultiAdapter((self.context,
                                                       self.request),
                                                  name=u"plone_context_state")
            if context_state.is_default_page():
                url = self.context.aq_inner.aq_parent.absolute_url()
                self.request.response.redirect(url + '/@@' + self.__name__)
                return
        self.update()
        return self.index(self)

    def update(self):
        pass

    @property
    def site_url(self):
        pstate = self.get_portal_state()
        return pstate.navigation_root_url()

    def get_tool(self, tool_id):
        if tool_id not in self.cached_tools:
            tool = api.portal.get_tool(name=tool_id)
            self.cached_tools[tool_id] = tool
        return self.cached_tools[tool_id]

    def query_catalog(self, query):
        catalog = self.get_tool('portal_catalog')
        return catalog(**query)

    def get_query(self):
        query = {}
        query['path'] = '/'.join(self.context.getPhysicalPath())
        return query

    def get_vocabulary(self, name=""):
        cid = "vocabulary_%s" % name
        if cid not in self.cached_components:
            self.cached_components[cid] = component.queryUtility(
                                            IVocabularyFactory,
                                            name=name)
        return self.cached_components[cid]

    def get_portal_state(self):
        cid = "plone_portal_state"
        if cid not in self.cached_components:
            self.cached_components[cid] = component.getMultiAdapter(
                                            (self.context, self.request),
                                            name=cid)
        return self.cached_components[cid]

    def get_views(self, interface=None):
        views = []
        key = 'views'
        if key not in self.cached_components:
            #http://developer.plone.org/views/browserviews.html
            views = [view.factory for view in \
                     registration.getViews(IBrowserRequest)]
            self.cached_components[key] = views

        if interface is not None:
            key = key + '.' + interface.__module__ + '.' + interface.__name__
            if key not in self.cached_components:
                views = [view for view in views \
                         if interface.implementedBy(view)]
                self.cached_components[key] = views

        return self.cached_components[key]

    def get_messages(self):
        if 'statusmessage' not in self.cached_components:
            status = IStatusMessage(self.request)
            self.cached_components['statusmessage'] = status
        return self.cached_components['statusmessage'].show()

    def log(self, message, mtype="info"):
        log = getattr(logger, mtype)
        log(message)

    def get_add_blog_url(self):
        path = '/createObject?type_name=' + self.settings['blog_type']
        return self.context.absolute_url() + path
