# -*- coding: utf-8 -*-
import logging
import pprint

from pyramid.authorization import ACLAuthorizationPolicy

from pyramid_facebook.security import FacebookAuthenticationPolicy

log = logging.getLogger(__name__)


def includeme(config):
    """Executed when including ``pyramid_facebook``.

    ``pyramid_facebook`` setup:

    * ACL Authorization with :class:`~pyramid.authorization.ACLAuthorizationPolicy`
      using :meth:`config.set_authorization_policy <pyramid.config.Configurator.set_authorization_policy>`
    * Authentication with :class:`~pyramid_facebook.security.FacebookAuthenticationPolicy`
      using :meth:`config.set_authentication_policy <pyramid.config.Configurator.set_authentication_policy>`

    """
    settings = config.registry.settings
    log.debug('Configuration settings: %s', pprint.pformat(settings))

    config.set_authentication_policy(FacebookAuthenticationPolicy())
    config.set_authorization_policy(ACLAuthorizationPolicy())

    facebook_path = '/%s' % settings['facebook.namespace']

    config.include('pyramid_facebook.auth',      route_prefix=facebook_path)
    config.include('pyramid_facebook.canvas',    route_prefix=facebook_path)
    config.include('pyramid_facebook.credits',   route_prefix=facebook_path)
    config.include('pyramid_facebook.real_time', route_prefix=facebook_path)
    config.commit()
