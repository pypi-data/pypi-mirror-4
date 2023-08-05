from AccessControl.PermissionRole import PermissionRole
from Products.CMFCore.permissions import ListPortalMembers
try:
    from Products.PlonePAS.tools.membership import MembershipTool
except ImportError:
    from Products.CMFPlone.MembershipTool import MembershipTool
MembershipTool.searchForMembers__roles__ = PermissionRole(ListPortalMembers, ('Manager',))
if hasattr(MembershipTool.getMemberInfo.im_func, '__doc__'):
    del MembershipTool.getMemberInfo.im_func.__doc__
