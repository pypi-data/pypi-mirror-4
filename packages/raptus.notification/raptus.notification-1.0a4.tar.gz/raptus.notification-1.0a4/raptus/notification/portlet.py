from Acquisition import aq_inner

from zope import interface
from zope import schema
from zope import component
from zope.formlib import form

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _p

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from raptus.notification import _
from raptus.notification import interfaces


class INotificationPortlet(IPortletDataProvider):

    header = schema.TextLine(
        title=_p(u'Portlet header'),
        description=_p(u'Title of the rendered portlet')
    )


class Assignment(base.Assignment):
    interface.implements(INotificationPortlet)

    header = u''

    def __init__(self, header=u''):
        self.header = header

    @property
    def title(self):
        return self.header or _(u'Notification portlet')


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('portlet.pt')

    def update(self):
        self.header = self.data.header
        self.notifications = component.getMultiAdapter((self.context, self.request),
                                                       name=u'notifications')

    @property
    def anonymous(self):
        context = aq_inner(self.context)
        portal_state = component.getMultiAdapter((context, self.request),
                                                 name=u'plone_portal_state')
        return portal_state.anonymous()

    @property
    def available(self):
        return not self.anonymous


class AddForm(base.AddForm):
    form_fields = form.Fields(INotificationPortlet)
    label = _(u'Add notification portlet')

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(INotificationPortlet)
    label = _(u'Edit notification portlet')
