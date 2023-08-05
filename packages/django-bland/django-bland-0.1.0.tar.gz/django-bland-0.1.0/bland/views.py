import os
import time
from django.http import HttpResponseNotFound
from django.shortcuts import render_to_response
from django.utils.http import http_date
from .models import Resource, NotFound


def root(cms_root):
    """
    A view that will render a basic site based on the
    directory layout of the provided path
    """
    def view(request, path):
        try:
            page = Resource.locate(os.path.join(cms_root, path))
        except NotFound as e:
            return HttpResponseNotFound(str(e))
        response = render_to_response('bland/resource.html',
            {'page': page})
        response['Last-Modified'] = _http_date(page.date())
        return response
    return view


def _http_date(datetime):
    """
    the ludicrous amount of work required in python date/time libs
    """
    return http_date(time.mktime(datetime.timetuple()))
