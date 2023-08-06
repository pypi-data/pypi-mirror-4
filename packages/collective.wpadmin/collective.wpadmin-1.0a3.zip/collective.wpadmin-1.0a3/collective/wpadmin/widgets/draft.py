from zope import component
from plone import api
from plone.registry.interfaces import IRegistry

from collective.wpadmin.widgets import widget
from collective.wpadmin import i18n

_ = i18n.messageFactory


class Draft(widget.Widget):
    name = "draft"
    title = _(u"Draft")
    content_template_name = "draft.pt"

    def get_drafts(self):
        registry = component.getUtility(IRegistry)
        key = 'collective.wpadmin.settings.WPAdminSettings.blog_type'
        post_type = registry.get(key, 'News Item')
        query = self.get_query()
        query['review_state'] = 'private'
        query['Creator'] = api.user.get_current().getId()
        query['portal_type'] = post_type
        brains = self.query_catalog(query)
        return brains
