# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from datetime import date
from iwwb.eventlist import _
from iwwb.eventlist import check_year_constraint
from plone.theme.interfaces import IDefaultPloneLayer
from zope import schema
from zope.interface import Interface
from zope.interface import Invalid
from zope.interface import invariant


class IIWWBEventlistLayer(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer."""


class IIWWBSearcher(Interface):
    """Interface for the utility for handling communication with the IWWB web
    service.
    """


class IListEventsForm(Interface):
    """Field definition for List Events form."""
    query = schema.TextLine(
        title=_(u'Keywords'),
        description=_(u'Enter the search keywords. Examples: Seminar, Excel, '
            'Berlin, etc.'),
        required=False,
    )
    allwords = schema.Bool(
        title=_(u'All words'),
        description=_(u'If you tick this checkbox, only courses that match '
            'all keywords you enter will be displayed.'),
        required=False,
        default=True,
    )
    startDate = schema.Date(
        title=_(u'Course Start'),
        description=_(u'Select the date when the course should start'),
        required=False,
        default=date.today(),
        constraint=check_year_constraint,
    )
    county = schema.Choice(
        title=_(u'County'),
        description=_(u'By selecting a county you can limit the courses found '
            'to those that take place in that county.'),
        vocabulary='iwwb.eventlist.vocabularies.Counties',
        required=False,
        default='alle',
    )
    zipcity = schema.TextLine(
        title=_(u'Zip or City'),
        description=_(u'Enter the zip code or city.'),
        required=False,
    )
    type = schema.Choice(
        title=_(u'Event type'),
        description=_(u'Select the event type.'),
        vocabulary='iwwb.eventlist.vocabularies.EventTypes',
        required=False,
        default=0,
    )
    startTimeRequired = schema.Bool(
        title=_(u'Exclude events without dates'),
        description=_(u'If the event does not have the date information it '
                      'will not be listed.'),
        required=False,
        default=True,
    )

    @invariant
    def check_enough_data_provided(obj):
        """Check that the user has provided enough data to perform the query.
        """
        if not (obj.query or obj.zipcity or obj.startDate or obj.county):
            raise Invalid(_("You have to fill out at least one of required " \
                "fields: Keywords, Zip code or city, Event Start, County"))


IWWB_SEARCHABLE_FIELDS = (
    'query', 'county', 'zipcity', 'startDate', 'type', 'sort',)
