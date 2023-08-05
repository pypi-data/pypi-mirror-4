from tg import expose
from calendarevents import model
from calendarevents.model import DBSession


@expose('calendarevents.templates.partials.event')
def event(event):
    return dict(calendar_event=event)