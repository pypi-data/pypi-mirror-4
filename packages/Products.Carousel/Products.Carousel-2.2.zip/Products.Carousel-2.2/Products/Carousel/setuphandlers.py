from zope.component import getUtility
from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
from plone.app.layout.viewlets.interfaces import IAboveContent, IContentViews
from Products.Carousel.utils import hasViewlet, registerViewlet
from Products.Carousel import HAS_PLONE4

if HAS_PLONE4:
    default_viewlet_manager = IAboveContent
    default_viewlet_manager_name = 'plone.abovecontent'
else:
    default_viewlet_manager = IContentViews
    default_viewlet_manager_name = 'plone.contentviews'

def configureViewlet(gscontext):
    """ Add the Carousel viewlet to the plone.contentviews viewlet manager
        as a *local* adapter, if it's not already registered for a manager.
    """
    if gscontext.readDataFile('carousel_various.txt') is None:
        # don't run this step for other profiles
        return

    if not hasViewlet():
        registerViewlet(default_viewlet_manager)
        
        # make sure it's first in the content views manager
        storage = getUtility(IViewletSettingsStorage)
        skins = getattr(storage, '_order')
        for skinname in skins:
            values = list(skins[skinname].get(default_viewlet_manager_name, []))
            values.insert(0, 'Products.Carousel.viewlet')
            storage.setOrder(default_viewlet_manager_name, skinname, tuple(values))
