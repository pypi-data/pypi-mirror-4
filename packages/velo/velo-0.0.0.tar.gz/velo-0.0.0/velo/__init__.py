# -*- coding: utf-8 -*-
import logging

import pkg_resources

from pyramid.config import Configurator

log = logging.getLogger(__name__)


def main(global_config, **settings):
    log.info('Starting...')
    config = Configurator(settings=settings)
    config.include('velo')
    log.info('Ready to serve...')
    return config.make_wsgi_app()


def includeme(config):
    version = pkg_resources.get_distribution('velo').version

    config.include('pyramid_rest')

    config.add_static_view('/static/%s' % version, 'velo:static')
    config.add_static_view('/static/{version:\d\.\d\.\d}', 'velo:static')

    config.scan('velo.views')
