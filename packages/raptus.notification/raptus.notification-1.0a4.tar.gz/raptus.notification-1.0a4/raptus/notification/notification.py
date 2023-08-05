from threading import Lock

from BTrees.IOBTree import IOBTree
from BTrees.OOBTree import OOBTree
from persistent import Persistent, dict, list

from zope import interface
from zope import component
from zope import schema
from zope.site.hooks import getSite
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.annotation import IAnnotations

from raptus.notification import interfaces

notification_lock = Lock()
ANNOTATIONS_KEY = 'raptus.notification'


class NotificationSender(object):
    interface.implements(interfaces.INotificationSender)

    def __init__(self):
        self.storage = None

    @property
    def context(self):
        return getSite()

    def _initialize(self, create=False):
        if self.storage is not None:
            return
        storage = IAnnotations(self.context)
        if storage.get(ANNOTATIONS_KEY, None) is None:
            storage[ANNOTATIONS_KEY] = dict.PersistentDict()
            storage[ANNOTATIONS_KEY]['notifications'] = IOBTree()
            storage[ANNOTATIONS_KEY]['user'] = OOBTree()
            storage[ANNOTATIONS_KEY]['intid'] = 1
        self.storage = storage.get(ANNOTATIONS_KEY, None)

    def send(self, notification):
        if not interfaces.INotification.providedBy(notification):
            raise ValueError('notification', 'INotification expected got %s' % notification.__class__)
        self._initialize(True)
        notification_lock.acquire()
        notification.id = self.storage['intid']
        notification.new = True
        self.storage['notifications'][notification.id] = notification
        if not notification.user in self.storage['user']:
            self.storage['user'][notification.user] = list.PersistentList()
        self.storage['user'][notification.user].insert(0, notification.id)
        self.storage['intid'] += 1
        notification_lock.release()
        return notification.id


class Notifications(NotificationSender):
    interface.implements(interfaces.INotifications)
    component.adapts(IBrowserRequest)

    def __init__(self, request):
        super(Notifications, self).__init__()
        self.request = request
        self.username = component.getMultiAdapter((self.context, self.request), name='plone_portal_state').member().getMemberId()

    def __iter__(self):
        self._initialize(False)
        if self.storage is not None and self.username in self.storage['user']:
            for id in self.storage['user'][self.username]:
                notification = self.storage['notifications'].get(id, None)
                if notification is not None and notification.available():
                    yield self.storage['notifications'][id]

    def __getitem__(self, id):
        self._initialize(False)
        if self.storage is None or not id in self.storage['notifications']:
            return None
        return self.storage['notifications'][id]

    def __delitem__(self, id):
        self._initialize(False)
        if not id in self.storage['notifications']:
            return
        if self.username in self.storage['user'] and id in self.storage['user'][self.username]:
            self.storage['user'][self.username].remove(id)
            del self.storage['notifications'][id]

    def delete(self, notification):
        if not interfaces.INotification.providedBy(notification):
            raise ValueError('notification', 'INotification expected got %s' % notification.__class__)
        del self[notification.id]


class Notification(Persistent):
    interface.implements(interfaces.INotification)

    id = schema.fieldproperty.FieldProperty(interfaces.INotification['id'])
    title = schema.fieldproperty.FieldProperty(interfaces.INotification['title'])
    description = schema.fieldproperty.FieldProperty(interfaces.INotification['description'])
    url = schema.fieldproperty.FieldProperty(interfaces.INotification['url'])
    user = schema.fieldproperty.FieldProperty(interfaces.INotification['user'])
    new = schema.fieldproperty.FieldProperty(interfaces.INotification['new'])

    def __init__(self, title, description, url, user):
        self.title = title
        self.description = description
        self.url = url
        self.user = user

    def available(self):
        return True
