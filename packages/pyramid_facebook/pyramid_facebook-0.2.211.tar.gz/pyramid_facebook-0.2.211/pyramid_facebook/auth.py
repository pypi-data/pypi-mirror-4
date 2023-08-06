# -*- coding: utf-8 -*-
import urllib
import logging

from pyramid.httpexceptions import HTTPForbidden
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from pyramid_facebook.events import OauthAccept, OauthDeny
from pyramid_facebook.lib import Base, js_redirect_tpl
from pyramid_facebook.security import Authenticate


log = logging.getLogger(__name__)


def includeme(config):
    log.debug('Adding route "facebook_canvas_oauth".')
    config.add_route(
        'facebook_canvas_oauth',
        '/oauth',
        request_method='POST',
        request_param='signed_request',
        factory='pyramid_facebook.security.SignedRequestContext',
        )
    config.scan(package='pyramid_facebook.auth')


@view_defaults(route_name='facebook_canvas_oauth')
class FacebookCanvasOAuth(Base):

    def _redirect_to_canvas(self):
        log.debug('redirect to canvas')
        path = self.request.route_path('facebook_canvas')
        query_string = self.request.GET.copy()
        query_string.pop('code', None)
        p = {'location': "//apps.facebook.com%s?%s" % (
            path,
            # we could filter out "error*" fields
            urllib.urlencode(query_string),
            )}
        return Response(js_redirect_tpl % p)

    @view_config(permission=Authenticate)
    def oauth_accept(self):
        log.debug('user accepts')
        try:
            self.request.registry.notify(OauthAccept(self.context, self.request))
        except Exception:
            log.exception(
                'Oauth accept with context=%r, params=%r.',
                self.context,
                self.request.params
                )
        return self._redirect_to_canvas()

    @view_config(context=HTTPForbidden, request_param="error")
    def oauth_deny(self):
        log.debug('user denies')
        try:
            self.request.registry.notify(OauthDeny(self.context, self.request))
        except Exception:
            log.exception(
                'Oauth deny with context=%r, params=%r: %s',
                self.context,
                self.request.params
                )
        return self._redirect_to_canvas()
