# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4
# GPL 2012
from __future__ import with_statement

import cookielib
import gzip
import json
import StringIO
import urllib2


__version__ = 0.0
__license__ = 'GPL 3'
__copyright__ = '2012, bd <code@basedata.org>'
__docformat__ = 'restructuredtext en'

class BaseData(object):
    __version__ = __version__
    __name__ = 'basedata'
    DEBUG = False
    debuglevel = 0

    def __init__(self, url=None):
        if not url:
            url = 'https://basedata.org/'
        if not url.endswith('/'):
            url = url + '/'
        self._url = url
        self._cj = cookielib.CookieJar()
        self._opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self._cj),
                                            urllib2.HTTPHandler(debuglevel=self.debuglevel))
        self._opener.addheaders = [
            ('User-Agent', '%s/%s' % (self.__name__, self.__version__))
        ]
        self._loggedin = False

    def login(self, username, password):
        r = self._request('login', {'username': username, 'password': password})
        self._loggedin = r['username'] == username
        return self._loggedin

    def get(self, query):
        r = self._request('get', query)
        return r

    def set(self, query, update):
        if not self._loggedin:
            raise Exception, 'you have to login to write to base data'
        return self._request('set', {'query': query, 'update': update})

    def log(self, query):
        return self._request('log', query)

    def _request(self, action, data):
        url = self._url
        body = json.dumps({
            'action': action,
            'data': data
        })
        request = urllib2.Request(str(url))
        request.add_header('Content-Type', 'application/json')
        request.add_header('Content-Length', str(len(body)))
        request.add_header('Accept-Encoding', 'gzip, deflate')
        request.add_data(body)
        try:
            f = self._opener.open(request)
        except urllib2.HTTPError, e:
            if self.DEBUG:
                with open('/tmp/basedata_error.html', 'w') as f:
                    f.write(e.read())
            raise e
        result = f.read()
        if f.headers.get('content-encoding', None) == 'gzip':
            result = gzip.GzipFile(fileobj=StringIO.StringIO(result)).read()
        result = result.decode('utf-8')
        result = json.loads(result)
        if 'error' in result:
            raise Exception, result
        return result
