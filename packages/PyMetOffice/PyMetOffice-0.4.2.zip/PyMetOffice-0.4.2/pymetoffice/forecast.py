#!/usr/bin/python

import base
import json
import constants
import places

class ForecastModel(base.baseModel):
   def _getRawForecastData(self, period, site, **other):
      params = other
      params['res'] = period
      (d, u) = self._makeApiRequest('public',
                                       'data',
                                       'val',
                                       'wxfcs',
                                       'all',
                                       'json',
                                       site,
                                       **params)
      return json.loads(d)
   
   ## This returns a dictionary in a suitable form for
   #  translating the Met Office observation/forecast items
   #  into more user-friendly names.
   def makeDecoder(self, data):
      d = data['SiteRep']['Wx']['Param']
      result = {}
      for item in d:
         result[item['name']] = (item['$'], item['units'])
      return result
   
   def _translateUnits(self, fcdata, decoder):
      result = []
      for rep in fcdata:
         # Two values need decoding.
         rep['V'] = constants.VISIBILITY[rep['V']]
         rep['W'] = constants.WEATHER_TYPES[int(rep['W'])]
         tmp = []
         for k in rep.keys():
            if k != '$':
               tmp.append((decoder[k][0], rep[k], decoder[k][1]))
         tmp.sort()
         result.append((rep['$'], tmp))
      result.sort()
      return result
        
      
   def _getDailyForecastData(self, site, **params):
      result = []
      data = self._getRawForecastData('daily', site, **params)
      dv = data['SiteRep']['DV']['Location']['Period']
      decoder = self.makeDecoder(data)
      for fc in dv:
         fcdata = fc['Rep']
         date = fc['value']
         fcast = self._translateUnits(fcdata, decoder)
         result.append((date, fcast))
      return result
         
   def _get3HourlyForecastData(self, site, **params):
      result = []
      data = self._getRawForecastData('3hourly', site, **params)
      dv = data['SiteRep']['DV']['Location']['Period']
      decoder = self.makeDecoder(data)
      for fc in dv:
         fcdata = fc['Rep']
         date = fc['value']
         fcast = self._translateUnits(fcdata, decoder)
         result.append((date, fcast))
      return result
         
   def getDailyForecastPlace(self, place, index=0):
      pls = places.PlaceSet(place)
      data = pls.places[index].getLatLon()
      return self._getDailyForecastData('nearestlatlon', **data)

   def get3HourlyForecastPlace(self, place, index=0):
      pls = places.PlaceSet(place)
      data = pls.places[index].getLatLon()
      return self._get3HourlyForecastData('nearestlatlon', **data)
   
   def getDailyForecastId(self, id):
      data = self._getDailyForecastData(id, **{})
      return data

   def get3HourlyForecastId(self, id):
      data = self._get3HourlyForecastData(id, **{})
      return data

      