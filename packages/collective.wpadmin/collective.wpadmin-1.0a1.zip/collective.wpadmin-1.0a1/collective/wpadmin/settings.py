from zope import interface
from zope import schema

from collective.wpadmin import i18n

_ = i18n.messageFactory


class WPAdminSettings(interface.Interface):
    """global settings"""

    blog_type = schema.ASCIILine(title=_(u"Blog content type"),
                                 default="News Item")
    image_type = schema.ASCIILine(title=_(u"Image content type"),
                                 default="Image")
    file_type = schema.ASCIILine(title=_(u"File content type"),
                                 default="File")
