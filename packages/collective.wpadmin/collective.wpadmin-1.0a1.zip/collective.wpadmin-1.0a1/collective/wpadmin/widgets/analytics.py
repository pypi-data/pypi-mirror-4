from collective.wpadmin.widgets import widget
from collective.wpadmin import i18n

_ = i18n.messageFactory


class Analytics(widget.Widget):
    name = "analytics"
    title = _(u"Analytics")
    content_template_name = "analytics.pt"
