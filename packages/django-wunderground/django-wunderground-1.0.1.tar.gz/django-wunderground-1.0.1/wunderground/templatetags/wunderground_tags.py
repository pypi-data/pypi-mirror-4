import urllib2
import json
from django import template
from django.conf import settings
from django.core.cache import cache
from classytags.core import Options
from classytags.arguments import Argument
from classytags.helpers import InclusionTag

register = template.Library()

class CurrentWeather(InclusionTag):
    '''
    Displays the current weather from wunderground.com

    By default uses the local_weather_tag template and the
    user's IP address to get the weather.

    You can set a location in the tag by forcing an IP address
    as a tag variable.

    {% current_weather %}
    or
    {% current_weather '04421' %}

    '''
    name = 'current_weather'
    options = Options(
         Argument('location', required=False, resolve=False),
    )
    template = "wunderground/local_weather_tag.html"

    def get_context(self, context, location):
        request = context['request']
        wunderground_key = settings.WUNDERGROUND_KEY
        if not location: # Fall back to looking up by ip address
            user_ip_address = request.META['REMOTE_ADDR']
            if user_ip_address == '127.0.0.1':
                user_ip_address = '169.244.235.50'
            weather_url = 'http://api.wunderground.com/api/%s/geolookup/conditions/q/autoip.json?geo_ip=%s' % (wunderground_key, user_ip_address)
            lookup_key = user_ip_address
            cache_key = 'wunderground_result_%s' % user_ip_address
        else: # Otherwise we want the weather from the location variable passed via the template tag
            weather_url = 'http://api.wunderground.com/api/%s/geolookup/conditions/q/%s.json' %(wunderground_key, location)
            lookup_key = location
            cache_key = 'wunderground_result_%s' % location
        # Check for a cache key so we don't hammer our Wunderground API account
        weather_info = cache.get(cache_key)
        if not weather_info:
            wunderground_response = urllib2.urlopen(weather_url)
            weather_info_json = wunderground_response.read()
            weather_info = json.loads(weather_info_json)
            cache.set(cache_key, weather_info, getattr(settings, 'WUNDERGROUND_CACHE_DURATION', 60*60))
        return {'lookup_key': lookup_key, 'weather_info': weather_info}

register.tag(CurrentWeather)