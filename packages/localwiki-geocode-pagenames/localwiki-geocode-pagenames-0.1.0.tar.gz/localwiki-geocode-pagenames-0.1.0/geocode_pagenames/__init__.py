#!/usr/bin/env python

from urlparse import urljoin
import slumber
from geopy import geocoders
import re

from utils import all

SITE_URL = ''
API_KEY = ''
USERNAME = ''
GEOCODE_SUFFIX = ''


def should_geocode(pagename):
    # To limit the geocode usage, and limit the possibility of crummy
    # data, we only geocode pages whos pagename looks like an address.
    if pagename.endswith('/Talk'):
        return False
    if re.match(r'[0-9]+\s[A-Z].*', pagename):
        # Prompt for confirmation.
        answer = raw_input("%s. Y/n? " % pagename)
        return (answer.strip().lower() == 'y' or not answer.strip())


def add_map(page, lat, lng, api):
    map = {
        'page': page['resource_uri'],
        'points': {'type': 'MultiPoint', 'coordinates': [[lng, lat]]}
    }
    # Create new map!
    api.map.post(map, api_key=API_KEY, username=USERNAME)
    print 'Created map for %s' % page['name']


def pagename_for_geocoding(pagename):
    if ',' in pagename:
        # Assume they've specified the city or something if they've put in a
        # comma
        return pagename
    # otherwise, let's add our suffix on.
    return pagename + ',' + GEOCODE_SUFFIX


def run():
    global SITE_URL, API_KEY, USERNAME, GEOCODE_SUFFIX

    SITE_URL = raw_input("Enter URL of LocalWiki instance: ").strip()
    API_KEY = raw_input("Enter API key: ").strip()
    USERNAME = raw_input("Enter API username: ").strip()
    GEOCODE_SUFFIX = raw_input("""What suffix should we use for geocoding?'
E.g. "San Francisco, California" or "Detroit, Michigan": """)

    api = slumber.API(urljoin(SITE_URL, '/api/'))
    geocoder = geocoders.Google()

    for page in all(api.page.get):
        # Does the page already have a map?
        has_map = api.map.get(page__name__iexact=page['name'])['objects']
        if has_map:
            # skip it - map is likely correct
            continue

        if should_geocode(page['name']):
            try:
                place, (lat, lng) = geocoder.geocode(
                    pagename_for_geocoding(page['name']))
            except:
                continue
            add_map(page, lat, lng, api)
