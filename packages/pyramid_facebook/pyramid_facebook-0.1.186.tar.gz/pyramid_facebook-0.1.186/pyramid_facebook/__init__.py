# -*- coding: utf-8 -*-
import logging


log = logging.getLogger(__name__)


def includeme(config):
    """Executed when including ``pyramid_facebook``.

    ``pyramid_facebook`` setup:

    * ACL Authorization with :class:`~pyramid.authorization
      .ACLAuthorizationPolicy` using :meth:`config.set_authorization_policy
      <pyramid.config.Configurator.set_authorization_policy>`
    * Authentication with :class:`~pyramid_facebook.security
      .FacebookAuthenticationPolicy` using :meth:`config
      .set_authentication_policy <pyramid.config.Configurator
      .set_authentication_policy>`

    """
    settings = config.registry.settings

    path = '/%s' % settings['facebook.namespace']

    config.include('pyramid_facebook.lib', route_prefix=path)
    config.include('pyramid_facebook.security', route_prefix=path)
    config.include('pyramid_facebook.auth', route_prefix=path)
    config.include('pyramid_facebook.canvas', route_prefix=path)
    config.include('pyramid_facebook.credits', route_prefix=path)
    config.include('pyramid_facebook.real_time', route_prefix=path)
    config.commit()
