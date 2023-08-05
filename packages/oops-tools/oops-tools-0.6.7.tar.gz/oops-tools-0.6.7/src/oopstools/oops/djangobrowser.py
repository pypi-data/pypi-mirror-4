# Copyright 2008-2011 Canonical Ltd.  All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""Django integration for zope.testbrowser."""

__metaclass__ = type
__all__ = ["Browser"]

# don't use cStringIO because it doesn't support unicode
from StringIO import StringIO
import httplib
import sys
import urllib2

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.core.signals import got_request_exception
from django.http import HttpRequest
from django.template import TemplateDoesNotExist
from django.test.client import ClientHandler, FakePayload
import mechanize
from zope.interface import implements
from zope.testbrowser import browser
from zope.testbrowser.interfaces import IBrowser


class DjangoConnection:
    """A `urllib2` compatible connection object.

    This is the httplib.HTTPConnection used by the HTTPHandler below
    """

    def __init__(self, host, timeout=None):
        self.handler = ClientHandler()
        self.host = host
        self.exc_info = None
        self.timeout = timeout

    def set_debuglevel(self, level):
        """Required by urllib2"""
        pass

    def _quote(self, url):
        """Fills in spaces with %20

        the publisher expects to be able to split on whitespace, so we have
        to make sure there is none in the URL
        """
        return url.replace(' ', '%20')

    def store_exc_info(self, **kwargs):
        """Return information about the most recent exception caught
        by an except clause in the current stack frame or in an older
        stack frame."""
        self.exc_info = sys.exc_info()

    def request(self, method, url, body=None, headers=None):
        """ Send a complete request to the server."""
        if '?' in url:
            path, query = url.split('?', 1)
        else:
            path = url
            query = ''
        environ = dict(
            REQUEST_METHOD=method,
            SCRIPT_NAME='',
            PATH_INFO=path,
            REMOTE_ADDR="127.0.0.1",
            QUERY_STRING=query,
            SERVER_NAME=self.host,
            SERVER_PORT='80',
            SERVER_PROTOCOL='HTTP/1.1')
        if headers is not None:
            for header, value in headers.items():
                if header.lower() == 'content-type':
                    environ['CONTENT_TYPE'] = value
                elif header.lower() == 'content-length':
                    environ['CONTENT_LENGTH'] = value
                else:
                    header = 'HTTP_' + header.upper().replace('-', '_')
                    environ[header] = value
        if body is not None:
            environ['wsgi.input'] = FakePayload(body)
        #XXX Hack to make djangobrowser.py work with Django 1.3
        else:
            environ['wsgi.input'] = FakePayload('')

        got_request_exception.connect(self.store_exc_info)
        try:
            #pylint: disable-msg=W0201
            #This is normal
            self.response = self.handler(environ)
            #pylint: enable-msg=W0201
        except TemplateDoesNotExist, exc:
            if exc.args != ('500.html',):
                raise

        if self.exc_info:
            try:
                raise self.exc_info[1], None, self.exc_info[2]
            finally:
                self.exc_info = None

    def getresponse(self):
        """Return a `urllib2` compatible response object."""
        return DjangoResponse(self.response)


class DjangoResponse:
    """A `urllib2` compatible response object."""

    def __init__(self, django_response):
        self.content = django_response.content
        self.status = django_response.status_code
        self.reason = '???'
        headers = ['%s: %s' % header for header in django_response.items()]
        headers.append(django_response.cookies.output())

        self.msg = httplib.HTTPMessage(StringIO('\r\n'.join(headers) + '\r\n'))
        self.content_as_file = StringIO(self.content)

    def read(self, amt=None):
        """Reads the response stream"""
        return self.content_as_file.read(amt)

    def close(self):
        """Close the response stream"""
        pass


