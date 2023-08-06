from collective.wpadmin.pages.page import WidgetsContainer
from collective.wpadmin import i18n

_ = i18n.messageFactory


class Dashboard(WidgetsContainer):
    """Dashboard page"""
    id = "dashboard"
    title = _(u"Dashboard")
    description = _(u"Get all you need")
    icon = "icon-th-large"

    left_widget_ids = ["summary", "draft", "recentcomments"]
    right_widget_ids = ["quickpress", "addbox"]
