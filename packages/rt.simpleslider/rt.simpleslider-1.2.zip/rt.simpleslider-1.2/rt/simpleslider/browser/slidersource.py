# -*- coding: utf-8 -*-

from zope.component import adapts, getMultiAdapter
from zope.interface import implements
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from Products.Archetypes.interfaces.base import IBaseFolder, IBaseObject
from Products.ATContentTypes.interfaces import IATImage
from Products.ATContentTypes.interfaces.topic import IATTopic

from rt.simpleslider.interfaces import ISliderSource, ISliderBrain
from rt.simpleslider import SIZE


class GenericSliderSource(object):

    implements(ISliderSource)
    adapts(IBrowserView, IBaseObject, IDefaultBrowserLayer)

    def __init__(self, view, context, request):
        self.context = context
        self.request = request
        self.view = view

    @property
    def caption_template(self):
        return """<p class="bjqs-caption"><a href="%(url)s">%(caption)s</a></p>"""

    def items(self):
        yield self.context

    def getCaption(self):
        return self.context.title_or_id()

    def getImage(self):
        return ''

    def getURL(self):
        return '#'

    def getSliderImages(self):
        for item in self.items():
            slide = getMultiAdapter((self.view, item, self.request),
                                     ISliderSource)
            img = slide.getImage()
            caption = {'caption': slide.getCaption(),
                       'url': slide.getURL()}

            yield {'image':img,
                   'caption': slide.caption_template % caption}


class FolderishSliderSource(GenericSliderSource):

    implements(ISliderSource)
    adapts(IBrowserView, IBaseFolder, IDefaultBrowserLayer)

    def items(self):
        return self.context.objectValues()


class TopicSliderSource(GenericSliderSource):

    implements(ISliderSource)
    adapts(IBrowserView, IATTopic, IDefaultBrowserLayer)

    def items(self):
        for item in self.context.queryCatalog():
            brain = BrainWrapper(item, self.context)
            if brain.getImage():
                yield brain


class ImageSliderSource(GenericSliderSource):

    implements(ISliderSource)
    adapts(IBrowserView, IATImage, IDefaultBrowserLayer)

    def getImage(self):
        caption = self.getCaption()
        return self.context.tag(title=caption)

    @property
    def caption_template(self):
        return """<p class="bjqs-caption">%(caption)s</p>"""


class BrainWrapper(object):
    implements(ISliderBrain)

    def __init__(self, brain, context):
        self.brain = brain
        self.context = context

    @property
    def caption_template(self):
        if self.brain.portal_type == 'Image':
            return """<p class="bjqs-caption">%(caption)s</p>"""
        else:
            return """<p class="bjqs-caption"><a href="%(url)s">%(caption)s</a></p>"""

    def getCaption(self):
        return self.brain.Title

    def getImage(self):
        cl = getattr(self.brain, 'hasContentLeadImage', False)
        if cl:
            return '<img src="%s/leadImage_%s" title="%s"/>' % \
                    (self.brain.getURL(), SIZE, self.getCaption())
        elif self.brain.portal_type == 'Image':
            return '<img src="%s/image_%s" title="%s"/>' % \
                    (self.brain.getURL(), SIZE, self.getCaption())
        elif self.brain.portal_type == 'Link':
            return '<img src="%s/image_%s" title="%s"/>' % \
                    (self.brain.getURL(), SIZE, self.getCaption())


class BrainSliderSource(GenericSliderSource):

    implements(ISliderSource)
    adapts(IBrowserView, ISliderBrain, IDefaultBrowserLayer)

    def __init__(self, view, context, request):
        self.context = context.context
        self.wrapper = context
        self.brain = context.brain
        self.request = request
        self.view = view

    def getCaption(self):
        return self.wrapper.getCaption()

    def getImage(self):
        return self.wrapper.getImage()

    @property
    def caption_template(self):
        return self.wrapper.caption_template
