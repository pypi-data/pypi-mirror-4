# -- coding: utf-8 --

# Copyright 2013 X Studios Inc. All rights reserved.
#
# Use of this source code is governed by the Apache 2 license
# that can be found in the LICENSE file.
#
# @author  Nickolas Whiting  <nwhiting@xstudiosinc.com>

VERSION = '1.0.1'

# Python
import urllib2
from urlparse import urlunparse, urlparse
from urllib import urlencode
from json import load, loads

try:
    import settings
except ImportError:
    settings = {}

ZIPTAX_API_KEY = getattr(settings, "ZIPTAX_API_KEY", "you-api-key")
ZIPTAX_API_VERSION = getattr(settings, "ZIPTAX_API_VERSION", "v20")
ZIPTAX_API_URL = getattr(settings, "ZIPTAX_API_URL", "api.zip-tax.com")

RESPONSE_CODES = {
    100: 'SUCCESS',
    101: 'INVALID_KEY',
    102: 'INVALID_STATE',
    103: 'INVALID_CITY',
    104: 'INVALID_POSTAL_CODE',
    105: 'INVALID_FORMAT'
}

class Ziptax_Failure(Exception):
    pass

def get_tax_rate(postalcode = None, state = None,  city = None, format = 'JSON'):
    """
    ZipTax

    Zip-Tax.com API Class

    Currently only JSON is supported.
    """
    params = {
        'state': state,
        'postalcode': postalcode,
        'city': city,
        'key': ZIPTAX_API_KEY,
        'format': format
    }
    for a, b in params.items():
        if b is None:
            del params[a]
    params = urlencode(params)
    try:
        request = urllib2.urlopen(urlunparse((
            'http', 
            ZIPTAX_API_URL, 
            'request/%s' % ZIPTAX_API_VERSION,
            None,
            params,
            None
        )))
        request = load(request)
    except Exception, e:
        raise Ziptax_Failure(str(e))
    if request is False:
        raise Ziptax_Failure('UNKNOWN FAILURE')
    if request['rCode'] != 100:
        raise Ziptax_Failure(RESPONSE_CODES[request['rCode']])
    if len(request['results']) == 0:
        return False
    return request['results'][0]['taxSales']