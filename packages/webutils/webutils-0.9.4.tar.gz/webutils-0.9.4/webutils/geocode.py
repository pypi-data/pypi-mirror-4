from geopy import geocoders, distance
from geopy.geocoders.google import GQueryError


class GeoCode(object):
    ''' Simple class to interface with Google geocode API.
        Depends on geopy module:
        http://code.google.com/p/geopy/
    '''
    def __init__(self, api_key):
        self.api_key = api_key

    def get_geocode(self, location=None):
        ''' Function to geocode an address, zipcode, etc.
            location variable can be any of those. ie,
               90715
               Lakewood, Ca
               12345 Fake Blvd, Lakewood, Ca 90715, USA
               etc.

            returns
                (Location, (latitude, longitude))
                (u'Lakewood, Ca USA', (-32.20923, -44.20948302))
        '''
        if location is None:
            return None

        g = geocoders.Google(self.api_key)
        try:
            res = g.geocode(location, exactly_one=False)
        except GQueryError:
            return None
            
        if isinstance(res, tuple):
            return res
        else:
            # Multiple, or no, results. Grab the first one
            if res:
                res_list = list(res)
                if res_list:
                    return res_list[0]

        return None


    def parse_result(self, gtuple=None):
        ''' Function to parse a geopy google geocode result tuple
            into an address map hash
        '''
        addy_hash = {
            'country': '',
            'zipcode': '',
            'state': '',
            'city': '',
            'address': '',
            'latitude': '',
            'longitude': ''
        }
        addy_map = ['country', 'zipcode', 'state', 'city', 'address']

        if gtuple is None:
            return gtuple

        place = [x.strip() for x in gtuple[0].split(',')]
        place.reverse()
        addy_hash['latitude'] = gtuple[1][0]
        addy_hash['longitude'] = gtuple[1][1]
      
        for x in xrange(len(place)):
            if addy_map[x] == 'zipcode':
                try:
                    addy_hash[addy_map[x]] = place[x].split()[1]
                    addy_hash[addy_map[x + 1]] = place[x].split()[0]
                except IndexError:
                    # Only returns Country + Zip (or State)
                    zip_state = place[x]
                    if zip_state.isdigit():
                        addy_hash[addy_map[x]] = zip_state
                    else:
                        addy_hash[addy_map[x + 1]] = zip_state
                addy_map.pop(x + 1)
            else:
                    addy_hash[addy_map[x]] = place[x]

        return addy_hash

    def parse_location(self, address, city, state, zipcode, country):
        ''' Function to get geocode information for various 
            address setups.
            Returns hash
        '''
        addy_list = [address, city, state, zipcode, country]
        location = ', '.join([x for x in addy_list if x])

        data = self.get_geocode(location)
        if data:
            return self.parse_result(data)
        return None


    def get_distance(self, start, end):
        ''' Return the distance, in miles, between the 2 
            lat/long tuples passed to this funtion.
            Example: get_distance((24.308400, -118.3903400), (34.23420, -87.23490))
        '''
        return distance.distance(start, end).miles
