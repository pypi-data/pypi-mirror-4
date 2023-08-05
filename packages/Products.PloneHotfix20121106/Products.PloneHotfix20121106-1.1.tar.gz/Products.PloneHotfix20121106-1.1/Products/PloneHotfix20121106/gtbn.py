from Products.CMFCore import utils
try:
   from Products.CMFPlone.FactoryTool import FauxArchetypeTool
   HAS_FAT = True
except ImportError:
   FauxArchetypeTool = None
   HAS_FAT = False
from persistent.interfaces import IPersistent
try:
    from OFS.interfaces import IItem
except ImportError:
    IItem = IPersistent

try:
    tool_registry = utils._tool_interface_registry
except AttributeError:
    tool_registry = {}

gtbn = utils.getToolByName
def wrapped_getToolByName(obj, name, default=utils._marker):
    result = gtbn(obj, name, default)
    if IPersistent.providedBy(result) or \
            IItem.providedBy(result) or \
            name in tool_registry or \
            (HAS_FAT and isinstance(result, FauxArchetypeTool)) or \
            result is utils._marker or \
            result is default:
        return result
    else:
        raise TypeError("Object found is not a portal tool (%s)" % (name,))
    return result
utils.getToolByName = wrapped_getToolByName

try:
    import Products.CMFPlone.utils
    Products.CMFPlone.utils.getToolByName = wrapped_getToolByName
except ImportError:
    pass
