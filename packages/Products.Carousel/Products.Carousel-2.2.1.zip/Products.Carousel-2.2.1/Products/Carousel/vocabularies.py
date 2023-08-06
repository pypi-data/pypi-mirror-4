from zope.interface import implements
from zope.app.publisher.interfaces.browser import IBrowserMenu
from zope.component import getUtility
from zope.schema.vocabulary import SimpleVocabulary
from Products.Carousel.interfaces import ICarousel

class DummyCarouselFolder(object):
    implements(ICarousel)

def getContext(context):
    """
    The context for the vocabulary could be an annotation, so we need
    this wrapper to get the real context.
    """
    
    if not hasattr(context, 'REQUEST') and hasattr(context, '__parent__'):
        return context.__parent__
    return context
    
def uniqueMenuItems(items, sort_first):
    """
    Returns a list of tuples in the form (title, action) where both title
    and action are unique.
    """
    
    results = {}
    for item in items:
        if not item['title'] in results.keys() \
            and not item['action'] in results.values():
            results[item['title']] = item['action']
    return sorted(results.items(),
        key=lambda item: (item[0] != sort_first, item))

def getBannerTemplates(context):
    context = getContext(context)
    menu = getUtility(IBrowserMenu, name='carousel_bannertemplates')
    items = menu.getMenuItems(DummyCarouselFolder(), context.REQUEST)
    return SimpleVocabulary.fromItems(uniqueMenuItems(items, 'Default'))
    
def getPagerTemplates(context):
    context = getContext(context)
    menu = getUtility(IBrowserMenu, name='carousel_pagertemplates')
    items = menu.getMenuItems(DummyCarouselFolder(), context.REQUEST)
    return SimpleVocabulary.fromItems(uniqueMenuItems(items, 'None'))