import anyjson
import httplib2
import sys
import urllib
import urlparse


class API(object):

    ENDPOINT = 'https://auspost.com.au/api/'
    SERIALIZATION = '.json'

    def __init__(self, api_key, debug=False, **kwargs):
        self.headers = {'AUTH-KEY': api_key}
        self.client = httplib2.Http(**kwargs)
        self.debug = debug

    def _transform_content(self, content):
        return anyjson.deserialize(content)

    def _make_request(self, path, parameters={}, method='GET', headers={}, **kwargs):
        headers.update(self.headers)

        url = urlparse.urljoin(self.ENDPOINT, path)
        if self.SERIALIZATION:
            url += self.SERIALIZATION
        if parameters:
            url += '?' + urllib.urlencode(parameters)

        if self.debug:
            print >>sys.stderr, url

        response, content = self.client.request(url, method, headers=headers, **kwargs)

        return self._transform_content(content)

    def countries(self):
        return self._make_request('postage/country')

    def domestic_letter_thickness(self):
        return self._make_request('postage/letter/domestic/thickness')

    def domestic_letter_weight(self):
        return self._make_request('postage/letter/domestic/weight')

    def domestic_letter_envelope_size(self):
        return self._make_request('postage/letter/domestic/size')

    def international_letter_weight(self):
        return self._make_request('postage/letter/international/weight')

    def international_parcel_weight(self):
        return self._make_request('postage/parcel/international/weight')

    def domestic_parcel_weight(self):
        return self._make_request('postage/parcel/domestic/weight')

    def domestic_parcel_box_type(self):
        return self._make_request('postage/parcel/domestic/type')

    def domestic_parcel_box_size(self):
        return self._make_request('postage/parcel/domestic/size')

    def domestic_letter_service_list(self, length, width, thickness, weight):
        """
        :param length: Length of the letter in millimetres (max 260mm)
        :param width: Width of the letter in millimetres (max 360mm)
        :param thickness: Thickness of the letter in millimetres (max 20mm)
        :param weight: Weight of the letter in grams (max 500g)
        """
        parameters = {
            'length': length,
            'width': width,
            'thickness': thickness,
            'weight': weight,
            }
        return self._make_request('postage/letter/domestic/service', parameters=parameters)

    def domestic_parcel_service_list(self, from_postcode, to_postcode, length, width, height, weight):
        """
        :param from_postcode: Postcode from which the parcel will be sent
        :param to_postcode: Postcode to which the parcel will be sent
        :param length: Length of the parcel in centimetres
        :param width: Width of the parcel in centimetres
        :param height: Height of the parcel in centimetres
        :param weight: Weight of the parcel in kilograms
        """
        parameters = {
            'from_postcode': from_postcode,
            'to_postcode': to_postcode,
            'length': length,
            'width': width,
            'height': height,
            'weight': weight,
            }
        return self._make_request('postage/parcel/domestic/service', parameters=parameters)

    def international_letter_service_list(self, country_code, weight):
        raise NotImplementedError

    def international_parcel_service_list(self, country_code, weight):
        raise NotImplementedError

    def postcode_search(self, q, state=None, exclude_post_box=None):
        parameters = {'q': q}

        if state:
            parameters['state'] = state

        if exclude_post_box:
            parameters['excludePostBoxFlag'] = 'true'

        return self._make_request('postcode/search', parameters=parameters)

    def domestic_letter_postage_calculation(self, service_code, weight, option_code=None, suboption_code=None, extra_cover=None):
        """
        :param service_code: Code retrieved from domestic_letter_service_list
        :param weight: Weight of the letter in grams (max 500g)
        :param option_code: Code retrieved from domestic_letter_service_list
        :param suboption_code: Code retrieved from domestic_letter_service_list
        :param extra_cover: Monetary value of extra cover, integer only
        """
        parameters = {
            'service_code': service_code,
            'weight': weight,
            }
        if option_code:
            parameters['option_code'] = option_code
        if suboption_code:
            parameters['suboption_code'] = suboption_code
        if extra_cover:
            assert suboption_code == "AUS_SERVICE_OPTION_EXTRA_COVER"
            parameters['extra_cover'] = extra_cover
        return self._make_request('postage/letter/domestic/calculate', parameters=parameters)

    def domestic_parcel_postage_calculation(self, from_postcode, to_postcode, length, width, height, weight, service_code, option_code=None, suboption_code=None, extra_cover=None):
        """
        :param from_postcode: Postcode from which the parcel will be sent
        :param to_postcode: Postcode to which the parcel will be sent
        :param length: Length of the parcel in centimetres
        :param width: Width of the parcel in centimetres
        :param height: Height of the parcel in centimetres
        :param weight: Weight of the parcel in kilograms
        """
        parameters = {
            'from_postcode': from_postcode,
            'to_postcode': to_postcode,
            'length': length,
            'width': width,
            'height': height,
            'weight': weight,
            'service_code': service_code,
            }
        if option_code:
            parameters['option_code'] = option_code
        if suboption_code:
            parameters['suboption_code'] = suboption_code
        if extra_cover:
            parameters['extra_cover'] = extra_cover
        return self._make_request('postage/parcel/domestic/calculate', parameters=parameters)

    def international_letter_postage_calculation(self, country_code, service_code, weight=None, option_code=None, suboption_code=None, extra_cover=None):
        raise NotImplementedError

    def international_parcel_postage_calculation(self, country_code, service_code, weight, option_code=None, extra_cover=None):
        raise NotImplementedError
