from urllib import urlencode

from zope import interface
from zope import component

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.memoize.view import memoize_contextless

from raptus.notification import interfaces


class Notifications(BrowserView):
    interface.implements(interfaces.INotificationsView)

    template = ViewPageTemplateFile('notifications.pt')
    default_amount = 5

    def __call__(self, amount=None):
        """ Renders the latest notifications of the current user
        """
        if amount is None:
            amount = self.default_amount
        else:
            try:
                amount = int(amount)
            except ValueError:
                amount = self.default_amount
        self.notifications = self._get_notifications(amount)
        portal_url = component.getMultiAdapter((self.context, self.request), name='plone_portal_state').portal_url()
        self._delete_url = portal_url + '/@@notifications/delete?'
        self._read_url = portal_url + '/@@notifications/read?'
        self.url = portal_url + '/@@notifications'
        return self.template()

    def delete_url(self, notification):
        return self._delete_url + urlencode({'id': notification.id,
                                             'came_from': self.request.getURL()})

    def read_url(self, notification):
        return self._read_url + urlencode({'id': notification.id})

    def _get_notifications(self, amount):
        notifications = []
        for notification in interfaces.INotifications(self.request):
            if amount <= 0:
                break
            notifications.append(notification)
            amount -= 1
        return notifications

    def delete(self, id, came_from=None):
        """ Deletes the notification with the given id for
            the current user
        """
        try:
            del interfaces.INotifications(self.request)[int(id)]
            ret = '1'
        except ValueError:
            ret = '0'
        if self.request.get('ajax_load', None) is not None:
            return ret
        if came_from is None:
            came_from = self.context.absolute_url()
        return self.request.response.redirect(came_from)

    def read(self, id):
        """ Marks the notification with the given id as read
            and redirects to it's URL
        """
        notification = None
        try:
            notification = interfaces.INotifications(self.request)[int(id)]
            notification.new = False
            ret = '1'
        except ValueError:
            ret = '0'
        if self.request.get('ajax_load', None) is not None:
            return ret
        if notification is not None and notification.url:
            return self.request.response.redirect(notification.url)
        return self.request.response.redirect(self.context.absolute_url())

    def news(self, latest=None):
        """ Whether there are notifications available newer than
            the one provided
        """
        try:
            for notification in interfaces.INotifications(self.request):
                if not latest or notification.id > int(latest):
                    return '1'
        except:
            pass
        return '0'

    def unread(self):
        """ The number of unread notifications for the current user
        """
        try:
            amount = 0
            for notification in interfaces.INotifications(self.request):
                if notification.new:
                    amount += 1
            return str(amount)
        except:
            pass
        return '0'
