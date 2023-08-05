from time import time
from random import shuffle

from persistent import Persistent
import ExtensionClass
from zope.annotation import factory
from zope.component import adapts
from zope.interface import implements
from z3c.form import form, field, group
from z3c.form.browser.checkbox import SingleCheckBoxFieldWidget, \
    CheckBoxFieldWidget
from plone.app.z3cform.layout import FormWrapper
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.interfaces import IFolderish
from Products.ATContentTypes.interface.topic import IATTopic
from Products.Carousel.interfaces import ICarousel, ICarouselSettings, \
    ICarouselFolder, ICarouselSettingsView, ICarouselBanner
from Products.Carousel import CarouselMessageFactory as _


class Carousel(ExtensionClass.Base):
    implements(ICarousel)
    adapts(ICarouselFolder)

    def __init__(self, context):
        self.context = context

    def getSettings(self):
        """
        Returns an object that provides ICarouselSettings.
        """

        return ICarouselSettings(self.context)

    def getBanners(self):
        """
        Returns a list of objects that provide ICarouselBanner.
        """

        banner_brains = []
        if IFolderish.providedBy(self.context):
            catalog = getToolByName(self.context, 'portal_catalog')
            banner_brains = catalog.searchResults({
                'path': '/'.join(self.context.getPhysicalPath()),
                'object_provides': ICarouselBanner.__identifier__,
                'sort_on': 'getObjPositionInParent',
            })
        elif IATTopic.providedBy(self.context):
            banner_brains = self.context.queryCatalog()

        banner_objects = [b.getObject() for b in banner_brains]
        banner_objects = [b for b in banner_objects if ICarouselBanner.providedBy(b)]

        # Shuffle carousel images if needde
        if self.getSettings().random_order:
            shuffle(banner_objects)

        return banner_objects


class CarouselSettings(Persistent):
    """
    Settings for a Carousel instance.
    """

    implements(ICarouselSettings)
    adapts(ICarouselFolder)

    enabled = True
    banner_template = u'@@banner-default'
    banner_elements = [u'title', u'text', u'image']
    width = None
    height = None
    pager_template = u'@@pager-numbers'
    element_id = u'carousel-default'
    transition_type = u'fade'
    transition_speed = 0.5
    transition_delay = 8.0
    default_page_only = True
    lazyload = False
    random_order = False

    def __init__(self):
        self.element_id = u'carousel-%s' % hash(time())

CarouselSettingsFactory = factory(CarouselSettings)


class AppearanceGroup(group.Group):
    """
    Appearance options.
    """

    label = _(u'Appearance')
    fields = field.Fields(ICarouselSettings).select(
        'banner_template', 'banner_elements', 'width', 'height',
        'pager_template', 'element_id', 'lazyload', 'random_order')
    fields['banner_elements'].widgetFactory = CheckBoxFieldWidget
    fields['lazyload'].widgetFactory = SingleCheckBoxFieldWidget
    fields['random_order'].widgetFactory = SingleCheckBoxFieldWidget


class TransitionGroup(group.Group):
    """
    Transition options.
    """

    label = _(u'Transition')
    fields = field.Fields(ICarouselSettings).select(
        'transition_type', 'transition_speed', 'transition_delay')


class DisplayGroup(group.Group):
    """
    Display options.
    """

    label = _(u'Display')
    fields = field.Fields(ICarouselSettings).select(
        'enabled', 'default_page_only')
    fields['enabled'].widgetFactory = SingleCheckBoxFieldWidget
    fields['default_page_only'].widgetFactory = SingleCheckBoxFieldWidget


class CarouselSettingsForm(group.GroupForm, form.EditForm):
    """
    Form for editing Carousel settings.
    """

    label = _(u'Carousel Settings')
    groups = (AppearanceGroup, TransitionGroup, DisplayGroup,)

    def getContent(self):
        return ICarouselSettings(self.context)

CarouselSettingsForm.buttons['apply'].title = _(u'Save')


class CarouselSettingsView(FormWrapper):
    """
    View for searching and filtering ATResources.
    """

    implements(ICarouselSettingsView)

    index = ViewPageTemplateFile('settings.pt')
    form = CarouselSettingsForm
