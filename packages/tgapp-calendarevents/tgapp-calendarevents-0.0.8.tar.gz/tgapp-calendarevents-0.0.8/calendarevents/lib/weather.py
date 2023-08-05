import tg
from tg.i18n import ugettext as _
from datetime import datetime
import json
from urllib import urlopen, urlencode
from contextlib import closing
from tgext.datahelpers.caching import entitycached, CacheKey

import urllib2
from xml.dom import minidom
from urllib import quote

YAHOO_WEATHER_URL    = 'http://xml.weather.yahoo.com/forecastrss?w=%s&u=%s'
YAHOO_WEATHER_NS     = 'http://xml.weather.yahoo.com/ns/rss/1.0'

def get_weather_from_yahoo(location_id, units = 'metric'):
    location_id = quote(location_id)
    if units == 'metric':
        unit = 'c'
    else:
        unit = 'f'
    url = YAHOO_WEATHER_URL % (location_id, unit)
    handler = urllib2.urlopen(url)
    dom = minidom.parse(handler)    
    handler.close()
        
    weather_data = {}
    weather_data['title'] = dom.getElementsByTagName('title')[0].firstChild.data
    weather_data['link'] = dom.getElementsByTagName('link')[0].firstChild.data

    ns_data_structure = { 
        'location': ('city', 'region', 'country'),
        'units': ('temperature', 'distance', 'pressure', 'speed'),
        'wind': ('chill', 'direction', 'speed'),
        'atmosphere': ('humidity', 'visibility', 'pressure', 'rising'),
        'astronomy': ('sunrise', 'sunset'),
        'condition': ('text', 'code', 'temp', 'date')
    }       
    
    for (tag, attrs) in ns_data_structure.iteritems():
        element = dom.getElementsByTagNameNS(YAHOO_WEATHER_NS, tag)[0]
        parsed_attrs = {}
        for attr in attrs:
            parsed_attrs[attr] = element.getAttribute(attr)
        weather_data[tag] = parsed_attrs
    weather_data['condition']['icon'] = 'http://l.yimg.com/a/i/us/we/52/%s.gif' % (weather_data['condition']['code'])

    weather_data['geo'] = {}
    weather_data['geo']['lat'] = dom.getElementsByTagName('geo:lat')[0].firstChild.data
    weather_data['geo']['long'] = dom.getElementsByTagName('geo:long')[0].firstChild.data

    weather_data['condition']['title'] = dom.getElementsByTagName('item')[0].getElementsByTagName('title')[0].firstChild.data
    weather_data['html_description'] = dom.getElementsByTagName('item')[0].getElementsByTagName('description')[0].firstChild.data
    
    forecasts = []
    for forecast in dom.getElementsByTagNameNS(YAHOO_WEATHER_NS, 'forecast'):
        parsed_attrs = {}
        for attr in ('date', 'low', 'high', 'text', 'code'):
            parsed_attrs[attr] = forecast.getAttribute(attr)
        parsed_attrs['icon'] = 'http://l.yimg.com/a/i/us/we/52/%s.gif' % (parsed_attrs['code'])
        parsed_attrs['temp_medium'] = int(parsed_attrs['high'])-((int(parsed_attrs['high'])-int(parsed_attrs['low']))/3)
        forecasts.append(parsed_attrs)
    weather_data['forecasts'] = forecasts
    
    dom.unlink()

    return weather_data


def get_weather_code_for_location(location):
    url = 'http://query.yahooapis.com/v1/public/yql'
    data = {'format':'json',
            'q':'select * from geo.places where text="%s"' % location}

    with closing(urlopen(url, urlencode(data))) as fbanswer:
        j = json.loads(fbanswer.read())
        return j["query"]["results"]["place"][0]["woeid"]

def get_weather_for_date(location, date):
    @entitycached('cache_key', expire=2*3600)
    def get_cached_weater(cache_key, location, date):
        weather = {}

        today_to_event = (date - datetime.now()).days
        if today_to_event >= -1:
            location = get_weather_code_for_location(location)
            if today_to_event < 1:
                weather = get_weather_from_yahoo(location, 'metric')
                weather = weather['condition']
            elif today_to_event < 5:
                weather = get_weather_from_yahoo(location, 'metric')
                weather = weather['forecasts'][today_to_event]
        if not weather:
            weather = {'icon':tg.url('/_pluggable/calendarevents/images/noweather.png'),
                       'temp':'', 'low':'', 'high':''}

        return weather

    try:
        return get_cached_weater(CacheKey('%s-%s' % (location, date)), location, date)
    except:
        return {'icon':tg.url('/_pluggable/calendarevents/images/noweather.png'),
                'temp':'', 'low':'', 'high':''}
