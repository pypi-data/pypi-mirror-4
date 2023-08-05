from json import loads
from omgeo import Geocoder
import socket
from urllib import urlencode
from urllib2 import HTTPError, urlopen, URLError

class PolyFinder:
    """
    A class to get geoenabled information based on an address.
    Initialize with a single-line address as the only parameter.
    """

    #: Some endpoint constants
    PHILA_GIS_BASE_URL = 'http://gis.phila.gov/ArcGIS/rest/services/'

    def __init__(self, address):
        """Geocode given address and set self.coords to (x,y) tuple."""
        geocoder = Geocoder()
        georesult = geocoder.geocode(address)
        geocandidates = georesult['candidates']
        coord_pairs = [(c.x, c.y) for c in geocandidates]
        num_coord_pairs = len(coord_pairs)
        if num_coord_pairs == 0:
            raise Exception('No geocoding results for %s' % address)
        if num_coord_pairs > 1:
            choices = [c.match_addr for c in geocandidates]
            raise Exception('Ambiguous address. Choices are:\n%s' % choices)
        self.coords = coord_pairs[0]
    
    def get_coords_str(self):
        """
        Turn instance's (x,y) coordinate tuple into a comma-separated string.
        """
        return '%s,%s' % (self.coords[0], self.coords[1])

    def get_response(self, endpoint, outFields='*', timeout=10): # adapted from Azavea's python-omgeo
        """
        Get an HTTP response from an ESRI ArcGIS REST endpoint.

        arguments
        =========
        endpoint    -- the URL of the REST API without the query string
        outFields   -- comma-separated list of desired output outFields
        timeout     -- number of seconds to wait before giving up
        """
        query = dict(inSR='4326',
                    outSR='4326',
                    geometry=self.get_coords_str(),
                    geometryType='esriGeometryPoint',
                    returnCountOnly='false',
                    returnIdsOnly='false',
                    returnGeometry='false',
                    outFields=outFields,
                    f='pjson')
        try:
            response = urlopen('%s?%s' % (endpoint, urlencode(query)),
                               timeout=timeout)
        except Exception as ex:
            if type(ex) == socket.timeout:
                raise Exception('API request timed out after %s seconds.' % timeout_secs)
            else:
                raise ex
        if response.code != 200:
            raise Exception('Received status code %s from %s. Content is:\n%s'
                            % (response.code,
                               self.get_service_name(),
                               response.read()))
        return response

    def ward_div(self, outFields='*'):
        """
        Get a dict containing ward district info, including WARD and DISTRICT k/v pairs.
        """
        endpoint = '%sPhilaGov/PollingPlaces/MapServer/0/query' % self.PHILA_GIS_BASE_URL
        query = dict()
        response_dict = loads(self.get_response(endpoint, outFields).read())
        features = response_dict['features']
        num_features = len(features)
        if num_features == 0:
            raise Exception('No ward districts found for %s.' % self.coords)
        elif num_features > 1:
            raise Exception('Overlapping ward districts found at %s.' % self.coords)
        return response_dict['features'][0]['attributes']