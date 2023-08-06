from collective.wpadmin.widgets import widget
from collective.wpadmin.pages.page import PloneActionModal
from collective.wpadmin import i18n

_ = i18n.messageFactory


class Addbox(widget.Widget):
    name = "addbox"
    title = _(u"Add box")
    content_template_name = "addbox.pt"

    def quickupload_url(self):
        return '%s/media/@@quick_upload' % self.context.absolute_url()

    def get_content_types(self):
        content_types = []
        name = "plone.app.vocabularies.ReallyUserFriendlyTypes"
        vocab_factory = self.get_vocabulary(name)
        vocab = vocab_factory(self.context)
        for term in vocab:
            content_types.append({'title': term.title,
                                  'id': term.token})
        return content_types


class AddModal(PloneActionModal):
    action = "folder_factories"
