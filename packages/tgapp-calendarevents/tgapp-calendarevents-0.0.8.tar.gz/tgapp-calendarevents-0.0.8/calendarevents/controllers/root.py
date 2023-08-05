# -*- coding: utf-8 -*-
"""Main Controller"""
try:
    from tg import predicates
except ImportError:
    from repoze.what import predicates

from tg import TGController
from tg import expose, flash, require, url, lurl, request, redirect, validate
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tgext.datahelpers.utils import fail_with
from tgext.datahelpers.validators import SQLAEntityConverter

from calendarevents import model
from calendarevents.model import DBSession

from tgext.pluggable import plug_redirect

from .calendar import CalendarController
from .event import EventController

class RootController(TGController):
    calendar = CalendarController()
    event = EventController()

    @require(predicates.in_group('calendarevents'))
    @expose('calendarevents.templates.index')
    def index(self):
        return plug_redirect('calendarevents', '/calendar/list')
