from collective.wpadmin.pages.page import Page
from collective.wpadmin import i18n

_ = i18n.messageFactory


class Tags(Page):
    """edit-tags page"""
    id = "edit-tags"
    title = _(u"Tags")
    description = _(u"Manage your tags")

    content_template_name = "edittags.pt"
