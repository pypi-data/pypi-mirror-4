from Products.CMFPlone.PloneControlPanel import PloneControlPanel

PloneControlPanel.registerConfiglet__roles__ = \
    PloneControlPanel.registerConfiglets__roles__

_perms = dict(PloneControlPanel.__ac_permissions__)
for name, methods in _perms.items():
    if 'registerConfiglets' in methods:
        methods = set(methods)
        methods.add('registerConfiglet')
        _perms[name] = tuple(methods)
PloneControlPanel.__ac_permissions__ = _perms.items()
