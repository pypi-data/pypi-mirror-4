from collective.wpadmin.pages.page import Page
from collective.wpadmin import i18n

_ = i18n.messageFactory


class Media(Page):
    """Media page"""
    id = "upload"
    title = _(u"Media")
    description = _(u"Manage your medias")
    icon = "icon-picture"

    content_template_name = "upload.pt"

    def get_all_media(self):
        query = self.get_query()
        media_types = [self.settings['image_type'],
                       self.settings['file_type']]
        query['portal_type'] = media_types
        return self.query_catalog(query)
