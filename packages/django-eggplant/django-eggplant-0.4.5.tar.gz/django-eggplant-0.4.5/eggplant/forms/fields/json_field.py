"""
Copyright (c) 2012, Derek Schaefer.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

    1) Redistributions of source code must retain the above copyright notice,
       this list of conditions and the following disclaimer.
    2) Redistributions in binary form must reproduce the above copyright
       notice, this list of conditions and the following disclaimer in the
       documentation and/or other materials provided with the distribution.
    3) Neither the name of django-json-field nor the names of its contributors
       may be used to endorse or promote products derived from this software
       without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

https://github.com/derek-schaefer/django-json-field/

"""

import json
from django.forms import fields, util
#from django.utils import simplejson as json

import datetime

class JSONFormField(fields.Field):

    def __init__(self, *args, **kwargs):
        self.simple = kwargs.pop('simple', False)
        self.encoder_kwargs = kwargs.pop('encoder_kwargs', {})
        self.decoder_kwargs = kwargs.pop('decoder_kwargs', {})
        super(JSONFormField, self).__init__(*args, **kwargs)

    def clean(self, value):
        # Have to jump through a few hoops to make this reliable
        value = super(JSONFormField, self).clean(value)

        # allow an empty value on an optional field
        if value is None:
            return value

        ## Got to get rid of newlines for validation to work
        # Data newlines are escaped so this is safe
        value = value.replace('\r', '').replace('\n', '')

        json_globals = { # safety first!
            '__builtins__': None,
        }
        if not self.simple: # optional restriction
            json_globals.update({'datetime':datetime})
        json_locals = { # value compatibility
            'null': None,
            'true': True,
            'false': False,
        }
        try:
            value = json.dumps(eval(value, json_globals, json_locals), **self.encoder_kwargs)
        except Exception, e: # eval can throw many different errors
            raise util.ValidationError('%s (Caught "%s")' % (self.help_text, e))

        try:
            json.loads(value, **self.decoder_kwargs)
        except ValueError, e:
            raise util.ValidationError('%s (Caught "%s")' % (self.help_text, e))

        return value