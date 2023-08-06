from Acquisition import aq_inner
from zope import component
from zope import interface
from zope import schema
from z3c.form import form, button
from z3c.form.interfaces import ISubForm, IFormLayer
from Products.Archetypes.interfaces.base import IBaseContent
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from plone import api
from plone.autoform.form import AutoExtensibleForm
from plone.autoform.interfaces import WIDGETS_KEY
from plone.namedfile.field import NamedBlobImage
from plone.z3cform.interfaces import IWrappedForm
from plone.z3cform import z2

from collective.wpadmin.pages.page import Page, PloneActionModal
from collective.wpadmin import i18n
from Products.ATContentTypes.interfaces.image import IATImage
from Products.ATContentTypes.interfaces.news import IATNewsItem

_ = i18n.messageFactory


class Posts(Page):
    """Dashboard page"""
    id = "edit"
    title = _(u"Posts")
    description = _(u"Manage your posts")
    icon = "icon-folder-open"

    content_template_name = "edit.pt"

    def get_all_posts(self):
        query = self.get_query()
        query['portal_type'] = self.settings['blog_type']
        return self.query_catalog(query)


class WPDeleteForm(AutoExtensibleForm, form.Form):
    """delete confirmation form"""
    schema = interface.Interface

    @button.buttonAndHandler(_(u"delete"))
    def action_delete(self, action):
        self.next_url()
        self.delete_item()

    @button.buttonAndHandler(_(u"cancel"))
    def action_cancel(self, action):
        self.next_url()

    def delete_item(self):
        """Delete the context and add a message"""
        api.content.delete(self.context)
        msg = "%s has been deleted" % self.context.Title()
        IStatusMessage(self.request).add(msg, "info")

    def next_url(self):
        url = self.request['HTTP_REFERER']
        self.request.response.redirect(url)


class WPDeleteFormView(BrowserView):
    form = WPDeleteForm
    request_layer = IFormLayer
    index = ViewPageTemplateFile('../templates/wpform.pt')
    description = u"If you validate it will be deleted"

    @property
    def title(self):
        return u"Delete %s" % self.context.Title()

    def __init__(self, context, request):
        super(WPDeleteFormView, self).__init__(context, request)
        if self.form is not None:
            self.form_instance = self.form(
                aq_inner(self.context), self.request)
            self.form_instance.__name__ = self.__name__

    def update(self):
        if not ISubForm.providedBy(self.form_instance):
            interface.alsoProvides(self.form_instance, IWrappedForm)

        # If a form action redirected, don't render the wrapped form
        if self.request.response.getStatus() in (302, 303):
            self.contents = ""
            return

        z2.switch_on(self, request_layer=self.request_layer)
        self.form_instance.update()

    def __call__(self):
        self.update()
        return self.index()


class RenameFormSchema(interface.Interface):
    name = schema.ASCIILine(title=_(u"New ID"),
                            description=_(u"ID is the URL chunk"))
    title = schema.TextLine(title=_(u"New title"))


class RenameFormAdapter(object):
    interface.implements(RenameFormSchema)
    component.adapts(IBaseContent)

    def __init__(self, context):
        self.context = context

    @property
    def name(self):
        return self.context.getId()

    @property
    def title(self):
        return self.context.Title().decode('utf-8')


class RenameForm(AutoExtensibleForm, form.Form):
    schema = RenameFormSchema

    @button.buttonAndHandler(_(u"Rename"))
    def action_rename(self, action):
        self.next_url()
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            for error in errors:
                IStatusMessage(self.request).add(error.message, "error")
            return False
        self.do_rename(data)

    def do_rename(self, data):
        if self.context.getId() != data['name']:
            api.content.rename(obj=self.context,
                               new_id=data['name'],
                               safe_id=True)
        title = data['title'].encode('utf-8')
        if self.context.Title() != title:
            self.context.setTitle(title)

    def next_url(self):
        url = self.request['HTTP_REFERER']
        self.request.response.redirect(url)


class RenameFormView(WPDeleteFormView):
    form = RenameForm
    description = u""

    @property
    def title(self):
        return u"Rename %s" % self.context.Title()


from plone.autoform import directives
from plone.supermodel import model
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
#wysiwyg_widget = "plone.app.z3cform.wysiwyg.widget.WysiwygWidget"


class NewsItemEditFormSchema(model.Schema):
    directives.widget(text=WysiwygFieldWidget)
    text = schema.Text(title=_(u"Text"))


class NewsItemEditFormAdapter(object):
    component.adapts(IATNewsItem)
    interface.implements(NewsItemEditFormSchema)

    def __init__(self, context):
        self.context = context

    @property
    def text(self):
        field = self.context.getField('text')
        if field:
            return field.get(self.context).decode('utf-8')


class NewsItemEditForm(AutoExtensibleForm, form.Form):
    schema = NewsItemEditFormSchema

    @button.buttonAndHandler(_(u"Save"))
    def action_save(self, action):
        self.next_url()
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            for error in errors:
                IStatusMessage(self.request).add(error.message, "error")
            return False
        self.do_save(data)

    def do_save(self, data):
        field = self.context.getField('text')
        if field:
            new_text = data['text'].decode('utf-8')
            text = field.get(self.context)
            if text != new_text:
                field.set(self.context, new_text)

    def next_url(self):
        url = self.request['HTTP_REFERER']
        self.request.response.redirect(url)


class NewsItemEditFormView(WPDeleteFormView):
    form = NewsItemEditForm
    description = u""

    @property
    def title(self):
        return u"Edit %s" % self.context.Title()


class ImageEditFormSchema(interface.Interface):

    image = NamedBlobImage(title=_(u"Please upload an image"))


class ImageEditFormAdapter(object):
    component.adapts(IATImage)
    interface.implements(ImageEditFormSchema)

    def __init__(self, context):
        self.context = context
        self.image = None


class ImageEditForm(AutoExtensibleForm, form.Form):
    schema = ImageEditFormSchema

    @button.buttonAndHandler(_(u"save"))
    def action_save(self, action):
        self.next_url()
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            for error in errors:
                IStatusMessage(self.request).add(error.message, "error")
            return False
        self.update_file(data)

    def update_file(self, data):
        image = data['image'].data
        field = self.context.getField('image')
        field.set(self.context, image)

    def next_url(self):
        url = self.request['HTTP_REFERER']
        self.request.response.redirect(url)


class ImageEditFormView(WPDeleteFormView):
    form = ImageEditForm
    description = u""

    @property
    def title(self):
        return u"Edit %s" % self.context.Title()
