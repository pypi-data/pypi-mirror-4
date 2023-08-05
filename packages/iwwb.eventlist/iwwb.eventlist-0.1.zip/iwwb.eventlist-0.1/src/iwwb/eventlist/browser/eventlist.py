# -*- coding: utf-8 -*-
"""The List Events view."""

from datetime import date
from iwwb.eventlist import _
from iwwb.eventlist.interfaces import IIWWBSearcher
from iwwb.eventlist.interfaces import IListEventsForm
from iwwb.eventlist.interfaces import IWWB_SEARCHABLE_FIELDS
from iwwb.eventlist.vocabularies import COUNTIES
from plone.formwidget.datetime.z3cform import DateFieldWidget
from plone.z3cform.layout import FormWrapper
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form import field
from z3c.form import form
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

import logging

logger = logging.getLogger('iwwb.eventlist')


class ListEventsForm(form.Form):
    """The List Events search form based on z3c.form."""
    fields = field.Fields(IListEventsForm)
    fields['startDate'].widgetFactory = DateFieldWidget
    label = _(u"List Events")

    # don't try to read Plone root for form fields data, this is only mostly
    # usable for edit forms, where you have an actual context
    ignoreContext = True

    def updateWidgets(self):
        """Move fields' descriptions to title attrs of HTML form elements.

        This way fields' descriptions are displayed as tooltip text, making
        the UI a bit more classy.

        Also, set a custom widget template for the zipcity field that displays
        a link to the zip code picker.
        """
        super(ListEventsForm, self).updateWidgets()
        for name, widget in self.widgets.items():
            widget.title = widget.field.description

        self.widgets['zipcity'].template = ViewPageTemplateFile("zipcode.pt")

    @button.buttonAndHandler(_(u"List Events"))
    def list_events(self, action):
        """Submit button handler."""
        data, errors = self.extractData()

        if errors:
            self.status = self.formErrorsMessage
            return

    @button.buttonAndHandler(_(u"Reset"))
    def reset_form(self, action):
        """Cancel button handler."""
        url = self.request['URL']
        self.request.response.redirect(url)


class ListEventsView(FormWrapper):
    """A BrowserView to display the ListEventsForm along with its results."""
    index = ViewPageTemplateFile('eventlist.pt')
    form = ListEventsForm

    def update(self):
        """Main view method that handles rendering."""
        super(ListEventsView, self).update()

        if self.request.form.get('form.buttons.reset'):
            return self.index()

        # Hide the editable border and tabs
        self.request.set('disable_border', True)

        # Prepare display values for the template
        self.options = {
            'events': self.events(),
        }

    def events(self):
        """Get the events for the provided parameters using the IIWWBSearcher
        utility.
        """
        if self.form_instance.status:
            return []  # don't do anything if there were validation errors

        querydict = self._construct_query()
        results = []

        try:
            searcher = getUtility(IIWWBSearcher)
            if querydict:
                results = searcher.get_results(querydict)
        except:
            IStatusMessage(self.request).addStatusMessage(
                u"An error occured while fetching results. Please try again "
                "later.", type="error")
            logger.exception('Error fetching results')

        if not results:
            IStatusMessage(self.request).addStatusMessage(
                _('No events found.'), type="info")

        return results

    def event_type(self, type_id):
        """Get event type title for the provided event type id."""
        factory = getUtility(
            IVocabularyFactory,
            'iwwb.eventlist.vocabularies.EventTypes'
        )
        vocabulary = factory(self.context)

        return vocabulary.getTerm(type_id).title

    def _construct_query(self):
        """Parse the searchable fields from the form."""
        querydict = {}

        for field in IWWB_SEARCHABLE_FIELDS:
            if field == 'query':
                value = self.request.get('form.widgets.query')
                if not value:
                    continue
                search_all_words = self.request.get('form.widgets.allwords')
                if search_all_words:
                    querydict['bool'] = 'AND'
                querydict[field] = value
            elif field == 'startDate':
                year = self.request.form.get('form.widgets.%s-year' % field)
                month = self.request.form.get('form.widgets.%s-month' % field)
                day = self.request.form.get('form.widgets.%s-day' % field) or '1'
                if year and month:
                    event_date = date(int(year), int(month), int(day))
                    querydict['startDate'] = event_date.isoformat()
            elif field == 'zipcity':
                value = self.request.get('form.widgets.%s' % field)
                if not value:
                    continue
                if ',' in value:
                    zips = [x.strip() for x in value.split(',')
                        if x.strip().isdigit()]
                    if len(zips) > 0:
                        querydict['zip'] = ','.join(zips)
                elif value.strip().isdigit():
                    querydict['zip'] = int(value)
                else:
                    querydict['city'] = value
            elif field == 'county':
                value = self.request.get('form.widgets.%s' % field, '')
                # I have no idea why, but the FormWrapper thinks Choice fields
                # should have list-type values
                if type(value) == list:
                    value = value[0]
                if value and value not in ('alle', '--NOVALUE--'):
                    querydict['bundesland'] = COUNTIES[value]
            else:
                value = self.request.get('form.widgets.%s' % field)
                if not value:
                    continue
                # Some field values are lists, convert them to string
                if isinstance(value, (list, tuple)):
                    value = ','.join(value)
                querydict[field] = value

        termine = self.request.get('form.widgets.startTimeRequired')
        if termine:
            querydict['termine'] = 'yes'
        return querydict
