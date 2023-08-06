# vim: set expandtab ts=4 sw=4 filetype=python:

import collections
import json
import logging
import textwrap
import urllib

log = logging.getLogger(__name__)

class GeocodeResponse(collections.Sequence, collections.Sized):

    """
    Friendlier wrapper around the JSON we get back from Google's
    geocoding API.
    """

    def __init__(self, json_blob):
        self.json_blob = json_blob
        self.response = json.loads(json_blob)

    @property
    def status(self):
        return self.response['status']

    @property
    def results(self):
        return self.response['results']

    @property
    def ambiguous_results(self):
        if len(self.results) > 1:
            return [GeocodedAddress(r) for r in self.results]


    @property
    def one_match(self):
        if len(self.results) == 1:
            return GeocodedAddress(self.results[0])

    @property
    def number_of_matches(self):

        num_results = len(self.results)

        if num_results == 1:
            return '<h2>I found exactly one match.</h2>'

        elif num_results > 1:
            return '<h2>I found %d matches.</h2>' % num_results

        else:
            return '<h2>I found zero matches.</h2>'


    def __len__(self):
        return len(self.results)

    def __getitem__(self, index):
        return GeocodedAddress(self.results[index])

    def to_dict(self):

        address_to_object = dict([(g.formatted_address, g.to_dict()) for
            g in self.ambiguous_results]) if self.ambiguous_results else {}

        return dict(

            address_to_object=address_to_object,

            number_of_matches=self.number_of_matches,

            one_match=self.one_match.to_dict() if self.one_match else None,

            ambiguous_results=[g.to_dict() for g in self.ambiguous_results]
            if self.ambiguous_results else None,

            candidate_matches_form=self.candidate_matches_form
        )

    @property
    def jsonified(self):

        return json.dumps(self.to_dict())


class Geocoder(object):

    """

    >>> addr = '2908 Coleridge, Cleveland Heights, OH, 44118'
    >>> Geocoder.lookup(addr) # doctest: +SKIP

    """

    GEOCODE_BASE_URL = 'http://maps.googleapis.com/maps/api/geocode/json'

    @classmethod
    def lookup(cls, geocoded_address, region_bias=None,
        viewport_bias=None):

        geo_args = dict(address=geocoded_address, sensor='false')

        if region_bias:
            geo_args['region'] = region_bias

        # I'm explicitly setting up a viewport bias right here.

        geo_args['bounds'] = "41.750312,-88.032761|42.129294,-87.380447"

        url = cls.GEOCODE_BASE_URL + '?' + urllib.urlencode(geo_args)

        log.debug('url is %s' % url)

        raw_results = urllib.urlopen(url).read()

        return GeocodeResponse(raw_results)


class GeocodedAddress(collections.Mapping):

    """
    Represents a single result back from Google's geocoding API.
    """

    def __init__(self, result):
        self.result = result
        self.addr_parts = None

    @property
    def latitude(self):
        return self.result['geometry']['location']['lat']

    @property
    def longitude(self):
        return self.result['geometry']['location']['lng']

    @property
    def formatted_address(self):
        return self.result['formatted_address']

    @property
    def address_parts(self):
        if self.addr_parts:
            return self.addr_parts

        self.addr_parts = dict()

        address_components = self.result['address_components']
        for component in address_components:
            if 'street_number' in component['types']:
                if 'street' not in self.addr_parts:
                    self.addr_parts['street'] = component['long_name']
                else:
                    self.addr_parts['street'] = '%s %s' % (component['long_name'], self.addr_parts['street'])
            elif 'route' in component['types']:
                if 'street' not in self.addr_parts:
                    self.addr_parts['street'] = component['long_name']
                else:
                    self.addr_parts['street'] = '%s %s' % (self.addr_parts['street'], component['long_name'])
            elif 'locality' in component['types']:
                self.addr_parts['city'] = component['long_name']
            elif 'administrative_area_level_1' in component['types']:
                self.addr_parts['state'] = component['short_name']
            elif 'postal_code' in component['types']:
                self.addr_parts['zip_code'] = component['long_name']

        return self.addr_parts

    @property
    def street(self):
        if 'street' in self.address_parts:
            #log.info('street = %s' % self.address_parts['street'])
            return self.address_parts['street']

    @property
    def city(self):
        if 'city' in self.address_parts:
            return self.address_parts['city']

    @property
    def state(self):
        if 'state' in self.address_parts:
            return self.address_parts['state']

    @property
    def zip_code(self):
        if 'zip_code' in self.address_parts:
            return self.address_parts['zip_code']

    @property
    def partial_match(self):
        return self.result['partial_match']

    def __getitem__(self, k):
        return self.result[k]

    def __len__(self):
        return len(self.result)

    def __iter__(self):
        return iter(self.result)

    def to_dict(self):

        return dict(
            formatted_address=self.formatted_address,
            street=self.street,
            city=self.city,
            state=self.state,
            zip_code=self.zip_code,
            latitude=self.latitude,
            longitude=self.longitude)
