#!c:/Python27/python.exe
# Change the above for *nix
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
