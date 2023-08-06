# -*- coding: utf-8 -*-
import os
from zope.component import adapts
from zope.interface import implements
from zope.publisher.interfaces.browser import IBrowserView
from Products.Archetypes.interfaces.base import IBaseObject
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.contentleadimage.interfaces import ILeadImageable,\
     ILeadImageSpecific
from collective.contentleadimage.config import IMAGE_FIELD_NAME
from collective.contentleadimage.config import IMAGE_CAPTION_FIELD_NAME
from collective.contentleadimage.browser.viewlets import LeadImageViewlet as BaseViewlet
from collective.contentleadimage.browser import viewlets

from rt.simpleslider.interfaces import ISliderSource
from rt.simpleslider.vocabularies import SLIDER_MYSELF
from rt.simpleslider.browser.slidersource import GenericSliderSource


class ContentLeadImageSliderSource(GenericSliderSource):

    implements(ISliderSource)
    adapts(IBrowserView, IBaseObject, ILeadImageSpecific)

    @property
    def caption_template(self):
        return """<p class="bjqs-caption">%(caption)s</p>"""

    def getCaption(self):
        if not ILeadImageable.providedBy(self.context):
            return self.context.title_or_id()

        field = self.context.getField(IMAGE_CAPTION_FIELD_NAME)
        caption = field.get_size(self.context) != 0
        if not caption:
            return self.context.title_or_id()
        else:
            return field.get(self.context)

    def getImage(self):
        if not ILeadImageable.providedBy(self.context):
            return ''
        else:
            caption = self.getCaption()
            field = self.context.getField(IMAGE_FIELD_NAME)
            return field.tag(self.context, title=caption)


CLPATH = os.path.dirname(viewlets.__file__)


class LeadImageViewletFull(BaseViewlet):
    index = ViewPageTemplateFile('%s/leadimage-body.pt' % CLPATH)

    def render(self):
        slider_tool = getattr(self.request,'slider_tool',None)
        if not slider_tool:
            return super(LeadImageViewletFull, self).render()
        if not slider_tool.show_slider():
            return super(LeadImageViewletFull, self).render()

        field = self.context.getField('show_slider')
        if field and field.get(self.context) == SLIDER_MYSELF:
            return ''
        else:
            return super(LeadImageViewletFull, self).render()


class LeadImageViewletThumb(LeadImageViewletFull):
    index = ViewPageTemplateFile('%s/leadimage.pt' % CLPATH)
