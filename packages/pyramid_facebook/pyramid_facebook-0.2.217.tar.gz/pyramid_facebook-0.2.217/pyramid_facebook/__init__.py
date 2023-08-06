# -*- coding: utf-8 -*-
import logging


log = logging.getLogger(__name__)


def includeme(config):
    config.include('pyramid_contextauth')

    settings = config.registry.settings

    path = '/%s' % settings['facebook.namespace']

    config.include('pyramid_facebook.predicates', route_prefix=path)
    config.include('pyramid_facebook.security', route_prefix=path)
    config.include('pyramid_facebook.auth', route_prefix=path)
    config.include('pyramid_facebook.canvas', route_prefix=path)
    config.include('pyramid_facebook.credits', route_prefix=path)
    config.include('pyramid_facebook.real_time', route_prefix=path)
    config.commit()
