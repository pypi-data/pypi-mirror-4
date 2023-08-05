from functools import update_wrapper
from django import VERSION as DJANGO_VERSION
from django.http import HttpResponse, QueryDict
from django.utils.decorators import classonlymethod
from eggplant.utils.constants import HTTP_METHOD
from eggplant.views.exceptions import ViewError

class View(object):
    def __init__(self):
        pass

    @classonlymethod
    def view(cls, **init_kwargs):
        def view(request, *args, **kwargs):
            self = cls(**init_kwargs)

            # Automatically add 'head' method
            if hasattr(self, 'get') and not hasattr(self, 'head'):
                def _head(self, *args, **kwargs):
                    getattr(self, 'get')(*args, **kwargs)
                    self.response.content = ''
                setattr(self, 'head', _head)

            return self.handle(request, *args, **kwargs)

        # take name and docstring from class
        update_wrapper(view, cls, updated=())

        # and possible attributes set by decorators
        # like csrf_exempt from dispatch
        update_wrapper(view, cls.handle, assigned=())
        return view

    def handle(self, request, *args, **kwargs):
        self.request = request
        self.response = HttpResponse()

        # Check allowed http methods
        if request.method.upper() in HTTP_METHOD and \
           hasattr(self, request.method.lower()):
            handler = getattr(self, request.method.lower())
        else:
            handler = self.method_not_allowed

        # Extend django request query dict
        if request.method.upper() in ('PUT', 'DELETE'):
            if DJANGO_VERSION[1] >= 4:
                raw_body = self.request.body
            else:
                raw_body = self.request.raw_post_data
            setattr(self.request, request.method.upper(), QueryDict(raw_body))
        elif request.method.upper() == 'HEAD':
            setattr(self.request, 'HEAD', self.request.GET)

        # Go
        try:
            handler(*args, **kwargs)
        except ViewError, e:
            self.response.content = ''
            self.response.status_code = e.status_code

            error_handler = self.default_error_handler
            if e.error_handler is not None:
                error_handler = e.error_handler
            error_handler(e)

        return self.response

    def method_not_allowed(self):
        raise ViewError(405, 'HTTP %s Method is not allowed.'%self.request.method.upper())

    def default_error_handler(self, error_obj):
        self.response['Content-Type'] = 'text/plain'
        self.response.content = error_obj.message

    def lack_of_required_key(self, error_obj):
        self.default_error_handler(error_obj)

    def key_validation_failed(self, error_obj):
        self.default_error_handler(error_obj)
