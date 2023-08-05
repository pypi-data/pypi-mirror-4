try:
    from Products.Archetypes.UIDCatalog import UIDCatalog
except ImportError:
    from Products.Archetypes.ReferenceEngine import UIDCatalog

if hasattr(UIDCatalog.resolve_url, '__doc__'):
    del UIDCatalog.resolve_url.im_func.__doc__
if not hasattr(UIDCatalog, '__ac_permissions__'):
    UIDCatalog.__ac_permissions__ = ()
