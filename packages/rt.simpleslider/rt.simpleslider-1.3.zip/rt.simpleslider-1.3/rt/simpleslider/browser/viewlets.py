# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import queryMultiAdapter, getMultiAdapter
from plone.app.layout.viewlets.common import ViewletBase
from plone.app.imaging.utils import getAllowedSizes
from rt.simpleslider.interfaces import ISliderSource
from rt.simpleslider.interfaces import ISliderUtils


JS_TEMPLATE = """
    (function($) {
        $('#simpleslider').bjqs({
              'height' : %(height)s,
              'width' : %(width)s,
              'usecaptions' : false,
              'responsive' : true
        });
    }(jQuery));"""


class Slider(ViewletBase):
    """ This viewlet renders the placholder for gallery """
    index = ViewPageTemplateFile('slider_viewlet.pt')

    def update(self):
        super(Slider, self).update()
        self.request.slider_tool = getMultiAdapter((self.view, self.context, self.request), ISliderUtils)
        slider_source_context = self.request.slider_tool.slider_source()
        self.request.slider_source = queryMultiAdapter((self.view, slider_source_context, self.request), ISliderSource)

    def render(self):
        if not self.request.slider_tool.show_slider():
            return ''
        sizes = getAllowedSizes()
        width, height = sizes['simpleslider']
        js = JS_TEMPLATE % {'width':width, 'height': height}
        return self.index(js=js)

    def slider_images(self):
        return self.request.slider_source.getSliderImages()
