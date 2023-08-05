from tg import TGController
from tg import expose, flash, require, url, lurl, request, redirect, validate, config, abort
from tg.i18n import ugettext as _, lazy_ugettext as l_

from calendarevents import model
from calendarevents.model import DBSession

from tgext.pluggable import plug_redirect, plug_url
from tgext.datahelpers.validators import SQLAEntityConverter, validated_handler
from tgext.datahelpers.utils import fail_with, object_primary_key

from calendarevents.lib import get_form

try:
    from tg import predicates
except ImportError:
    from repoze.what import predicates

class EventController(TGController):
    @expose('calendarevents.templates.event.event')
    @validate(dict(event=SQLAEntityConverter(model.CalendarEvent)),
              error_handler=fail_with(404))
    def _default(self, event):
        return dict(event=event)

    @expose('calendarevents.templates.event.new')
    @require(predicates.in_group('calendarevents'))
    @validate(dict(cal=SQLAEntityConverter(model.Calendar)),
              error_handler=fail_with(403))
    def new(self, cal, **kw):
        return dict(cal=cal, form=get_form(), linkable_entities=cal.linkable_entities)

    @expose()
    @require(predicates.in_group('calendarevents'))
    @validate(get_form(), error_handler=validated_handler(new))
    def create(self, cal, **kw):
        new_event = model.CalendarEvent(calendar_id=cal.uid, name=kw['name'],
                                        summary=kw['summary'], datetime=kw['datetime'],
                                        location=kw['location'],
                                        linked_entity_type=cal.events_type,
                                        linked_entity_id=kw.get('linked_entity'))
        model.DBSession.add(new_event)
        flash(_('Event successfully added'))
        return plug_redirect('calendarevents', '/calendar/%s' % cal.uid)

    @expose()
    @require(predicates.in_group('calendarevents'))
    @validate(dict(event=SQLAEntityConverter(model.CalendarEvent)),
              error_handler=fail_with(404))
    def remove(self, event):
        referer = request.referer
        if referer and referer.endswith(plug_url('calendarevents', '/event/%s' % event.uid)):
            referer = plug_url('calendarevents', '/calendar/%s' % event.calendar_id)
        DBSession.delete(event)
        return redirect(referer)

    @expose('calendarevents.templates.event.edit')
    @require(predicates.in_group('calendarevents'))
    @validate(dict(event=SQLAEntityConverter(model.CalendarEvent)),
              error_handler=fail_with(404))
    def edit(self, event, **kw):
        cal = event.calendar
        return dict(cal=cal, event=event, linkable_entities=cal.linkable_entities, form=get_form())

    @expose()
    @require(predicates.in_group('calendarevents'))
    @validate(get_form(), error_handler=validated_handler(edit))
    def save(self, event, **kw):
        event = DBSession.query(model.CalendarEvent).get(event)
        if not event:
            abort(404)

        event.name=kw['name']
        event.summary=kw['summary']
        event.datetime=kw['datetime']
        event.location=kw['location']
        event.linked_entity_id=kw.get('linked_entity')

        flash(_('Event successfully modified'))
        return plug_redirect('calendarevents', '/event/%s' % event.uid)
