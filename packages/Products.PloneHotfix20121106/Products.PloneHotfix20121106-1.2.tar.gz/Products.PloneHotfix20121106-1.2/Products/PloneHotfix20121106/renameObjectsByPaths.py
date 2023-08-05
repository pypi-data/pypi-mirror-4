try:
   from AccessControl.requestmethod import postonly
   HAS_POSTONLY = True
except ImportError:
   HAS_POSTONLY = False
from AccessControl import getSecurityManager
from Acquisition import aq_parent, aq_inner
from zExceptions import Unauthorized
from ZODB.POSException import ConflictError
import transaction
from zope.event import notify
from Products.CMFPlone.PloneTool import PloneTool
try:
    from zope.lifecycleevent import ObjectModifiedEvent
except ImportError:
    from zope.app.event.objectevent import ObjectModifiedEvent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import transaction_note


if not HAS_POSTONLY:
   def postonly(fn):
       def inner(self, *args, **kwargs):
           request = kwargs.get('REQUEST', None)
           if request is None and len(args)>=5:
               request = args[4]
           if request is not None and request['REQUEST_METHOD']!='POST':
               raise Unauthorized('Request must be POST')

           return fn(self, *args, **kwargs)
       return inner


def renameObjectsByPaths(self, paths, new_ids, new_titles,
                         handle_errors=True, REQUEST=None):
    failure = {}
    success = {}
    # use the portal for traversal in case we have relative paths
    portal = getToolByName(self, 'portal_url').getPortalObject()
    traverse = portal.restrictedTraverse
    for i, path in enumerate(paths):
        new_id = new_ids[i]
        new_title = new_titles[i]
        if handle_errors:
            sp = transaction.savepoint(optimistic=True)
        try:
            obj = traverse(path, None)
            obid = obj.getId()
            title = obj.Title()
            change_title = new_title and title != new_title
            changed = False
            if change_title:
                getSecurityManager().validate(obj, obj, 'setTitle', obj.setTitle)
                obj.setTitle(new_title)
                notify(ObjectModifiedEvent(obj))
                changed = True
            if new_id and obid != new_id:
                parent = aq_parent(aq_inner(obj))
                parent.manage_renameObjects((obid,), (new_id,))
                changed = True
            elif change_title:
                # the rename will have already triggered a reindex
                obj.reindexObject()
            if changed:
                success[path] = (new_id, new_title)
        except ConflictError:
            raise
        except Exception, e:
            if handle_errors:
                # skip this object but continue with sub-objects.
                sp.rollback()
                failure[path] = e
            else:
                raise
    transaction_note('Renamed %s' % str(success.keys()))
    return success, failure
renameObjectsByPaths = postonly(renameObjectsByPaths)

try:
    from plone.protect import protect, CheckAuthenticator
except ImportError:
    pass
else:
    renameObjectsByPaths = protect(CheckAuthenticator)(renameObjectsByPaths)

PloneTool.renameObjectsByPaths = renameObjectsByPaths
