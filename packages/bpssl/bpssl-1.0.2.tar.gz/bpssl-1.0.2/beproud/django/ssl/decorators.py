#:coding=utf-8:

from django.utils.decorators import decorator_from_middleware

from beproud.django.ssl.middleware import SSLMiddleware

__all__ = ('ssl_view',)

def ssl_view(view):
    """
    Requires that a view be accessed via SSL(HTTPS). Calls
    to this view where request.is_secure() returns False
    will redirect to the SSL(HTTPS) version of the view.
    """
    wrapped_view = decorator_from_middleware(SSLMiddleware)(view)
    # Exempt this view from processing by middleware.
    wrapped_view.ssl_exempt = True
    return wrapped_view
