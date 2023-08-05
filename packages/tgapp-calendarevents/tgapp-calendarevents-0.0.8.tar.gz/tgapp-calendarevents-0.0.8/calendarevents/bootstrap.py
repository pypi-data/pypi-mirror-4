# -*- coding: utf-8 -*-
"""Setup the calendarevents application"""

from calendarevents import model
from tgext.pluggable import app_model

def bootstrap(command, conf, vars):
    print 'Bootstrapping calendarevents...'

    g = app_model.Group(group_name='calendarevents', display_name='Calendar Events manager')
    model.DBSession.add(g)
    model.DBSession.flush()

    u1 = model.DBSession.query(app_model.User).filter_by(user_name='manager').first()
    if u1:
        g.users.append(u1)

    model.DBSession.flush()

