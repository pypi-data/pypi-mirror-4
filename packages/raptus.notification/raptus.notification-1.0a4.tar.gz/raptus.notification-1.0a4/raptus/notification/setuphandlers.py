from zope.annotation import IAnnotations

from raptus.notification.notification import ANNOTATIONS_KEY


def uninstall(context):
    if context.readDataFile('raptus.notification.uninstall.txt') is None:
        return
    portal = context.getSite()

    # Remove notification storage to prevent broken object errors after removal
    storage = IAnnotations(portal)
    if storage.get(ANNOTATIONS_KEY, None) is not None:
        del storage[ANNOTATIONS_KEY]
