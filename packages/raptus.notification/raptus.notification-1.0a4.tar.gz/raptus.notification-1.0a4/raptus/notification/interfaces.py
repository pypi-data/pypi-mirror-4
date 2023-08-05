from persistent.interfaces import IPersistent

from zope import interface
from zope import schema


class INotificationSender(interface.Interface):
    """ Notification sender
    """

    def send(notification):
        """ Sends a new notification (INotification) and returns the
            generated ID
        """


class INotifications(INotificationSender):
    """ Notification manager
    """

    def __iter__():
        """ Iterator over the available notifications of the
            current user
        """

    def __getitem__(id):
        """ Returns the notification with the given ID if available
        """

    def __delitem__(id):
        """ Deletes the notification with the given ID for the current
            user
        """

    def delete(notification):
        """ Deletes the given notification for the current user
        """


class INotification(IPersistent):
    """ A notification
    """

    id = schema.Int(
        required=True
    )

    title = schema.TextLine(
        required=True
    )

    description = schema.Text(
        required=False
    )

    url = schema.ASCIILine(
        required=False
    )

    user = schema.ASCIILine(
        required=True
    )

    new = schema.Bool(
        required=False,
        default=True
    )

    def available():
        """ Whether this notification is available or not
        """


class INotificationsView(interface.Interface):
    """ View rendering and deleting notifications of the
        current user
    """

    def __call__(amount=5):
        """ Renders the latest notifications of the current user
        """

    def delete(id, came_from):
        """ Deletes the notification with the given id for
            the current user and redirects to the url given
        """

    def read(id):
        """ Marks the notification with the given id as read
            and redirects to it's URL
        """

    def news(latest=None):
        """ Whether there are notifications available newer than
            the one provided
        """

    def unread():
        """ The number of unread notifications for the current user
        """
