from zope.interface import alsoProvides
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Carousel.interfaces import ICarouselFolder
from Products.Carousel.utils import addPermissionsForRole
from Products.Carousel.config import CAROUSEL_ID

class CarouselManager(BrowserView):
    
    def __call__(self):
        
        if hasattr(self.context.aq_base, CAROUSEL_ID):
            carousel = getattr(self.context, CAROUSEL_ID)
        else:
            pt = getToolByName(self.context, 'portal_types')
            newid = pt.constructContent('Folder', self.context, 'carousel', title='Carousel Banners', excludeFromNav=True)
            carousel = getattr(self.context, newid)
            
            # mark the new folder as a Carousel folder
            alsoProvides(carousel, ICarouselFolder)
            
            # make sure Carousel banners are addable within the new folder
            addPermissionsForRole(carousel, 'Manager', ('Carousel: Add Carousel Banner',))
            addPermissionsForRole(carousel, 'Site Administrator', ('Carousel: Add Carousel Banner',))
            
            # make sure *only* Carousel banners are addable
            carousel.setConstrainTypesMode(1)
            carousel.setLocallyAllowedTypes(['Carousel Banner'])
            carousel.setImmediatelyAddableTypes(['Carousel Banner'])

        self.request.RESPONSE.redirect(
            carousel.absolute_url() + '/@@edit-carousel'
        )

