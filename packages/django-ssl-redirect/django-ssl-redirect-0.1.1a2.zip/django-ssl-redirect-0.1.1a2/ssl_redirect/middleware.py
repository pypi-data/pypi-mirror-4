from django.conf import settings
from django.http import HttpResponseRedirect, get_host


USE_SSL = getattr(settings, 'USE_SSL', True)
HTTPS_PATHS = getattr(settings, 'HTTPS_PATHS', [])
SSL = 'SSL'
SSLPORT = getattr(settings, 'SSL_PORT', None)


class SSLRedirectMiddleware:
    """
    This middleware answers the problem of redirecting to (and from) a SSL secured path
    by stating what paths should be secured in urls.py file. To secure a path, add the
    additional view_kwarg 'SSL':True to the view_kwargs.

    For example

    urlpatterns = patterns('some_site.some_app.views',
        (r'^test/secure/$','test_secure',{'SSL':True}),
         )

    All paths where 'SSL':False or where the kwarg of 'SSL' is not specified are routed
    to an unsecure path.

    For example

    urlpatterns = patterns('some_site.some_app.views',
        (r'^test/unsecure1/$','test_unsecure',{'SSL':False}),
        (r'^test/unsecure2/$','test_unsecure'),
         )

    Gotcha's : Redirects should only occur during GETs; this is due to the fact that
    POST data will get lost in the redirect.
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        if SSL in view_kwargs:
            secure = view_kwargs[SSL]
            del view_kwargs[SSL]
        else:
            secure = False

        if not USE_SSL:
            return

        if not secure:
            for path in HTTPS_PATHS:
                if request.path.startswith("/%s" % path):
                    secure = True
                    break

        if not secure == self._request_is_secure(request):
            return self._redirect(request, secure)

    def _request_is_secure(self, request):
        if request.is_secure():
            return True

        # Handle forwarded SSL (used at Webfaction)
        if 'HTTP_X_FORWARDED_SSL' in request.META:
            return request.META['HTTP_X_FORWARDED_SSL'] == 'on'

        # Handle an additional case of proxying SSL requests. This is useful for Media Temple's
        # Django container
        if 'HTTP_X_FORWARDED_HOST' in request.META and request.META['HTTP_X_FORWARDED_HOST'].endswith('443'):
            return True

        return False

    def _redirect(self, request, secure):
        if settings.DEBUG and request.method == 'POST':
            raise RuntimeError(
"""Django can't perform a SSL redirect while maintaining POST data.
Please structure your views so that redirects only occur during GETs.""")

        protocol = secure and "https" or "http"
        host = "%s://%s" % (protocol, get_host(request))
        # In certain proxying situations, we need to strip out the 443 port
        # in order to prevent inifinite redirects
        if not secure:
            host = host.replace(':443', '')
        if secure and SSLPORT:
            host = "%s:%s" % (host, SSLPORT)

        newurl = "%s%s" % (host, request.get_full_path())

        return HttpResponseRedirect(newurl)
