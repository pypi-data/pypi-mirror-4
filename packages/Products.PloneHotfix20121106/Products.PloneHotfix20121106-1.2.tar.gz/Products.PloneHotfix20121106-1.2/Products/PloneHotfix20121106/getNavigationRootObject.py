from Acquisition import aq_base, aq_parent, aq_inner
from plone.app.layout.navigation import root
from plone.app.layout.navigation.interfaces import INavigationRoot


def getNavigationRootObject(context, portal):
    obj = context
    while (not INavigationRoot.providedBy(obj) and
            aq_base(obj) is not aq_base(portal)):
        parent = aq_parent(aq_inner(obj))
        if parent is None:
            return obj
        obj = parent
    return obj
root.getNavigationRootObject = getNavigationRootObject
