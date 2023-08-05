from AccessControl.SecurityManagement import getSecurityManager
import AccessControl.users

def FakeUser(context, user='system'):
    """Function that fakes a user.  Will use system user (has full
    access) by default.  If you want to fake a real user stored
    in an acl_users folder, specify relative or full path (for
    example 'acl_users/admin'."""
    # Fakes a user
    manager = getSecurityManager()
    manager._context.old_user = manager._context.user
    if '/' in user:
        # Fake a user stored in the database
        path, username = user.rsplit('/', 1)
        try:
            user_object = context.unrestrictedTraverse(path).getUser(username)
            if user_object is None:
                # Some Zope/Plone/remember/membrane funkyness maybe
                # 
                # Anyway, user_folder from above portal should be
                # accessible and usable
                user_object = context.portal_url.getPortalObject().getParentNode().acl_users.getUser(username)
        except:
            raise ValueError, '%s is not a valid path/username' % user
    elif user in ('nobody', 'system'):
        user_object = getattr(AccessControl.users, user)
    else:
        raise ValueError, '%s is not a valid username' % user
    if user_object is None:
        import pdb; pdb.set_trace()
    manager._context.user = user_object
#    print 'FZU', manager, user_object

def UnFakeUser(context):
    "Function that unfakes a user."""
    manager = getSecurityManager()
    manager._context.user = manager._context.old_user
    del manager._context.old_user
