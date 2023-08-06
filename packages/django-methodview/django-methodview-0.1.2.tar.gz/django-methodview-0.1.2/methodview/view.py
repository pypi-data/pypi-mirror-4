#
# Copyright 2012 keyes.ie
#
# License: http://jkeyes.mit-license.org/
#

import inspect

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseNotAllowed
from django.template import loader
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

from .accept_header import AcceptHeader

def hasmethod(obj, method_name):
    if hasattr(obj, method_name):
        attr = getattr(obj, method_name)
        return inspect.ismethod(attr)
    return False

class HttpResponseNotImplemented(HttpResponse):
    status_code = 501

    def __init__(self, *args, **kwargs):
        HttpResponse.__init__(self, *args, **kwargs)

class HttpResponseNotAcceptable(HttpResponse):
    status_code = 406

    def __init__(self, *args, **kwargs):
        HttpResponse.__init__(self, *args, **kwargs)

ALLOWED_METHODS = ( 'GET', 'HEAD', 'POST', 'PUT')

class MethodView(object):

    def __init__(self, allowed=None, accepts=None):
        if allowed is None:
            allowed = ALLOWED_METHODS
        self._allowed_methods = [a.upper() for a in allowed]
        self._accepts = accepts
        self._method_supported = False
        
    def _get_handler(self, http_method, accept):
        self._methods = inspect.getmembers(self, inspect.ismethod)
        self._method_names = [method[0] for method in self._methods]
        for mname in self._method_names:
            if mname.lower().startswith(http_method):
                self._method_supported = True
        handler_name = None
        for media_range in accept:
            if media_range.any_media:
                # check for default first
                if http_method in self._method_names:
                    handler_name = http_method
                    break
                method_prefix = "%s_" % (http_method)
                for name in self._method_names:
                    if name.startswith(method_prefix):
                        handler_name = name
                        break
                if handler_name is None and http_method in self._method_names:
                    handler_name = http_method
            elif media_range.any_subtype:
                method_prefix = "%s_%s_" % (http_method, media_range.mtype)
                for name in self._method_names:
                    if name.startswith(method_prefix):
                        handler_name = name
                        break
            else:
                handler_name = "%s_%s_%s" % (http_method, media_range.mtype, media_range.subtype)
            if handler_name and hasmethod(self, handler_name):
                return getattr(self, handler_name)
        if hasmethod(self, http_method):
            return getattr(self, http_method)
        return None

    def __call__(self, request, *args, **kwargs):
        """
        Method dispatcher.
        """
        method_name = request.method
        if 'HTTP_ACCEPT' not in request.META:
            # From: http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html
            #     "If no Accept header field is present, then it is assumed 
            #      that the client accepts all media types."
            accept = AcceptHeader("*/*")
        else:
            accept = AcceptHeader(request.META['HTTP_ACCEPT'])

        if '_method' in request.REQUEST:
            method_name = request.REQUEST['_method']
        
        method_name = method_name.upper()
        if method_name in self._allowed_methods:
            handler_name = method_name.lower()
            handler = self._get_handler(handler_name, accept)
            if handler is None:
                # if the method is handled for the Resource but
                # an allowed MIME type handler is not found the
                # return a NotAcceptable
                # TODO: determine the response content 
                # See: http://labs.apache.org/webarch/http/draft-fielding-http/p2-semantics.html#status.406
                if self._method_supported:
                    return HttpResponseNotAcceptable()
                return HttpResponseNotImplemented()
            return handler(request, *args, **kwargs)
        return HttpResponseNotAllowed(self._allowed_methods)