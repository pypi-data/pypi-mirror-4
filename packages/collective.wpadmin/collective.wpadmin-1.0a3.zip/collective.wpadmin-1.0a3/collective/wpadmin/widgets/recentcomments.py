from collective.wpadmin.widgets import widget
from collective.wpadmin import i18n

_ = i18n.messageFactory


class RecentComments(widget.Widget):
    name = "recentcomments"
    title = _(u"Recent comments")
    content_template_name = "recentcomments.pt"

    def get_comments(self):
        query = self.get_query()
        query['portal_type'] = 'Discussion Item'

        brains = self.query_catalog(query)
        return brains
