import tg

class EventType(object):
    name = 'Unknown'

    def get_linkable_entities(self, calendar):
        raise NotImplementedError

    def get_linked_entity_url(self, event):
        return NotImplementedError

    def get_linked_entity_info(self, event):
        return NotImplementedError

def lookup_event_type(name):
    event_types = tg.config['_calendarevents']['event_types']
    for et in event_types:
        if et.name == name:
            return et
    return None
