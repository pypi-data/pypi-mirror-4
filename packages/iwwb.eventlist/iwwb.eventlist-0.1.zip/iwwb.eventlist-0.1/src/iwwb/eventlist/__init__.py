# -*- coding: utf-8 -*-
"""Init and utils."""

from zope.i18nmessageid import MessageFactory
from zope.interface import Invalid

_ = MessageFactory('iwwb.eventlist')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""


def check_year_constraint(value):
    """Check that the year entered is not too low or too high."""
    if value.year < 1000 or value.year > 9999:
        raise Invalid(_(u"The year entered is not valid."))
    return True
