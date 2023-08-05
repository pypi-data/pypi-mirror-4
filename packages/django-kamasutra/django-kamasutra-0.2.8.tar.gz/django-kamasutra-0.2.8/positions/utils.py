#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Credit: Troy Melhase https://github.com/natural

from django.conf import settings
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseServerError, )
from django.utils import simplejson as json


APP_JSON = 'application/json'
INDENT = 4
SUFFIX = ''

if getattr(settings, 'DEBUG'):
    INDENT = 4
    SUFFIX = '\n'


class JSONResponse(HttpResponse):
    """HTTP Response with automatic JSON serialization and content type."""
    def __init__(self, content={}, mimetype=None, status=None,
                 content_type=APP_JSON):
        if not isinstance(content, (basestring, )):
            content = json.dumps(content, indent=INDENT)
            content += SUFFIX
        HttpResponse.__init__(self, content, mimetype, status,
            content_type)


class JSONResponseBadRequest(HttpResponseBadRequest):
    """HTTP Bad Request with automatic JSON serialization and content type."""
    def __init__(self, content={}, mimetype=None, status=None,
                 content_type=APP_JSON):
        if not isinstance(content, (basestring, )):
            content = json.dumps(content, indent=INDENT)
            content += SUFFIX
        HttpResponseBadRequest.__init__(self, content, mimetype, status,
            content_type)


class JSONResponseServerError(HttpResponseServerError):
    """HTTP Server Error with automatic JSON serialization and content type."""
    def __init__(self, content={}, mimetype=None, status=None,
                 content_type=APP_JSON):
        if not isinstance(content, (basestring, )):
            content = json.dumps(content, indent=INDENT)
            content += SUFFIX
        HttpResponseServerError.__init__(self, content, mimetype, status,
            content_type)
