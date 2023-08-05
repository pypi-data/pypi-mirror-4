# -*- coding: utf-8 -*-
"""Definitions of vocabularies."""

from iwwb.eventlist import _
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


COUNTIES = dict(
    alle=_(u'no_selection', default=u'No selection'),
    baw=u'Baden-Württemberg',
    bay=u'Bayern',
    bln=u'Berlin',
    bra=u'Brandenburg',
    bre=u'Bremen',
    hh=u'Hamburg',
    hes=u'Hessen',
    mvp=u'Mecklenburg-Vorpommern',
    nds=u'Niedersachsen',
    nrw=u'Nordrhein-Westfalen',
    rpf=u'Rheinland-Pfalz',
    saa=u'Saarland',
    sac=u'Sachsen',
    san=u'Sachsen-Anhalt',
    slh=u'Schleswig-Holstein',
    thu=u'Thüringen',
)

class CountiesVocabulary(object):
    """ Counties """
    implements(IVocabularyFactory)

    def __call__(self, context):
        """Build a vocabulary of counties.
           zope.schema.vocabulary is really stupid, because it needs a string
           as token, and can't work with unicode (though technically it could).
           Since WSDL's GetFullResult takes a county's full name, and some of
           them contain umlauts, we need to keep a mapping of abbr to name for
           the counties, and make the replacement when we create the query.
        """
        items = list()
        keys = COUNTIES.keys()
        keys.sort()
        for key in keys:
            items.append(SimpleTerm(key, key, COUNTIES[key]))

        return SimpleVocabulary(items)

CountiesVocabularyFactory = CountiesVocabulary()


class EventTypesVocabulary(object):
    """Vocabulary factory for event types."""
    implements(IVocabularyFactory)

    def __call__(self, context):
        """Build a vocabulary of event types.
        """
        items = [
            SimpleTerm(0, 0, _(u'All Events')),
            SimpleTerm(1, 1, _(u'Seminar')),
            SimpleTerm(2, 2, _(u'Distance Learning')),
            SimpleTerm(3, 3, _(u'CBT/WBT/E-Learning')),
        ]

        return SimpleVocabulary(items)

EventTypesVocabularyFactory = EventTypesVocabulary()


class SortOptionsVocabulary(object):
    """Vocabulary factory for sort options."""
    implements(IVocabularyFactory)

    def __call__(self, context):
        """Build a vocabulary of sort options.
        """
        items = [
            SimpleTerm(
                'Treffergenauigkeit',
                'Treffergenauigkeit',
                _(u'Treffergenauigkeit')
            ),
            SimpleTerm('city', 'city', _(u'Ort')),
            SimpleTerm('zip', 'zip', _(u'PLZ')),
            SimpleTerm('startTime', 'startTime', _(u'Datum')),
        ]

        return SimpleVocabulary(items)

SortOptionsVocabularyFactory = SortOptionsVocabulary()
