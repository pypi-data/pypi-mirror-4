import logging

from Acquisition import aq_inner
from zope import interface
from zope import schema
from z3c.form.interfaces import ISubForm, IFormLayer

from plone.z3cform.interfaces import IWrappedForm
from plone.z3cform import z2

from collective.wpadmin import i18n
from collective.wpadmin.utils import Core
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

_ = i18n.messageFactory
logger = logging.getLogger('collective.wpadmin')


class IWidget(interface.Interface):
    """Define a widget for the WP Admin view"""

    name = schema.ASCIILine(title=_(u"Widget name"))
    title = schema.TextLine(title=_(u"Title"))
    description = schema.TextLine(title=_(u"Description"))
    settings = schema.Object(interface.Interface, title=_(u"Settings"))


class Widget(Core):
    interface.implements(IWidget)
    columns = 6
    template_name = "widget.pt"
    content_template_name = ""
    title = u"Widget"
    description = u""

    def __init__(self, page):
        Core.__init__(self, page.context, page.request)
        self.page = page

    @property
    def content(self):
        template = '../templates/%s' % self.content_template_name
        return ViewPageTemplateFile(template)(self)


class WidgetFormWrapper(Widget):
    """Add support to non browserview for z3c.form
    multi update/rendering issue when redirection happens"""

    form = None  # override this with a form class.
    request_layer = IFormLayer

    def __init__(self, page):
        super(WidgetFormWrapper, self).__init__(page)
        if self.form is not None:
            self.form_instance = self.form(
                aq_inner(self.context), self.request)
            self.form_instance.__name__ = self.name
            self.form_instance.parent_widget = self

    def update(self):
        if not ISubForm.providedBy(self.form_instance):
            interface.alsoProvides(self.form_instance, IWrappedForm)

        # If a form action redirected, don't render the wrapped form
        if self.request.response.getStatus() in (302, 303):
            self.contents = ""
            return

        z2.switch_on(self, request_layer=self.request_layer)
        self.form_instance.update()

        # A z3c.form.form.AddForm does a redirect in its render method.
        # So we have to render the form to see if we have a redirection.
        # In the case of redirection, we don't render the layout at all.
        self.contents = self.form_instance.render()
