from collective.wpadmin.pages.page import Page
from collective.wpadmin import i18n

_ = i18n.messageFactory


class Comments(Page):
    """Dashboard page"""
    id = "edit-comments"
    title = _(u"Comments")
    description = _(u"Manage your comments")

    content_template_name = "editcomments.pt"
