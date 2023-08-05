#!/usr/bin/env python
'''
metoffer

Wrapper for MetOffice API (http://partner.metoffice.gov.uk).

The UK's Met Office collects a great deal of meteorological
information which it makes available through its website.
It also offers forecast information.  These data are available
through their API to anyone who has signed up to receive a
'key'.   metoffer offers the ability to retrieve and browse
this data in a handy Python format.

                        *    *    *

Copyright 2012 Stephen B. Murray

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>
'''
__version__ = '0.1'
__author__ = 'Stephen B. Murray <sbm199 WITH gmail STOP com>'

import datetime
import json
import urllib.request

HOST_NAME = 'http://partner.metoffice.gov.uk'
DATA_VISIBILITY = 'public'
DATA_CATEGORY = 'val'   # This may broaden in future.
RESOURCE_TYPE = 'all'   # Has the same caveat as DATA_CATEGORY
DATA_FORMAT = 'json'    # Easier to work with than the XML alternative

# Some Met Office constants to aid interpretation of data
WEATHER_TYPES = {
                 'NA': 'Not available',
                 0:    'Clear sky',
                 1:    'Sunny',
                 2:    'Partly cloudy (night)',
                 3:    'Sunny intervals',
                 4:    'Dust',
                 5:    'Mist',
                 6:    'Fog',
                 7:    'Medium-level cloud',
                 8:    'Low-level cloud',
                 9:    'Light rain shower (night)',
                 10:   'Light rain shower (day)',
                 11:   'Drizzle',
                 12:   'Light rain',
                 13:   'Heavy rain shower (night)',
                 14:   'Heavy rain shower (day)',
                 15:   'Heavy rain',
                 16:   'Sleet shower (night)',
                 17:   'Sleet shower (day)',
                 18:   'Sleet',
                 19:   'Hail shower (night)',
                 20:   'Hail shower (day)',
                 21:   'Hail',
                 22:   'Light snow shower (night)',
                 23:   'Light snow shower (day)',
                 24:   'Light snow',
                 25:   'Heavy snow shower (night)',
                 26:   'Heavy snow shower (day)',
                 27:   'Heavy snow',
                 28:   'Thundery shower (night)',
                 29:   'Thundery shower (day)',
                 30:   'Thunder storm',
                 31:   'Tropical storm',
                 33:   'Haze'
                 }
VISIBILITY = {
              'UN': 'Unknown',
              'VP': 'Very poor - Less than 1 km',
              'PO': 'Poor - Between 1-4 km',
              'MO': 'Moderate - Between 4-10 km',
              'GO': 'Good - Between 10-20 km',
              'VG': 'Very good - Between 20-40 km',
              'EX': 'Excellent - More than 40 km'
              }

class MetOffer():
    def __init__(self, key):
        '''
          Args:
            key:
              API key obtained from Met Office.  This is necessary
              to use the API.  Keys can be obtained (at time of
              writing) by signing up online.
        '''
        self.key = key

    def _query(self,
               observations=True,
               location='sitelist',
               lat=None,
               lon=None,
               temporal_resolution='hourly'):
        '''Make request of MetOffice server using REST URL.'''
        # Request observations or forecasts:
        resource_category = 'wxobs' if observations == True else 'wxfcs'
        rest_url = '/'.join([HOST_NAME,
                             DATA_VISIBILITY,
                             DATA_CATEGORY,
                             resource_category,
                             RESOURCE_TYPE,
                             DATA_FORMAT,
                             location])
        query_string = '?' + '&'.join(['res=' + temporal_resolution if observations == False else 'hourly',
                                       'lat=' + lat if lat is not None else '',
                                       'lon=' + lon if lon is not None else '',
                                       'key=' + self.key])
        url = rest_url + query_string
        page = urllib.request.urlopen(url)
        pg = page.read()
        return json.loads(pg.decode(errors='replace'))
    
    def get_weather(self, observations, id=None, lat=None, lon=None, temporal_resolution=None):
        '''Get weather data from Met Office server.
        
        Args:
          observations:
            Bool.  True to get observations, False to get forecasts.
          id:
            String.  A numeric location ID.  For forecast data this
            can be any ID from the Complete list of locations.  For
            observed data this can be any ID from the List of
            locations with observations.  In each case the forecast
            or observation for the specified.
          lat:
            Float.  Latitude closest to which the observation or
            forecast should be returned.  Used when the specific
            location ID is not known.  Requires lon be set.
          lon:
            Float.  Longitude.  Works in same fashion as lat above.
            Requires lat to be set.
          temporal_resolution:
            String.  The interval that should be used for returned
            data.  There are several options:
            
            For forecast data:
              '3hourly' returns three-hourly results
              'daily' returns daily results
            
            For observed data, temporal_resolution is always
            'hourly'.  It is required for forecast data.
        Returns:
          Instance of Weather class.'''
        returned_object = self._query(observations=observations,
                                      location=id if id is not None else 'nearestlatlon',
                                      lat=str(lat) if lat is not None else '',
                                      lon=str(lon) if lon is not None else '', 
                                      temporal_resolution=temporal_resolution if observations == False else 'hourly')
        id = returned_object['SiteRep']['DV']['Location']['@i']
        name = returned_object['SiteRep']['DV']['Location']['@name']
        country = returned_object['SiteRep']['DV']['Location']['@country']
        continent = returned_object['SiteRep']['DV']['Location']['@continent']
        lat = returned_object['SiteRep']['DV']['Location']['@lat']
        lon = returned_object['SiteRep']['DV']['Location']['@lon']
        def _weather_dict_gen(period):
            name_map = {}
            for i in returned_object['SiteRep']['Wx']['Param']:
                name_map[i['@name']] = {'text': i['$'], 'units': i['@units']}
            for i in period:
                y, m, d = i['@val'][:-1].split('-')
                date = datetime.datetime(int(y), int(m), int(d))
                for rep in i['Rep']:
                    try:
                        dt = (date + datetime.timedelta(seconds=int(rep['$']) * 60), '') # dt always a tuple
                    except(ValueError):
                        dt = (date, rep['$']) # Used for 'daily' temporal_resolution
                    del rep['$']
                    weather = {}
                    weather['timestamp'] = dt
                    for n in rep:
                        try:
                            # -99 is used by the Met Office as a value where
                            # no data is held.
                            weather[name_map[n[1:]]['text']] = (int(rep[n]) if rep[n]!= '-99' else None,
                                                                name_map[n[1:]]['units'])
                        except(ValueError):
                            try:
                                weather[name_map[n[1:]]['text']] = (float(rep[n]), name_map[n[1:]]['units'])
                            except(ValueError):
                                weather[name_map[n[1:]]['text']] = (rep[n], name_map[n[1:]]['units'])
                    yield weather
        data = []
        for weather in _weather_dict_gen(returned_object['SiteRep']['DV']['Location']['Period']):
            data.append(weather)
        return Weather(id, name, country, continent, lat, lon, temporal_resolution, observations, data)

class Weather():
    '''A hold-all for returned weather data, including associated metadata.'''
    def __init__(self, id, name, country, continent, lat, lon,
                 temporal_resolution, observations, data):
        self.id = id
        self.name = name
        self.country = country
        self.continent = continent
        self.lat = float(lat)
        self.lon = float(lon)
        self.temporal_resolution = temporal_resolution
        self.observations = observations # True for observations, False for forecasts
        self.data = data