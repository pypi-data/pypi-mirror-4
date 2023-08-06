# -*- coding: utf-8 -*-

import re
from Acquisition import aq_chain
from zope.component import adapts
from zope.interface import Interface, implements
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.publisher.interfaces.browser import IBrowserView
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.memoize.view import memoize

from rt.simpleslider.interfaces import ISliderUtils
from rt.simpleslider.vocabularies import SLIDER_PARENT,\
    BLACKLIST_URLS, SLIDER_NO, SLIDER_YES, SLIDER_MYSELF


class SliderUtils(object):

    implements(ISliderUtils)
    adapts(IBrowserView, Interface, IDefaultBrowserLayer)

    def __init__(self, view, context, request):
        self.request = request
        self.context = context
        self.view = view
        self.chain = aq_chain(self.context)

    @memoize
    def show_slider(self):
        """ Return True if we have a slider_source """
        if hasattr(self.request,'error_type'):
            #we have an error - stop
            return False

        # First check if context allow to show the map:
        if not self._check_context():
            return False

        # then if we have a source for map
        if not self._check_source():
            return False
        # finally if request is not in blacklist
        if not self._check_urls():
            return False

        return True

    def _check_urls(self):
        """ Check if current request url is valid to display map """
        for step in self.request.steps:
            for url in BLACKLIST_URLS:
                if re.compile(url).search(step):
                    return False
        return True

    def _check_source(self):
        """
        Check if for current context we have slider source.
        """
        if not hasattr(self.request,'slider_source'):
            return False
        elif not self.request.slider_source:
            return False
        return True

    def _check_context(self):
        """
        check if we should show slider in current context
        """
        for obj in self.chain:

            if INavigationRoot.providedBy(obj): #Plone site return default view
                default = obj.getDefaultPage()
                if default:
                    obj = obj[default]

            extended = getattr(obj, 'getField', None)
            if extended:
                field = extended('show_slider')
                if field:
                    show = field.getAccessor(obj)()
                    if show == SLIDER_PARENT: #skip context go up
                        continue
                    elif show == SLIDER_NO:
                        return False
                    elif show == SLIDER_YES:
                        return True
                    elif show == SLIDER_MYSELF:
                        return True
        return False

    @memoize
    def slider_source(self):
        """ Return source object for slider. If nothing is found
        return None """
        for obj in self.chain:

            if INavigationRoot.providedBy(obj): #Plone site return default view
                default = obj.getDefaultPage()
                if default:
                    obj = obj[default]

            extended = getattr(obj, 'getField', None)
            if extended:
                source_field = extended('slider_source')
                show_field = extended('show_slider')
                if source_field or show_field:
                    source = source_field.getAccessor(obj)()
                    show = show_field.getAccessor(obj)()
                    if show == SLIDER_MYSELF: #if myself - display directly
                        return obj
                    if source:
                        return source
