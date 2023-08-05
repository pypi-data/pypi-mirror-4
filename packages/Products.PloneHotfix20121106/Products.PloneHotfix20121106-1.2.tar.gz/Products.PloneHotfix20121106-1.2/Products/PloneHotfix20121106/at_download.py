from zExceptions import Unauthorized


def check_perm(func):
	def protected_func(self, instance, *args, **kw):
		if not self.checkPermission('r', instance):
			raise Unauthorized('Field %s requires %s permission' % (self, self.read_permission))
		return func(self, instance, *args, **kw)
	return protected_func


from Products.Archetypes.Field import FileField
FileField.download = check_perm(FileField.download)


try:
	from plone.app.blob.field import BlobField
	BlobField.index_html = check_perm(BlobField.index_html)
except ImportError:
	pass
