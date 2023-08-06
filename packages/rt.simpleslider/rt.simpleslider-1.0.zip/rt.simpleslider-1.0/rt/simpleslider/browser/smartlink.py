from zope.component import adapts
from zope.interface import implements
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from redturtle.smartlink.interfaces import ISmartLink

from rt.simpleslider.interfaces import ISliderSource
from rt.simpleslider.browser.slidersource import GenericSliderSource


class SmartLinkSliderSource(GenericSliderSource):

    implements(ISliderSource)
    adapts(IBrowserView, ISmartLink, IDefaultBrowserLayer)

    def getURL(self):
        return self.context.getRemoteUrl()

    def getImage(self):
        caption = self.getCaption()
        field = self.context.getField('image')
        return field.tag(self.context, title=caption)
