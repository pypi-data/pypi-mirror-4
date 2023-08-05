# -*- coding: utf-8 -*-
from pyramid.view import view_config

from pyramid_rest.resource import Resource


hello = Resource('hello_world')

@hello.index()
def hello_index(context, request):
    return {'Hello': 'World!'}


@view_config(renderer='index.mako')
def index(context, request):
    return {}
