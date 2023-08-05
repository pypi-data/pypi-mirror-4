import types
from AccessControl.Permission import Permission
from zope.interface import Interface
from zope.component import getSiteManager
from zope.publisher.interfaces.browser import IBrowserView, IDefaultBrowserLayer
from zope.viewlet.interfaces import IViewlet
from Products.Carousel.browser.viewlet import CarouselViewlet

def hasViewlet():
    """Returns true if the Carousel viewlet is already registered locally"""
    sm = getSiteManager()
    return len([reg for reg in sm.registeredAdapters() if reg.factory is CarouselViewlet]) > 0

def registerViewlet(manager):
    """Creates a local Carousel viewlet registration (and removes any existing one)"""
    unregisterViewlet()

    sm = getSiteManager()
    sm.registerAdapter(
        CarouselViewlet,
        required = (Interface, IDefaultBrowserLayer, IBrowserView, manager),
        provided = IViewlet,
        name = u'Products.Carousel.viewlet'
        )

def unregisterViewlet():
    """Removes the local Carousel viewlet registration"""
    sm = getSiteManager()
    # need to not have a generator, so that we can make modifications
    regs = list(sm.registeredAdapters())
    for reg in regs:
        if reg.factory is CarouselViewlet:
            sm.unregisterAdapter(CarouselViewlet, reg.required, reg.provided, reg.name)

def addPermissionsForRole(context, role, wanted_permissions):
    """ Add permissions for a role in the context.

    Parameters:
        @param context Portal object (portal itself, Archetypes item, any inherited from RoleManager)
        @param role role name, as a string
        @param wanted_permissions tuple of permissions (string names) to add for the role    

    All wanted_permissions lose their acquiring ability
    """

    assert type(wanted_permissions) == types.TupleType

    #print "Doing role:" + role + " perms:" + str(wanted_permissions)
    for p in context.ac_inherited_permissions(all=True):
        name, value = p[:2]
        p=Permission(name, value, context)
        roles=list(p.getRoles())

        #print "Permission:" + name + " roles " + str(roles)
        if name in wanted_permissions:
            if role not in roles:
                roles.append(role)
            p.setRoles(tuple(roles))

def removePermissionsForRole(context, role, wanted_permissions):
    """ Remove permissions for a role in the context.

    Parameters:
        @param context Portal object (portal itself, Archetypes item, any inherited from RoleManager)
        @param role role name, as a string
        @param wanted_permissions tuple of permissions (string names) to add for the role    

    All wanted_permissions lose their acquiring ability
    """        

    assert type(wanted_permissions) == types.TupleType

    #print "Doing role:" + role + " perms:" + str(wanted_permissions)
    for p in context.ac_inherited_permissions(all=True):
        name, value = p[:2]
        p=Permission(name, value, context)
        roles=list(p.getRoles())

        #print "Permission:" + name + " roles " + str(roles)
        if name in wanted_permissions:
            if role in roles:
                roles.remove(role)
            p.setRoles(tuple(roles))
