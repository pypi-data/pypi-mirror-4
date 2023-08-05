from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from collective.googleanalytics.tracking import AnalyticsBaseTrackingPlugin

class CarouselBannerPlugin(AnalyticsBaseTrackingPlugin):
    """
    A tracking plugin to track clicks on Carousel banners.
    """

    __call__ = ViewPageTemplateFile('banner.pt')
