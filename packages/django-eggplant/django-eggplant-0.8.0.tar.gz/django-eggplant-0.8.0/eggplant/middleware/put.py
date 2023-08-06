from django import VERSION as DJANGO_VERSION
from django.http import QueryDict


class PutRequestMiddleware(object):
    def process_request(self, request):
        if request.method.upper() == 'PUT':
            if not hasattr(request, 'PUT'):
                if DJANGO_VERSION >= (1, 4):
                    raw_body = request.body
                else:
                    raw_body = request.raw_post_data
                setattr(request, request.method.upper(), QueryDict(raw_body))
        elif request.method.upper() not in ('POST', 'GET'):
            setattr(request, request.method.upper(), request.GET)
