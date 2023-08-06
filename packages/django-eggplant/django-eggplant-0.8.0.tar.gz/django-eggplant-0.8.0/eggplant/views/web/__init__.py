"""
Copyright 2012 Dian-Je Tsai, Cramdroid, and Wantoto Inc

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import render
from eggplant.views import View


class HTMLView(View):
    def __init__(self, *args, **kwargs):
        super(HTMLView, self).__init__(*args, **kwargs)
        self.template_name = kwargs.get('template_name', None)

    def get(self, *args, **kwargs):
        if self.template_name is not None:
            context = {}
            context.update(self.init_kwargs)
            context.update(kwargs)
            context.update(self.request.GET)
            self.response = render(self.request, self.template_name, context)
        else:
            raise ImproperlyConfigured('Template name is undefined.')
