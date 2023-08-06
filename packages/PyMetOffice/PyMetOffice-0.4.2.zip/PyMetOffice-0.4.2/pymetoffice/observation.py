#!/usr/bin/python

import base
import json
import constants
import places
import xml.dom.minidom

## This is the analogue of the ForecastModel class
#  At present, the DataPoint API appears not to
#  support the 'nearestlatlon' form of location specifier.
#  This is inconvenient, to say the least!
class ObservationModel(base.baseModel):
   ## Get the raw data (Json format).
   #  Use as you please but the library increasingly uses
   #  the XML methods.
   #  \param period Currently this must be 'hourly'.
   #  May change in the future.
   #  \param site Most likely to be a site Id,
   #  eg '3772' gets you the data for Heathrow Airport.
   #  \param extra Usually {}.
   #  \return Decoded JSON dictionary.
   def _getRawJsonObsData(self, period, site, **extra):
      params = extra
      params['res'] = period
      (d, u) = self._makeApiRequest('public',
                                       'data',
                                       'val',
                                       'wxobs',
                                       'all',
                                       'json',
                                       site,
                                       **params)
      return json.loads(d)
   ## Get XML data as a minidom object.
   #  \param period Currently this must be 'hourly'.
   #  May change in the future.
   #  \param site Most likely to be a site Id,
   #  eg '3772' gets you the data for Heathrow Airport.
   #  \param extra Usually {}.
   #  \return Decoded JSON dictionary.
   def _getRawXMLObsData(self, period, site, **extra):
      params = extra
      params['res'] = period
      (d, u) = self._makeApiRequest('public',
                                       'data',
                                       'val',
                                       'wxobs',
                                       'all',
                                       'xml',
                                       site,
                                       **params)
      return xml.dom.minidom.parseString(d)
   ## Construct a dictionary for decoding abbreviations into
   #  user-friendly forms. Deals with a couple of current
   #  special cases.
   #  \param doc An XML document as returned from
   #  getRawXmlObsData.
   def _makeDecoder(self, doc):
      result = {}
      els = doc.getElementsByTagName('Param')
      for e in els:
         atts = e.attributes
         fname = e.firstChild.data
         abbr = atts['name'].value
         unit = atts['units'].value
         if unit == 'm':
            unit = 'metres'
         if abbr == 'D':
            unit = u''
         decstring = '%s: %%s %s' % (fname, unit)
         result[abbr] =  decstring
      return result
   ## For now, this method is not supported by the
   #  DataPoint API (apparently). It always returns
   #  an empty list of Observation objects.
   #  However, it does not throw an exception because
   #  the API returns just the parameter
   #  decoding information.
   #  One day we may be able to use it.
   def getObservationsPlace(self, location):
      latlong = places.getLatLong(location)
      latlong.pop('name')
      doc = self._getRawXMLObsData('hourly', 'nearestlatlon', **latlong)
      dec = self._makeDecoder(doc)
      obsSet = ObservationSet(dec, doc)
      return obsSet
   ## This, on the other hand, works fine given a valid
   #  location Id.
   #  I have chosen \em not to provide a mechanism for
   #  specifying a specific time (which would have to be in
   #  the last 24 hours). It is simpler
   #  to get all the data (24 observations) and extract the
   #  one that you want.
   def getObservationsId(self, id):
      doc = self._getRawXMLObsData('hourly', id, **{})
      dec = self._makeDecoder(doc)
      obsSet = ObservationSet(dec, doc)
      return obsSet
      
## A convenient wrapper for a single observation.         
class Observation(object):
   ## \param decoder
   #  is a decoder obtained from the _makeDecoder method.
   #  \param repData
   #  is a DOM Element object with tag 'Rep'
   def __init__(self, decoder, repData):
      object.__init__(self)
      r = repData
      self._data = {}
      reptime = int(r.firstChild.data)/60
      stime = '%02d:00' % reptime
      self._data['time'] = stime
      atts = r.attributes
      for k in atts.keys():
         if k == 'W':
            self._data[k] = constants.WEATHER_TYPES[int(atts[k].value)]
         else:
            self._data[k] = decoder[k] % atts[k].value
   ## The 'day' value is part of a set of observations but can be useful
   #  in a single observation.
   def addDay(self, day):
      self._data['day'] = day
   ## Enable sorting of lists of Observation objects.
   def __lt__(self, other):
      return self._data['time'] < other._data['time']
   ## This provides a fairly sensible text representation.
   #  Mostly useful for debugging.
   def __repr__(self):
      result = []
      data = self._data
      result.append('%s: %s, %s: %s' % ('Date', data['day'], 'Time', data['time'] ))
      data.pop('time')
      data.pop('day')
      keys = data.keys()
      for k in keys:
         result.append('\t\t%s' % data[k])
      return '\n'.join(result)
            
   def __str__(self):
      return self.__repr__()
   
class ObservationSet(object):
   ## \param doc
   #  is a complete XML DOM as returned from
   #  _getRawObsData.
   #  \param decoder A decoder returned by calling
   #  _makeDecoder with the supplied doc.  
   def __init__(self, decoder, doc):
      object.__init__(self)
      self._doc = doc
      self._reps = []
      obsData = doc.getElementsByTagName('DV')
      obsDataDate = obsData[0].attributes['dataDate'].value[:-1].split('T')
      self._date = obsDataDate[0]
      self._time = obsDataDate[1]
      periods = doc.getElementsByTagName('Period')
      for period in periods:
         date = period.attributes['value'].value[:-1]
         obs = doc.getElementsByTagName('Rep')
         for ob in obs:
            rep = Observation(decoder, ob)
            rep.addDay(date)
            self._reps.append(rep)
            
   def _getObs(self):
      return self._reps
   
   observations = property(_getObs)
      
      
      
      
      
