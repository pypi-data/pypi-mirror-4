"""
http://djangosnippets.org/snippets/1351/

Wrote this some time ago when I couldn't find one already completed.
Came up in the IRC channel so I decided to post it.

Easy enough to use.

>>> from ssldecorator import ssl_required

>>> @ssl_required
... def your_view(request):
...     ''' your code here '''

You can place a variable in your settings.py to change the SSL domain
(ie, if you have SSL running on secure.yourdomain.com instead of www.yourdomain.com)

>>> SSL_DOMAIN = 'https://secure.yourdomain.com'

Note: please include a proper URL. If https isn't used, the decorator will add it.
"""

import urlparse
from django.conf import settings
from django.http import HttpResponseRedirect

def ssl_required(view_func):
    def _checkssl(request, *args, **kwargs):
        if not settings.DEBUG and not request.is_secure():
            if hasattr(settings, 'SSL_DOMAIN'):
                url_str = urlparse.urljoin(
                    settings.SSL_DOMAIN,
                    request.get_full_path()
                )
            else:
                url_str = request.build_absolute_uri()
            url_str = url_str.replace('http://', 'https://')
            return HttpResponseRedirect(url_str)

        return view_func(request, *args, **kwargs)
    return _checkssl