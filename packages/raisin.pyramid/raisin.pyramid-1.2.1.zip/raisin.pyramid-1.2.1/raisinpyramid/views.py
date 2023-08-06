"""Views for boxes and pages"""

import re
from webob import Response
from webob.exc import HTTPNotFound

from pyramid.security import authenticated_userid
from pyramid.static import static_view

from pyramid.renderers import render_to_response

from raisin.restyler.page import Page
from raisin.restyler.box import Box

from raisinpyramid import security

STATIC_VIEW_OF_ICO = static_view('raisin.page:templates/static/',
                                 cache_max_age=3600)

VALID_KEY = re.compile('^[A-Za-z_]*$')
VALID_VALUE = re.compile('^[A-Za-z0-9-_\.\+]*$')


def validate(matchdict):
    """Validate the matchdict"""
    for key, value in matchdict.items():
        if not VALID_KEY.match(key):
            raise AttributeError
        if not VALID_VALUE.match(value):
            raise AttributeError


def box_html_view(request):
    """View for boxes rendered as html using an internal template renderer.

    Returns a response object.
    """
    validate(request.matchdict)
    logged_in = authenticated_userid(request)
    security.check_permission(request, logged_in)
    context = Box(request)
    template = 'raisin.page:templates/box.pt'
    value = dict(context=context)
    response = render_to_response(template, value)
    return response


def box_csv_view(request):
    """View for boxes rendered as csv.

    Returns a response object.
    """
    validate(request.matchdict)
    logged_in = authenticated_userid(request)
    security.check_permission(request, logged_in)
    context = Box(request)
    if context.body is None:
        return HTTPNotFound()
    else:
        response = Response()
        response.body = context.body
        response.content_type = 'text/csv'
    return response


def page_view(request):
    """View for pages using a template renderer defined outside of this
    view callable.

    Returns a dictionary whose itemw will be used as top-level names
    in the template.
    """
    validate(request.matchdict)
    logged_in = authenticated_userid(request)
    security.check_permission(request, logged_in)
    context = Page(request)

    return dict(
        context=context,
        logged_in=logged_in,
        )
