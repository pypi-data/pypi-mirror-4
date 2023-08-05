# -*- coding: utf-8 -*-
"""The tgapp-calendarevents package"""

import tg
from calendarevents.lib.event_type import EventType

def plugme(app_config, options):
    tg.config['_calendarevents'] = options
    return dict(appid='calendarevents', global_helpers=False)

