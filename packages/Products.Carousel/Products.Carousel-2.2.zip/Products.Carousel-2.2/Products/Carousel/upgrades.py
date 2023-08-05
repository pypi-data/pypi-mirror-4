from Products.CMFCore.utils import getToolByName
from Products.Carousel.interfaces import ICarouselBanner
from Products.Carousel import CarouselMessageFactory as _

def null_upgrade_step(setup_tool):
    """
    This is a null upgrade. Use it when nothing happens
    """
    pass
    
def upgrade_11_to_20b1(setup_tool):
    """
    Upgrade old Carousel banners by moving the description into the new
    body field.
    """
    
    # Install new dependencies.
    qi = getToolByName(setup_tool, 'portal_quickinstaller')
    if qi.isProductInstallable('plone.app.z3cform') and not \
        qi.isProductInstalled('plone.app.z3cform'):
        qi.installProduct('plone.app.z3cform')
    
    # Update Carousel banners.
    catalog = getToolByName(setup_tool, 'portal_catalog')
    transforms = getToolByName(setup_tool, 'portal_transforms')
        
    banners = catalog.searchResults({
        'object_provides': ICarouselBanner.__identifier__,
    })
    
    for banner in banners:
        description = banner.Description
        if description:
            html = transforms.convertTo('text/html',
                description, mimetype='text/plain')
            banner.getObject().setText(html.getData(), mimetype='text/html')
            
    # Change the tab name to Carousel.
    actions = getToolByName(setup_tool, 'portal_actions')
    obj_actions = actions.get('object', {})
    if 'carousel' in obj_actions.keys():
        obj_actions['carousel'].title = _(u'Carousel')
        
def upgrade_21b3_to_10(setup_tool):
    """
    Upgrade action permission settings.
    """
    
    actions = getToolByName(setup_tool, 'portal_actions')
    carousel = actions.get('object', {}).get('carousel', None)
    if carousel:
        if carousel.permissions == ('Manage portal',):
            carousel.permissions = ('Carousel: Manage Carousel',)
