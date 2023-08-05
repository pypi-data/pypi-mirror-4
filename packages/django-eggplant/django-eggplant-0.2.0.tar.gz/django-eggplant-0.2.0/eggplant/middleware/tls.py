"""
http://djangosnippets.org/snippets/2282/

Allows url patterns to include a boolean indicating whether a view requires
TLS(SSL).  The accompanying middleware handles the redirects needed to make
sure that it upholds this requirement.

WARNING: this monkey-patches some Django internals and is difficult to test
since Django's TestClient does not support TLS.  If you use this make sure you
test it thouroughly.

Add this to your Django settings::

    USE_TLS = True   # The default for this setting is False.

URL pattern usage::

    url(r'^login$', 'myproject.login.index',
        {'require_tls': True}, name='login-index'),

Use ``require_tls`` True to force the middleware to perform redirects needed to
make sure your are serving this view using https.

Use ``require_tls`` False to force the middleware to redirect to http.  Be
careful with this setting, this may not behave as you expect.  If you don't
care if the view is served via https or http then do not include
``require_tls`` in the pattern.

If you wish to have every view in the site served with TLS then specify the
following Django setting::

    ALWAYS_USE_TLS = True   # Django setting, use TLS for every view

"""
from django.conf import settings
from django.core import urlresolvers
from django.http import HttpResponsePermanentRedirect
from django.http import get_host
from django.utils.encoding import smart_str

ALWAYS_USE_TLS = getattr(settings, 'ALWAYS_USE_TLS', False)
USE_TLS = getattr(settings, 'HTTPS_SUPPORT', ALWAYS_USE_TLS)


def resolve_pattern(path, urlconf=None):
    """
    Works the same as Django's url resolver but instead of return a view
    function that handles a specific path it gives you the pattern that matches
    it
    """
    return urlresolvers.get_resolver(urlconf).resolve_pattern(path)


def resolve_pattern_method(self, path):
    """
    Monkey-patchable to the RegexURLResolver class

    The difference is that this method will return the pattern instead of what
    Django's RegexURLResolver.resolve returns
    """
    tried = []
    match = self.regex.search(path)
    if match:
        new_path = path[match.end():]
        for pattern in self.url_patterns:
            try:
                if hasattr(pattern, 'resolve_pattern'):
                    # Use our resolve_pattern method
                    sub_match = pattern.resolve_pattern(new_path)
                    if isinstance(sub_match, urlresolvers.RegexURLPattern):
                        return sub_match
                else:
                    sub_match = pattern.resolve(new_path)
            except urlresolvers.Resolver404, e:
                sub_tried = e.args[0].get('tried')
                if sub_tried is not None:
                    tried.extend([(pattern.regex.pattern + '   ' + t) for t in sub_tried])
                else:
                    tried.append(pattern.regex.pattern)
            else:
                if sub_match:
                    if hasattr(pattern, 'callback'):
                        # Found our pattern
                        return pattern
                    sub_match_dict = dict([(smart_str(k), v) for k, v in match.groupdict().items()])
                    sub_match_dict.update(self.default_kwargs)
                    for k, v in sub_match[2].iteritems():
                        sub_match_dict[smart_str(k)] = v
                    return sub_match[0], sub_match[1], sub_match_dict
                tried.append(pattern.regex.pattern)
        raise urlresolvers.Resolver404, {'tried': tried, 'path': new_path}
    raise urlresolvers.Resolver404, {'path' : path}

# Monkey patch the additional methods
urlresolvers.RegexURLResolver.resolve_pattern = resolve_pattern_method


def reverse_decorator(func):
    def inner(*args, **kwargs):
        if 'request' in kwargs:
            request = kwargs['request']
            del kwargs['request']
        else:
            request = None

        # Call the real reverse function
        abs_path = func(*args, **kwargs)

        if not request or not USE_TLS:
            # Short-circuit, no need to continue becuase there is no request we
            # can get smart with or TLS is turned off
            return abs_path

        # Let's figure out if we need this URL to be secure or not
        pattern = resolve_pattern(abs_path)
        if 'require_tls' in pattern.default_args:
            secure = pattern.default_args['require_tls']
        else:
            secure = None

        if not secure is None and request and \
           not secure == is_secure(request):
            # Secure indicates either http or https and the request is not
            # currently being served that way
            protocol = 'https' if secure else 'http'
            abs_path = '%s://%s%s' % (protocol, get_host(request), abs_path,)
        return abs_path
    return inner
urlresolvers.reverse = reverse_decorator(urlresolvers.reverse)


def is_secure(request):
    """
    Determines if the given request is over HTTPS or not
    """
    if request.is_secure():
        return True

    return False


class TlsRedirect(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if 'require_tls' in view_kwargs:
            secure = view_kwargs['require_tls']
            del view_kwargs['require_tls']
        else:
            secure = None

        if not any([USE_TLS, ALWAYS_USE_TLS]):
            return None

        if ALWAYS_USE_TLS:
            # This site is setup to always use TLS so we set the secure bit to
            # always be true
            secure = True

        # If secure is None, the require_tls was not present in the view
        # keyword args at all.  In this case, we don't want to redirect.
        # Leaving this keyword off probably indicates that the particular url
        # doesn't require http or https, we go with whatever we got
        if not secure is None and \
           not secure == is_secure(request):
            return self._redirect(request, secure)

    def _redirect(self, request, secure):
        #protocol = secure and 'https' or 'http'
        protocol = ''
        if secure: protocol = 'https'
        else: protocol = 'http'

        newurl = '%s://%s%s' % (
            protocol, get_host(request), request.get_full_path(),)
        # replace for dev server
        if settings.DEBUG and secure:
            newurl = newurl.replace(':8000', ':8443')
        if settings.DEBUG and request.method == 'POST':
            raise RuntimeError('Django can\'t perform a TLS redirect while '
                'maintaining POST data.  Please structure your views so that '
                'redirects only occur during GETs.')

        return HttpResponsePermanentRedirect(newurl)