from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Unicode, Integer, DateTime
from sqlalchemy.orm import backref, relation

from calendarevents.model import DeclarativeBase
from calendarevents.lib.event_type import lookup_event_type
from calendarevents.lib.weather import get_weather_for_date

from tg.decorators import cached_property
import re, cgi, fileinput

class Calendar(DeclarativeBase):
    __tablename__ = 'calendarevents_calendar'

    uid = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(64))
    events_type = Column(Unicode(64), index=True)

    @property
    def events_type_info(self):
        return lookup_event_type(self.events_type)

    @property
    def linkable_entities(self):
        event_type = self.events_type_info
        if not event_type:
            return []
        return event_type.get_linkable_entities(self)

class CalendarEvent(DeclarativeBase):
    __tablename__ = 'calendarevents_event'

    uid = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    summary = Column(Unicode(1024))
    datetime = Column(DateTime, nullable=False, index=True)
    location = Column(Unicode(255), nullable=False)

    calendar_id = Column(Integer, ForeignKey(Calendar.uid), nullable=False, index=True)
    calendar = relation(Calendar, backref=backref('events', order_by='CalendarEvent.datetime.desc()',
                                                            cascade='all, delete-orphan'))

    linked_entity_id = Column(Integer, nullable=False, index=True)
    linked_entity_type = Column(Unicode(255), nullable=False, index=True)

    @property
    def event_type(self):
        return lookup_event_type(self.linked_entity_type)

    @property
    def linked_entity_url(self):
        return self.event_type.get_linked_entity_url(self)

    @property
    def linked_entity_info(self):
        return self.event_type.get_linked_entity_info(self)

    @cached_property
    def weather(self):
        return get_weather_for_date(self.location, self.datetime)
