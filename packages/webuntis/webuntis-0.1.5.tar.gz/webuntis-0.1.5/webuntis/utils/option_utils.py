'''
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''
from __future__ import unicode_literals
import re
import logging
try:
    from urllib import parse as urlparse  # Python 3
except ImportError:
    import urlparse  # Python 2


def whatever(value):
    return value


def server(url):
    if not url:
        return url  # either it's None or we have a dictionary

    if not re.match(r'^http(s?)\:\/\/', url):  # if we just have the hostname
        logging.debug('The URL given doesn\'t seem to be a valid URL, just '
                      'gonna prepend "http://"')

        # append the http prefix and hope for the best
        url = 'http://' + url

    urlobj = urlparse.urlparse(url)

    if not urlobj.scheme or not urlobj.netloc:
        # urlparse failed
        raise ValueError('Not a valid URL or hostname')

    if not re.match(r'^[a-zA-Z0-9\.\:-_]+$', urlobj.netloc):
        # That's not even a valid hostname
        raise ValueError('Not a valid hostname')

    if urlobj.path == '/':
        logging.warning('You specified that the API endpoint should be "/".'
                        'That is uncommon. If you didn\'t mean to do so,'
                        'remove the slash at the end of your "server"'
                        'parameter.')

    return urlobj.scheme + \
        '://' + \
        urlobj.netloc + \
        (urlobj.path or '/WebUntis/jsonrpc.do')


def string(value):
    if value is None:
        return None

    return value

options = {
    'username': string,
    'password': string,
    'jsessionid': string,
    'school': whatever,
    'server': server,
    'useragent': whatever,
    'login_repeat': int
}
