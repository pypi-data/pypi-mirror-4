# vim:fileencoding=utf8
import re

from django.http import HttpResponseRedirect, Http404
from django.conf import settings as django_settings
from django.core import urlresolvers

from beproud.django.ssl.conf import settings

__all__ = (
    'SSLMiddleware',
    'SSLRedirectMiddleware',
    'SSLProxyMiddleware',
)

class SSLMiddleware(object):
    """
    Redirects all http requests to the equivalent https url
    """
    def process_request(self, request):
        """
        Processes the request and redirects to the appropriate
        url if necessary. 
        
        Processing is done by process_request rather than
        process_view because if a url is not matched
        then process_view is not called and some badly implemented
        middleware such as FlatpageFallbackMiddleware could return
        responses which would end up bypassing the SSLMiddleware
        processing.
        """
        # Resolve the view from the path_info. urlresolvers info
        # is cached so this isn't too expensive.
        callback = None
        callback_args = None
        callback_kwargs = None
        try:
            callback, callback_args, callback_kwargs = urlresolvers.resolve(request.path_info)

            # If the view exists but we aren't handling it then return immediately
            # Whether the URL is handled or not doesn't matter
            if not self.is_handle_view(request, callback, callback_args, callback_kwargs):
                return
        except Http404:
            pass

        # Only handle the request if either the view doesn't exist and handle_url==True
        # or the view exists and is_handle_view==True and handle_url==True
        handle_url = self.is_handle_url(request)
        if handle_url:
            secure = self.is_secure_url(request)
            # If the request is https but ssl is not required redirect to http
            # If the request is http but ssl is required redirect to https
            if not secure == self.is_secure_request(request):
                return self._redirect(request, secure)

    def is_handle_url(self, request):
        """
        Return true if this URL should be handled. The request
        may still be handled if the view uses the ssl_view decorator.
        """
        return settings.USE_SSL

    def is_handle_view(self, request, callback, callback_args, callback_kwargs):
        """
        Returns whether the view should be handled. The request
        may still be handled if the view uses the ssl_view decorator.
        """
        return settings.USE_SSL

    def is_secure_url(self, request):
        """
        Returns True when the requested URL should only be accessed
        by secure requests.
        """
        return True

    def is_secure_request(self, request):
        """
        Returns True when the request is a secure request.
        """
        return request.is_secure()

    def _redirect(self, request, secure):
        """
        Redirect to the proper http or https URL.
        """
        # TODO: Use django site framework instead of HTTP_HOST/SSL_HOST?
        protocol = secure and "https" or "http"
        if secure:
            host = getattr(django_settings, 'SSL_HOST', request.get_host())
        else:
            host = getattr(django_settings, 'HTTP_HOST', request.get_host())
        newurl = "%s://%s%s" % (protocol,host,request.get_full_path())
        if django_settings.DEBUG and request.method == 'POST':
            raise RuntimeError, \
        """Django can't perform a SSL redirect while maintaining POST data.
           Please structure your views so that redirects only occur during GETs."""

        return HttpResponseRedirect(newurl)

class SSLRedirectMiddleware(SSLMiddleware):
    """
    Redirects all http requests directed at urls matching regular expressions
    set in the SSL_URLS in settings.py to the equivalent https url.
    """

    def __init__(self, urls=None, ignore_urls=None):
        if not urls:
            urls = settings.SSL_URLS
        self.urls = map(lambda u: re.compile(u) if isinstance(u, basestring) else u, urls)
        if not ignore_urls:
            ignore_urls = settings.SSL_IGNORE_URLS
        self.ignore_urls = map(lambda u: re.compile(u) if isinstance(u, basestring) else u, ignore_urls)

    def is_handle_url(self, request):
        """
        Only handle urls that are not in SSL_IGNORE_URLS
        """
        for url in self.ignore_urls:
            if url.match(request.path_info):
                return False
        return True

    def is_handle_view(self, request, callback, callback_args, callback_kwargs):
        """
        Don't handle views that are marked as ssl_exempt
        """
        return settings.USE_SSL and not getattr(callback, 'ssl_exempt', False)

    def is_secure_url(self, request):
        """
        Return True if the requested url matches a URL
        in SSL_URLS
        """
        secure = False
        for url in self.urls:
            if url.match(request.path_info):
                secure = True
                break
        return secure

class SSLProxyMiddleware(object):
    """
    Patches the request object so that is_secure() returns True
    when using an HTTP Proxy and the HTTP header defined by the
    SSL_REQUEST_HEADER setting is set to 'on' or 'https'. This
    way a header can be set in the style of HTTPS=on or PROTOCOL=https

    Typical settings for the SSL_REQUEST_HEADER setting would be
    HTTP_X_FORWARDED_SSL or HTTP_X_FORWARDED_PROTOCOL.

    This middleware should be set as early as possible in your
    MIDDLEWARE_CLASSES setting.
    """
    def __init__(self, header_name=None, header_value=None):
        default_header_name, default_header_value = settings.SSL_REQUEST_HEADER
        if not header_name:
            header_name = default_header_name
        if not header_value:
            header_value = default_header_value
        self.header_name = header_name.upper()
        self.header_value = header_value

    def process_request(self, request):
        if self.header_name:
            if request.META.get(self.header_name,'').lower() == self.header_value.lower():
                request.is_secure = lambda: True

