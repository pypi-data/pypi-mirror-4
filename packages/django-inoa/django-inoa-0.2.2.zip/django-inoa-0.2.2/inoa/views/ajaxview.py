# -*- coding: utf-8 -*-

from django.http import HttpResponseBadRequest, HttpResponse,\
    HttpResponseNotFound, Http404
from django.shortcuts import render
from django.views.generic.base import View
from functools import partial
from inoa.http.responses import JsonResponse


class AjaxView(View):
    """
    Returns the rendered HTML if the request.is_ajax() == False, otherwise returns a JsonResponse of the context.

    Define httpmethod_context(self, request) methods [e.g. get_context] that return a context object, which should be
    dictionary-like objects that SimpleJson knows how to serialize, or None (which will be converted to an empty dictionary).

    Set a template_name attribute in your class with the template name for this view.
    If not set, non-ajax requests will return an HTTP error.
    
    You must also create two templates in your root template folder: '4xx.html' and '5xx.html',
    which will be called when your view returns an error code in these ranges.
    
    If you want to return an HTTP code other than 200 OK, return a 2-tuple (code, context) instead.
    Code can be either an integer or a subclass of django.http.HttpResponse.
    If you don't need to supply a context, you can simply return a subclass of HttpResponse. 
    
    If you want to return a specific HttpResponse instance in your httpmethod_context() method,
    raise a ResponseWrapperException with your response wrapped in.
    """
    
    class ResponseWrapperException(Exception):
        """Wraps a HttpResponse object."""
        def __init__(self, response):
            self.response = response

    def __init__(self, *args, **kwargs):
        super(AjaxView, self).__init__(*args, **kwargs)

        # Create the get(), post(), etc methods from their get_context(), etc equivalents.
        for m in self.http_method_names:
            if hasattr(self, m + '_context'):
                context_method = getattr(self, m + '_context')
                setattr(self, m, partial(self.base_view, context_method))

    def base_view(self, context_method, request, *args, **kwargs):
        if not request.is_ajax() and not hasattr(self, 'template_name'):
            return HttpResponseBadRequest

        try:
            data = context_method(request, *args, **kwargs)
        except self.ResponseWrapperException as ex:
            return ex.response
        except Http404 as ex:
            data = HttpResponseNotFound
        
        success_code = HttpResponse.status_code
        if isinstance(data, HttpResponse) or (isinstance(data, type) and issubclass(data, HttpResponse)):
            status_code = data.status_code
            ctx = {}
        elif isinstance(data, tuple) and len(data) == 2:
            status_code = getattr(data[0], 'status_code', data[0])
            ctx = data[1] or {}
        else:
            status_code = success_code
            ctx = data or {}
        
        if request.is_ajax():
            response = JsonResponse(ctx)
        elif status_code < 400:
            response = render(request, self.template_name, ctx)
        else:
            error_ctx = {'request_path': request.path, 'http_status_code': status_code}
            error_ctx.update(ctx)
            error_template = '4xx.html' if status_code < 500 else '5xx.html'
            response = render(request, error_template, error_ctx)
        response.status_code = status_code
        return response
