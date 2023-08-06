from Products.CMFCore.utils import getToolByName
from Products.Carousel.utils import unregisterViewlet

def install(portal, reinstall=False):
    setup_tool = getToolByName(portal, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile('profile-Products.Carousel:default')

def uninstall(portal, reinstall=False):
    if not reinstall:
        unregisterViewlet()
