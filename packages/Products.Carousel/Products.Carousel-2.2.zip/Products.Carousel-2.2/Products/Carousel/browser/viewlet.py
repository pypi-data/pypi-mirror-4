from Acquisition import aq_base
from zope.component import queryMultiAdapter
from zope.interface import Interface
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.layout.viewlets.common import ViewletBase

from Products.Carousel.config import CAROUSEL_ID
from Products.Carousel.interfaces import ICarousel


class CarouselViewlet(ViewletBase):
    __name__ = 'Products.Carousel.viewlet'

    index = ViewPageTemplateFile('viewlet.pt')

    def _template_for_carousel(self, name, carousel):
        """
        Returns a template for rendering the banners or pager.
        """

        template = queryMultiAdapter(
            (carousel, self.request),
            Interface,
            default=None,
            name=name.replace('@@', '')
        )

        if template:
            return template.__of__(carousel)
        return None

    def update(self):
        """
        Set the variables needed by the template.
        """

        self.available = False

        context_state = self.context.restrictedTraverse('@@plone_context_state')
        if context_state.is_structural_folder() and not context_state.is_default_page():
            folder = self.context
        else:
            folder = context_state.parent()

        if hasattr(aq_base(folder), CAROUSEL_ID):
            carousel = ICarousel(folder[CAROUSEL_ID], None)
            if not carousel:
                return
        else:
            return

        settings = carousel.getSettings()

        if not settings.enabled:
            return

        if not context_state.is_default_page():
            if settings.default_page_only:
                if folder != self.context:
                    return
                elif self.context.defaultView() != context_state.view_template_id():
                    return
            elif folder == self.context:
                    if not context_state.is_view_template():
                        return

        banners = carousel.getBanners()
        if not banners:
            return

        self.banners = self._template_for_carousel(
            settings.banner_template or u'@@banner-default',
            carousel
        )

        self.pager = self._template_for_carousel(
            settings.pager_template or u'@@pager-numbers',
            carousel
        )

        width, height = banners[0].getSize()
        self.height = settings.height or height or 0
        self.width = settings.width or width or 0
        self.transition = settings.transition_type
        self.speed = int(settings.transition_speed * 1000)
        self.delay = int(settings.transition_delay * 1000)
        self.element_id = settings.element_id
        self.available = True
