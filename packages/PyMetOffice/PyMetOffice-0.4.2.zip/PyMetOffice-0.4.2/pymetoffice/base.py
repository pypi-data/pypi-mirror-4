#!/usr/bin/python
# Change the above for *nix

## \package base
#  This provides the low level access to the
#  UK Met Office DataPoint API.
#  It is not intended for direct use, but feel free!
#
#  To use these utilities, you need to read the
#  Met Office documentation. Unfortunately,
#  this is not always completely accurate
#  or even internally consistent. Doubtless things will
# improve.
#

## This decoding hack is more or less justified because the
#  Met Office Datapoint service is for UK only at present.
#  ASCII won't do because some Gaelic site names have
#  accented characters. Hence, I chose latin-1.

import sys
reload(sys)
sys.setdefaultencoding('L1')

import json
import xml.dom.minidom as xdm
import codecs
import places

try:
   import urllib.request
   _urlopen = urllib.request.urlopen
except:
   try:
      import urllib2
      _urlopen = urllib2.urlopen
   except:
      import urllib
      _urlopen = urllib.urlopen

#####################################################

## This is the base model object and provides
#  low level access.
class baseModel(object):
   ## Constructor
   #  \param url
   #    This is mandatory and must be the current
   #     base url for the Met Office DataPoint services.
   #     at the time of writing, this is
   #     http://datapoint.metoffice.gov.uk
   #     It has changed in the past and may well do so again.
   #  \param key
   #     This is mandatory and you must obtain a key from the
   #     Met Office DataPoint web site. Currently, this is free
   #     for modest usage (<= 5000 data requests per day and
   #     <= 100 requests/minute). Register (free)
   #     at http://www.metoffice.gov.uk/datapoint (currently).
   def __init__(self, url, key):
      object.__init__(self)
      ## Holds client api-key.
      self._key = key
      ## Holds current DataPoint api URL.
      self._url = url
      self._currentLocation = ''
      self._placeList = []
      self._obCached = False
      self._fcCached = False
      
      
   def _getCached(self):
      return self._obCached and self._fcCached
   Cached = property(_getCached)
   
   def _getObList(self):
      if not self._obCached:
         self._obsSitelist = self._getObsXMLSitelist()
         self._obCached = True
      return self._obsSitelist
   
   def _getFcList(self):
      if not self._fcCached:
         self._fcsSitelist = self._getFcsXMLSitelist()
         self._fcCached = True
      return self._fcsSitelist
   
   ## This provides the list of observation sites.
   #  At the time of writing, there are just over
   #  5000 of these.
   ObservationSitelist = property(_getObList)
   ## This provides the list of forecast sites.
   #  At the time of writing, there are just over
   #  120 of these.
   ForecastSitelist = property(_getFcList)
   
   
   ## All data requests made to the DataPoint API come
   #  through this method. It is made as future-proof
   #  as reasonably possible but does assume that the API
   #  will stick to the URL+parameter-string format for
   #  requests
   #  \em Note: some Met Office documentation
   #  leaves out the second folder (currently data).
   #  The API would not work for me with this omission.
   #  The same documentation gives a previous base url.
   #  \param access Currently 'public'
   #  \param datatype Currently 'data'
   #  \param datacategory one of the following at present:
   #     val   for values (quite a lot of requests)\n
   #     layer usually used for maps and related requests\n
   #     txt   usually for requests where the interesting data is text
   #  \param dataclass Currently 'wxobs' for observations and
   #                    'wxfcs' for forecasts.
   #  \param datasource This has different meanings for different types
   #                    of requests.
   #     'all' for many requests
   #     a layer name for map requests
   #     'mountain area' for mountain forecasts
   #     'nationalpark' for National Park forecasts.
   #  \param dataformat Currently available formats are 'xml' and 'json'
   #  \param datarequest The Met Office calls this  \em location which is
   #     rather misleading.
   #     For many requests it is a location, either as id number as a string.
   #     It may also be an image format 'png' or 'gif' at present. This is used
   #     for requests returning image data (maps etc).
   #     It may also be 'sitelist' or 'capabilities' which do
   #     what they say on the tin.
   #  \param requestargs This must be a dictionary
   #     of the other parameters required by the request. The mandatory
   #     entry in the dictionary of 'key':api-access-key is added automatically,
   #     where the api access key is obtained as described above.
   #  \returns A 2-tuple consisting of: a string which is the raw xml or json according
   #     to the dataformat requested (the caller must parse the data as needed) and
   #     the URL used for the request (for diagnostic purposes, mostly discarded).
   def _makeApiRequest(self,
                        access,
                        datatype,
                        datacategory,
                        dataclass,
                        datasource,
                        dataformat,
                        datarequest,
                        **requestargs):
      url = '/'.join([self._url,
                        access,
                        datatype,
                        datacategory,
                        dataclass,
                        datasource,
                        dataformat,
                        datarequest
                     ])
      rargs = requestargs
      rargs['key'] = self._key
      params = ['='.join([k,rargs[k]]) for k in rargs.keys()]
      params = '&'.join(params)
      url = '?'.join([url,params])
      source = _urlopen(url)
      data = source.read(3000000)
      return (data, url)
   
   ## This method provides the list of times for which
   #  observations are available.
   #  \return List of times in yyyymmddThhmmZ format
   def _getObservationTimes(self):
      (d, u) = self._makeApiRequest('public',
                                         'data',
                                         'val',
                                         'wxobs',
                                         'all',
                                         'json',
                                         'capabilities',
                                         **{'res':'hourly'})
      return json.loads(d)['Resource']['TimeSteps']['TS']
   
   ## This method provides a list of days for which forecasts are
   #  available.
   #  \return List of times in yyyymmddThhmmZ format
   def _getForecastDays(self):
      (d, u) = self._makeApiRequest('public',
                                         'data',
                                         'val',
                                         'wxfcs',
                                         'all',
                                         'json',
                                         'capabilities',
                                         **{'res':'daily'})
      return json.loads(d)['Resource']['TimeSteps']['TS']
      
   ## This method provides a list of times for which forecasts are
   #  available.
   #  \return List of times in yyyymmddThhmmZ format
   def _getForecastTimes(self):
      (d, u) = self._makeApiRequest('public',
                                         'data',
                                         'val',
                                         'wxfcs',
                                         'all',
                                         'json',
                                         'capabilities',
                                         **{'res':'3hourly'})
      return json.loads(d)['Resource']['TimeSteps']['TS']
   
   
   ## \b Warning: may not be completely reliable. Work in progress.
   #  This method obtains the list of observation sites.
   #  As currently coded it is ok but may fail if
   #  the list of sites increases dramatically. The problem
   #  is not always managing to collect all data from the
   #  connection.
   #  Actually, this is consistently quite unreliable!
   #  \return List of Site objects.
   def _getObservationSitelist(self):
      result = []
      (d, u) = self._makeApiRequest('public',
                                         'data',
                                         'val',
                                         'wxobs',
                                         'all',
                                         'json',
                                         'sitelist',
                                         **{})
      sites = json.loads(d)['Locations']['Location']
      for s in sites:
         result.append(Site(**s))
      result.sort()
      return result

      
   ## \b Warning: may not be completely reliable.
   #  This method obtains the list of sites for forecasts.
   #  As currently coded it is unreliable as it
   #  does not always manage to collect all data from the
   #  connection.
   #  However, the failure rate is much lower than
   #  for observation sites.
   #  \return List of Site objects.
   def _getForecastSitelist(self):
      result = []
      (d, u) = self._makeApiRequest('public',
                                         'data',
                                         'val',
                                         'wxfcs',
                                         'all',
                                         'json',
                                         'sitelist',
                                         **{})
      sites = json.loads(d)['Locations']['Location']
      for s in sites:
         result.append(Site(**s))
      result.sort()
      return result
   
   ## This version retrieves XML and seems to be more reliable!
   #  No idea why that should be.
   def _getFcsXMLSitelist(self):
      result = []
      (d, u) = self._makeApiRequest('public',
                                         'data',
                                         'val',
                                         'wxfcs',
                                         'all',
                                         'xml',
                                         'sitelist',
                                         **{})
      doc = xdm.parseString(d)
      sl = doc.getElementsByTagName('Location')
      for s in sl:
         site = Site(s.getAttribute('name'),
                     s.getAttribute('id'),
                     s.getAttribute('latitude'),
                     s.getAttribute('longitude'))
         result.append(site)
      result.sort()
      return result

   ## This version retrieves observation sites using
   #  an XML request. Really provided for completeness.
   #  \return List of Site objects where observations are made.
   def _getObsXMLSitelist(self):
      result = []
      (d, u) = self._makeApiRequest('public',
                                         'data',
                                         'val',
                                         'wxobs',
                                         'all',
                                         'xml',
                                         'sitelist',
                                         **{})
      doc = xdm.parseString(d)
      sl = doc.getElementsByTagName('Location')
      for s in sl:
         site = Site(s.getAttribute('name'),
                     s.getAttribute('id'),
                     s.getAttribute('latitude'),
                     s.getAttribute('longitude'))
         result.append(site)
      result.sort()
      return result
   
   ## This method obtains a list of places corresponding
   #  to a given location.
   def _getPlaces(self, location):
      if self._currentLocation != location:
         self._placeList = places.PlaceSet(location)._places
         self._currentLocation = location
      return self._placeList
   
     
   ## A method to get round the lack of 'nearestlatlon'
   #  for observations.
   def _getNearestObservationId(self, place):
      sites = self.ObservationSitelist
      lt1 = float(place.getLatLon()['lat'])
      ln1 = float(place.getLatLon()['lon'])
      dist = 1000.0
      st = None
      for s in sites:
         lt2 = float(s.latitude)
         ln2 = float(s.longitude)
         d = abs(ln1-ln2) + abs(lt1-lt2)
         if d < dist:
            dist = d
            st = s
      if st: st = st.id
      return st
         
   
## The Site class simply provides a convenient container for site information.
#  It can be used as a sortable item in lists.
class Site(object):
   ## The parameters are derived straight from JSON or XML values.
   #  Typically, one creates a Site object by
   #     site = Site(**<data-from-DataPoint>)
   #  as in the \em _getObervationSitelist code.
   def __init__(self, name, id, latitude, longitude):
      object.__init__(self)
      self.name = name
      self.id = id
      self.latitude = latitude
      self.longitude = longitude
   ## This is provided so that Site objects are sortable by name.   
   def __lt__(self, other):
      return self.name < other.name
   ## This provides a simple printable representation.
   #  Mostly useful for testing.
   def __repr__(self):
      s = '{:<35}{:^6}{:>8}{:>8}'.format(self.name, self.id, self.latitude, self.longitude)
      return s
   
   def __str__(self):
      return self.__repr__()
   

