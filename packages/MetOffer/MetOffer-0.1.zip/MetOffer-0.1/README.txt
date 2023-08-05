================
metoffer v.0.1.0
================

metoffer is a simple wrapper for the API provided by the British
`Met Office <http://www.metoffice.gov.uk>`_. It can be used to retrieve
weather observations and forecasts.

Weather Observations
--------------------

So. Let's say we're keen to find out the latest weather conditions at
Heathrow. First thing to do is use the key we received by registering as a
developer with `metoffice datapoint <http://www.metoffice.gov.uk/public/ddc/>`_
(at time of writing, it's still in Beta)::

    >>> import metoffer
    >>> M = metoffer.MetOffer('xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx')

Rather than knowing all the unique identifiers the Met Office has assigned to
its many weather stations, we can simply find the nearest to a given
co-ordinate::

    >>> heathrow_obs = M.get_weather(observations=True, lat=51.479,
    ...                              lon=-0.449)

Now we should have some data to play around with. Hopefully there'll be a
little useful metadata about what we just pulled::

    >>> heathrow_obs.name
    'HEATHROW'
    >>> heathrow_obs.id
    '3772'
    >>> heathrow_obs.country
    ''
    >>> heathrow_obs.continent
    'EUROPE'
    >>> heathrow_obs.lat
    51.48
    >>> heathrow_obs.lon
    -0.45

Nothing returned for heathrow_obs.country, but otherwise not bad. Now let's
take a look at the actual data::

    >>> heathrow_obs.data
    [{'Wind Speed': (13, 'mph'), 'timestamp': (datetime.datetime(2012, 7, 22, 18, 0)
    , ''), 'Wind Direction': ('SW', 'compass'), 'Visibility': (30000, 'm'), 'Pressur
    e': (1025, 'hPa'), 'Wind Gust': (None, 'mph'), 'Weather Type': (1, ''), 'Tempera
    ture': (21.6, 'C')}, {'Wind Speed': (11, 'mph'), 'timestamp': (datetime.datetime
    (2012, 7, 22, 19, 0), ''), 'Wind Direction': ('SSW', 'compass'), 'Visibility': (
    30000, 'm'), 'Pressure': (1025, 'hPa'), 'Wind Gust': (None, 'mph'), 'Weather Typ
    e': (1, ''), 'Temperature': (21.1, 'C')}, {'Wind Speed': (11, 'mph'), 'timestamp
    ': (datetime.datetime(2012, 7, 22, 20, 0), ''), 'Wind Direction': ('SSW', 'compa
    ss'), 'Visibility': (30000, 'm'), 'Pressure': (1025, 'hPa'), 'Wind Gust': (None,
     'mph'), 'Weather Type': (1, ''), 'Temperature': (19.8, 'C')}, {'Wind Speed': (1

    [...]

The structure of the data is fairly easy to understand. It is a list
containing a dict for each point in time observations were taken (for
observations this is always hourly). Each key of these dicts, except
'timestamp', is a category of weather observation with a tuple usually
representing an observation/unit pair. 'timestamp' is, of course, the time at
which these observations were recorded, made available as a datetime.datetime
object. Here it is in pretty print::

    [
       {
          'Wind Speed':     (13, 'mph'),
          'timestamp':      (datetime.datetime(2012, 7, 22, 18, 0), ''),
          'Wind Direction': ('SW', 'compass'),
          'Visibility':     (30000, 'm'),
          'Pressure':       (1025, 'hPa'),
          'Wind Gust':      (None, 'mph'),
          'Weather Type':   (1, ''),
          'Temperature':    (21.6, 'C')
          },
       {
          'Wind Speed':     (11, 'mph'),
          'timestamp':      (datetime.datetime(2012, 7, 22, 19, 0), ''),
          'Wind Direction': ('SSW', 'compass'),
          'Visibility':     (30000, 'm'),
          'Pressure':       (1025, 'hPa'),
          'Wind Gust':      (None, 'mph'),
          'Weather Type':   (1, ''),
          'Temperature':    (21.1, 'C')
          },
       {
          'Wind Speed':     (11, 'mph'),
          'timestamp':      (datetime.datetime(2012, 7, 22, 20, 0), ''),
          'Wind Direction': ('SSW', 'compass'),
          'Visibility':     (30000, 'm'),
          'Pressure':       (1025, 'hPa'),
          'Wind Gust':      (None, 'mph'),
          'Weather Type':   (1, ''),
          'Temperature':    (19.8, 'C')
          },
       {
          'Wind Speed':     (1

    [...]

A couple of points to note:

* All dict keys have a tuple, even where there is no obvious need, such as
  with 'timestamp' and 'Weather Type'. This is a feature.
* When the Met Office does not have a recorded observation against a category,
  metoffer will return None.

The 'Weather Type' is in Met Office code. Let's unravel it::

    >>> weather_type = heathrow_obs.data[0]['Weather Type'][0]
    >>> metoffer.WEATHER_TYPES[weather_type]
    'Sunny'

So far, so good. But the Met Office also makes...

Weather Forecasts
-----------------

This time, let's use the Met Office ID for Heathrow to retrieve the data we
desire, and as it's a forecast we're after and not an observation, we must
specify a 'temporal_resolution' -- the intervals at which we would like our
weather predictions. Let's go for an interval of three hours::

    >>> heathrow_forecast = M.get_weather(observations=False,
    ...                                   id=heathrow_obs.id,
    ...                                   temporal_resolution='3hourly')

Again, we have access to some metadata::

    >>> heathrow_forecast.name
    'HEATHROW'
    >>> heathrow_forecast.country
    'ENGLAND'
    >>> heathrow_forecast.continent
    'EUROPE'
    >>> heathrow_forecast.lat
    51.48
    >>> heathrow_forecast.lon
    -0.45

And again, we have lots of data::

    >>> heathrow_forecast.data
    [{'Wind Speed': (11, 'mph'), 'timestamp': (datetime.datetime(2012, 7, 23, 18, 0)
    , ''), 'Wind Direction': ('SSW', 'compass'), 'Visibility': ('VG', ''), 'Max Uv I
    ndex': (1, ''), 'Wind Gust': (17, 'mph'), 'Precipitation Probability': (5, '%'),
     'Weather Type': (1, ''), 'Screen Relative Humidity': (40, '%'), 'Feels Like Tem
    perature': (24, 'C'), 'Temperature': (25, 'C')}, {'Wind Speed': (9, 'mph'), 'tim
    estamp': (datetime.datetime(2012, 7, 23, 21, 0), ''), 'Wind Direction': ('SSW',
    'compass'), 'Visibility': ('VG', ''), 'Max Uv Index': (0, ''), 'Wind Gust': (15,

    [...]

The data structure is very similar to that for observations. There are a few
more categories, and 'timestamp' gives you a time in the future that the
stated conditions are thought will occur. The pretty print::

    [
       {
          'Wind Speed':                (11, 'mph'),
          'timestamp':                 (datetime.datetime(2012, 7, 23, 18, 0), ''),
          'Wind Direction':            ('SSW', 'compass'),
          'Visibility':                ('VG', ''),
          'Max Uv Index':              (1, ''),
          'Wind Gust':                 (17, 'mph'),
          'Precipitation Probability': (5, '%'),
          'Weather Type':              (1, ''),
          'Screen Relative Humidity':  (40, '%'),
          'Feels Like Temperature':    (24, 'C'),
          'Temperature':               (25, 'C')
          },
       {
          'Wind Speed':                (9, 'mph'),
          'timestamp':                 (datetime.datetime(2012, 7, 23, 21, 0), ''),
          'Wind Direction':            ('SSW', 'compass'),
          'Visibility':                ('VG', ''),
          'Max Uv Index':              (0, ''),
          'Wind Gust':                 (15,

    [...]

You'll notice that 'Visibility' is in code like 'Weather Type', and like the
latter, we can decode it::

    >>> visibility = heathrow_forecast.data[0]['Visibility'][0]
    >>> metoffer.VISIBILITY[visibility]
    'Very good - Between 20-40 km'

Sometimes we need something a little less fine grained. Generally, we more
likely to ask what the day's overrall weather will be like. For this, we
simply adjust the 'temporal_resolution'::

    >>> daily_forecast = M.get_weather(observations=False, id=heathrow_obs.id,
    ...                                temporal_resolution='daily')

We get all the familiar metadata and data structure, but, once again, there
are slight differences. Let's pretty print again::

    [
       {
          'Screen Relative Humidity Noon':        (37, '%'),
          'Wind Speed':                           (7, 'mph'),
          'Weather Type':                         (1, ''),
          'timestamp':                            (datetime.datetime(2012, 7, 24, 0, 0), 'Day'),
          'Wind Direction':                       ('S', 'compass'),
          'Visibility':                           ('VG', ''),
          'Max UV Index':                         (5, ''),
          'Day Maximum Temperature':              (28, 'C'),
          'Precipitation Probability Day':        (5, '%'),
          'Wind Gust Noon':                       (15, 'mph'),
          'Feels Like Day Maximum Temperature':   (28, 'C')
          },
       {
          'Wind Speed':                           (5, 'mph'),
          'Wind Gust Midnight':                   (8, 'mph'),
          'timestamp':                            (datetime.datetime(2012, 7, 24, 0, 0), 'Night'),
          'Wind Direction':                       ('SW', 'compass'),
          'Visibility':                           ('GO', ''),
          'Feels Like Night Minimum Temperature': (18, 'C'),
          'Night Minimum Temperature':            (16, 'C'),
          'Weather Type':                         (0, ''),
          'Screen Relative Humidity Midnight':    (73, '%'),
          'Precipitation Probability Night':      (5, '%')
          },
       {
          'Screen Relative Humidity Noon':        (39, '%'),
          'Wind Speed':                           (6, 'mph'),
          'Weather Type':                         (1,

    [...]

You'll notice that the hours and mintutes of the 'timestamp' datetime.datetime
object are superfluous. In fact, it would be misleading to follow them. 
Rather, this time there is a sensible entry in the second part of the tuple.
This alternates between 'Day' and 'Night' with each successive dict. The
categories are often specific to the time of day. This is how the API provides
it. Take note; it may catch you out.

Bugs
----

I don't know if this package will be maintained. I wrote it as a quick one-off
and hope it can be of some use to someone else. That's all.

That said, I can be contacted here: Stephen B. Murray <sbm199 WITH gmail STOP com>

Legal
-----

Copyright 2012 Stephen B. Murray

Distributed under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

You should have received a copy of the GNU General Public License along with
this package. If not, see <http://www.gnu.org/licenses/>
