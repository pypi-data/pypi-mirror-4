from Products.Five.metaconfigure import ClassDirective

old_require = ClassDirective.require
def require(self, *args, **kw):
    if self._ClassDirective__class.__module__.startswith('z3c.form.browser'):
        return
    return old_require(self, *args, **kw)
ClassDirective.require = require