class DjangoHTTPHandler(urllib2.HTTPHandler):
    """Special HTTP handler to use the Django testing client."""

    def http_request(self, req):
        """Sets the content type and calls the base http_request"""
        #look at data and set content type
        if req.has_data():
            data = req.get_data()
            if isinstance(data, dict):
                req.add_data(data['body'])
                req.add_unredirected_header('Content-type',
                                            data['content-type'])
                req.set_method(data.get('method'))
        return urllib2.AbstractHTTPHandler.do_request_(self, req)

    def http_open(self, req):
        """Open an HTTP connection having a ``urllib2`` request."""
        # Here we connect to the publisher.
        return self.do_open(DjangoConnection, req)


class RESTRequest(urllib2.Request):
    """
    Let the HTTP method be manually settable, in addition to being
    autodetected from the presence of a data body.
    """

    def __init__(self, url, data=None, **kwargs):
        urllib2.Request.__init__(self, url, data, **kwargs)
        # reproduce the previous behavior of the get_method method
        self.method = 'GET' if data is None else 'POST'

    def set_method(self, method=None):
        """Manually set the HTTP method"""
        if method:
            self.method = method

    def get_method(self):
        """Get the HTTP method"""
        return self.method


class DjangoMechanizeBrowser(mechanize.Browser):
    """Special `mechanize` browser using the Django client handler."""

    default_schemes = ['http']
    default_others = ['_http_error', '_http_request_upgrade',
                      '_http_default_error']
    default_features = ['_redirect', '_cookies', '_referer', '_refresh',
                        '_equiv', '_basicauth', '_digestauth']

    def __init__(self, *args, **kws):
        inherited_handlers = ['_unknown', '_http_error',
            '_http_request_upgrade', '_http_default_error', '_basicauth',
            '_digestauth', '_redirect', '_cookies', '_referer',
            '_refresh', '_equiv', '_gzip']

        self.handler_classes = {"http": DjangoHTTPHandler}
        for name in inherited_handlers:
            self.handler_classes[name] = mechanize.Browser.handler_classes[name]

        mechanize.Browser.__init__(self, *args, **kws)

    def open(self, url, data=None):
        """If any data, wrap url with our own RESTRequest."""
        url_or_req = url if data is None else RESTRequest(url, data)
        return self._mech_open(url_or_req, data)

class Browser(browser.Browser):
    """A Zope `testbrowser` instance that uses the Django test client."""
    implements(IBrowser)

    def __init__(self, url=None):
        mech_browser = DjangoMechanizeBrowser()
        self.cookiejar = mechanize.CookieJar()
        mech_browser.set_cookiejar(self.cookiejar)
        super(Browser, self).__init__(url=url, mech_browser=mech_browser)

    @property
    def session(self):
        """The django browser session"""
        if 'django.contrib.sessions' in settings.INSTALLED_APPS:
            engine = __import__(settings.SESSION_ENGINE, {}, {}, [''])
            for cookie in self.cookiejar:
                if cookie.name == settings.SESSION_COOKIE_NAME:
                    return engine.SessionStore(cookie.value)
        return {}

    def login(self, **credentials):
        """Log in as a particular user."""
        user = authenticate(**credentials)
        if (user and user.is_active and
            'django.contrib.sessions' in settings.INSTALLED_APPS):
            engine = __import__(settings.SESSION_ENGINE, {}, {}, [''])

            # Create a fake request to store login details.
            request = HttpRequest()
            if self.session:
                request.session = self.session
            else:
                request.session = engine.SessionStore()
            login(request, user)

            # Set the cookie to represent the session.
            cookie_string = '%s=%s; path=/' % (
                settings.SESSION_COOKIE_NAME, request.session.session_key)
            if settings.SESSION_COOKIE_DOMAIN:
                cookie_string += '; domain=%s' % settings.SESSION_COOKIE_DOMAIN
            if settings.SESSION_COOKIE_SECURE:
                cookie_string += '; secure'
            self.mech_browser.set_cookie(cookie_string)

            # Save the session values.
            request.session.save()

            return True
        else:
            return False

    def logout(self):
        """Log out."""
        engine = __import__(settings.SESSION_ENGINE, {}, {}, [''])
        for cookie in self.cookiejar:
            if cookie.name == settings.SESSION_COOKIE_NAME:
                engine.SessionStore(cookie.value).delete()
        self.cookiejar.clear()
