from zope.interface import Interface
from zope.app.publisher.browser.viewmeta import _handle_menu
from zope.configuration.fields import GlobalInterface, Path, MessageID
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.schema import TextLine
from Products.Five.browser.metaconfigure import page
from Products.Carousel.interfaces import ICarousel

class ICarouselDirective(Interface):
    """
    A ZCML directive for register a banner or pager template for Carousel.
    """
    
    name = TextLine(
        title=u"The name of the banner or pager",
        description=u"The name shows up in URLs/paths. For example 'foo'.",
        required=True,
        )
        
    template = Path(
        title=u"The name of a template that implements the banner or pager",
        description=u"Refers to a file containing a page template (should end in"
            u"extension '.pt' or '.html').",
        required=True
        )
    
    title = MessageID(
        title=u"The browser menu label for the banner or pager",
        required=True
        )
        
    layer = GlobalInterface(
        title=u"The layer the banner or pager is declared for",
        description=u"The default layer for which the banner or pager is "
                    u"applicable. By default it is applied to all layers.",
        required=False
        )

def banner(_context, name, template, title, layer=IDefaultBrowserLayer):
    """
    Registers a banner template for use with Carousel.
    """
    
    page(_context, name, 'zope.Public', ICarousel, layer=layer,
        template=template)
        
    menu = _context.resolve('zope.app.menus.carousel_bannertemplates')
    _handle_menu(_context, menu, title, 
        [ICarousel], name, 'zope.Public', layer)
        
def pager(_context, name, template, title, layer=IDefaultBrowserLayer):
    """
    Registers a pager template for use with Carousel.
    """
    
    page(_context, name, 'zope.Public', ICarousel, layer=layer,
        template=template)
        
    menu = _context.resolve('zope.app.menus.carousel_pagertemplates')
    _handle_menu(_context, menu, title, 
        [ICarousel], name, 'zope.Public', layer)