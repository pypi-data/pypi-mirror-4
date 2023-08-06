#!/usr/bin/python
# Convert various place identifiers to lat, lon pair.
#
# Experimental code at present.
#
# The object of the exercise is to convert
# a human-readable place name to latitude, longitude
# so that we can use the 'nearestlatlon' facility of the DataPoint API.

## _urlopen
#  This is the function required to open a URL as a file-like object.
#  We make three attempts to get a url library. If the 3rd one
#  fails, the exception is \em not caught. I claim this is deliberate!

try:
   import urllib
   _urlopen = urllib.request.urlopen
   _quote = urllib.quote
except:
   try:
      import urllib2
      _urlopen = urllib2.urlopen
      _quote = urllib2.quote
      urllib = urllib2
   except:
      import urllib
      _urlopen = urllib.urlopen
      _quote = urllib2.quote
      
#import urllib

import json
import xml
import xml.dom.minidom
## This is the URL of the currently used free place locator.
#  Many thanks MapQuest for providing it.

MapQuestKey = 'Fmjtd%7Cluub296r2g%2Crl%3Do5-968shf'
MAPQUEST = "http://open.mapquestapi.com/geocoding/v1/address"
      

## A convenient wrapper round location information
#  obtained from geocoding sites. 
class Place(object):
   ## Constructor:
   #  \param info A dictionary containing
   #  name: original search text, county: UK county,
   #  lat: latitude, lon: longitude.
   def __init__(self, **info):
      object.__init__(self)
      self._info = info
   
   ## Enable sorting of lists of places.
   def __lt__(self, other):
      return self._info['county'] < other._info['county']
   
   ## Printing a representation can be useful for debugging.
   def __repr__(self):
      data = []
      pattern = '%s: %s'
      for k in self._info.keys():
         data.append(pattern % (k, self._info[k]))
      return ', '.join(data)
   
   def __str__(self):
      return self.__repr__()
   
   ## A Utility method to return data suitable for requesting forecasts.
   def getLatLon(self):
      d = self._info
      d.pop('name')
      d.pop('county')
      return d
   
   ## Class to represent a collection of places.
   #  Useful for presenting choices to user after a text search.
class PlaceSet(object):
   ## \param location A full or partial address.
   #  If 'UK' does not appear, it will be added
   #  because the DataPoint API provides UK data only.
   def __init__(self, location):
      object.__init__(self)
      self._places = []
      loc = location
      if loc.find('UK') < 0: loc = '%s%s' % (loc, ',UK')
      data = self._getData(loc)
      doc = xml.dom.minidom.parseString(data)
      locations = doc.getElementsByTagName('locations')
      locs = locations[0].getElementsByTagName('location')
      for loc in locs:
         name = loc.getElementsByTagName('adminArea5')[0].firstChild.data
         county = loc.getElementsByTagName('adminArea4')[0].firstChild.data
         lat = loc.getElementsByTagName('lat')[0].firstChild.data
         lon = loc.getElementsByTagName('lng')[0].firstChild.data
         info = {'name': name, 'county': county, 'lat': lat, 'lon': lon}
         place = Place(**info)
         self._places.append(place)
      self._places.sort()
      
   ## This method makes the geocoding request from a
   #  full or partial address.
   def _getData(self, location):
      data = None
      url = '%s?location=%s&outFormat=xml&key=%s'
      fullurl = url % (MAPQUEST, _quote(location), MapQuestKey)
      data = _urlopen(fullurl).read()
      return data

   def _getPlaces(self):
      return self._places
   
   def __repr__(self):
      data = [s.__repr__() for s in self._places]
      return '\n'.join(data)
   
   places = property(_getPlaces)

