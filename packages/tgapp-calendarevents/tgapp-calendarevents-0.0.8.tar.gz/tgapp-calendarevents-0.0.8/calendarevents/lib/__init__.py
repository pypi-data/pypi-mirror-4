# -*- coding: utf-8 -*-
from tg import config
import forms

def get_form():
    calendar_form = config.get('_calendarevents.form_instance')
    if not calendar_form:
        form_path = config.get('_calendarevents.form', 'calendarevents.lib.forms.NewEventForm')
        module, form_name = form_path.rsplit('.', 1)
        module = __import__(module, fromlist=form_name)
        form_class = getattr(module, form_name)
        calendar_form = config['_calendarevents.form_instance'] = form_class()
    return calendar_form
