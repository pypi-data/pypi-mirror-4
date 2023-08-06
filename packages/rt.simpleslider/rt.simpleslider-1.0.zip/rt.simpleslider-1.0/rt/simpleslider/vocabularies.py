# -*- coding: utf-8 -*-
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.interface import implements
from rt.simpleslider import MessageFactory as _


class PlainListVocabulary(object):
    def __call__(self, context):
        simple_terms = []
        for t in self.terms:
            token, title = t
            simple_terms.append(SimpleTerm(token=token, value=token, title=title))
        return SimpleVocabulary(simple_terms)


BLACKLIST_URLS = [r'edit', r'plone_control_panel', 'manage', 'sharing',
                   'portlets', 'search', 'portal_factory']
SLIDER_PARENT = 'parent'
SLIDER_MYSELF = 'myself'
SLIDER_NO = 'no'
SLIDER_YES = 'yes'


class SimpleSliderDisplayType(PlainListVocabulary):
    implements(IVocabularyFactory)
    terms = [
            (SLIDER_PARENT,  _(u'parent_inherit', default=u'Inherit configuration from parent')),
            (SLIDER_MYSELF,  _(u'use_myself',     default=u'Use myself as a source')),
            (SLIDER_NO,      _(u'no_dispaly',     default=u'Do not display')),
            (SLIDER_YES,     _(u'yes_display',    default=u'Display')),
            ]

SimpleSliderDisplayVocabularyFactory = SimpleSliderDisplayType()
