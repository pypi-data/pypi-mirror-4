from collective.wpadmin.widgets import widget
from collective.wpadmin import i18n
from plone import api

_ = i18n.messageFactory


class Draft(widget.Widget):
    name = "draft"
    title = _(u"Draft")
    content_template_name = "draft.pt"

    def get_drafts(self):
        query = self.get_query()
        query['review_state'] = 'private'

        query['Creator'] = api.user.get_current().getId()
        brains = self.query_catalog(query)
        return brains
