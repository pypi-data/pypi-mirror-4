# -*- coding: utf-8 -*-
import logging

from facepy import FacepyError, get_application_access_token, GraphAPI

from pyramid.httpexceptions import HTTPForbidden, HTTPOk, HTTPInternalServerError
from pyramid.response import Response
from pyramid.view import view_config

from pyramid_facebook.events import ChangeNotification
from pyramid_facebook.lib import (
    headers_predicate,
    request_params_predicate,
    nor_predicate,
    )
from pyramid_facebook.security import UpdateSubscription, NotifyRealTimeChanges

log = logging.getLogger(__name__)


def includeme(config):
    """Adds routes related to real time updates.

    Routes Added:

    * ``facebook_real_time_subscription_verification`` associated to url
        /{namespace}/real-time

    * ``facebook_real_time_notification`` associated to url
        /{namespace}/real-time

    * ``facebook_real_time_subscriptions`` associated to url
        /{namespace}/real-time/subscriptions

    * ``facebook_real_time_subscriptions_update`` associated to url
        /{namespace}/real-time/subscriptions

    * ``facebook_real_time_subscriptions_delete`` associated to url
        /{namespace}/real-time/subscriptions
    """
    log.debug('Adding route "facebook_real_time_subscription_verification".')
    config.add_route(
        'facebook_real_time_subscription_verification',
        '/real-time',
        request_method='GET',
        custom_predicates=[
            request_params_predicate(
                'hub.challenge',
                'hub.verify_token',
                **{'hub.mode': 'subscribe'}
                ),
            ]
        )

    log.debug('Adding route "facebook_real_time_notification".')
    config.add_route(
        'facebook_real_time_notification',
        '/real-time',
        request_method='POST',
        factory='pyramid_facebook.security.RealTimeNotificationContext',
        custom_predicates=[
            headers_predicate(
                'X-Hub-Signature',
                **{'Content-Type': 'application/json'}
                )
            ]
        )

    log.debug('Adding route "facebook_real_time_subscriptions".')
    config.add_route(
        'facebook_real_time_subscriptions',
        '/real-time/subscriptions',
        request_method='GET',
        request_param='access_token',
        factory='pyramid_facebook.security.AdminContext',
        )

    log.debug('Adding route "facebook_real_time_subscriptions_update".')
    config.add_route(
        'facebook_real_time_subscriptions_update',
        '/real-time/subscriptions',
        request_method='POST',
        custom_predicates=[
            nor_predicate(object=('user', 'permissions', 'page', 'errors')),
            request_params_predicate('fields', 'access_token'),
            ],
        factory='pyramid_facebook.security.AdminContext',
        )

    log.debug('Adding route "facebook_real_time_subscriptions_delete".')
    config.add_route(
        'facebook_real_time_subscriptions_delete',
        '/real-time/subscriptions',
        request_method='DELETE',
        request_param='access_token',
        factory='pyramid_facebook.security.AdminContext',
        )

    config.scan(package='pyramid_facebook.real_time')


@view_config(route_name='facebook_real_time_subscription_verification')
def verify_real_time_subscription(request):
    verify_token = request.params['hub.verify_token']
    settings = request.registry.settings
    try:
        access_token = get_application_access_token(
            settings['facebook.app_id'],
            settings['facebook.secret_key'],
            )
        if access_token == verify_token:
            return Response(request.params['hub.challenge'])
    except FacepyError:
        log.exception('get_application_access_token failed')
    raise HTTPForbidden()


@view_config(context=FacepyError, renderer='json')
def render_facepy_error(exc, request):
    return dict(
        error=dict(
            type=exc.__class__.__name__,
            code=getattr(exc, 'code'),
            message=exc.message,
            )
        )


@view_config(
    route_name='facebook_real_time_subscriptions',
    renderer='json',
    permission=UpdateSubscription,
    )
def list_real_time_subscriptions(request):
    settings = request.registry.settings
    app_id = settings['facebook.app_id']
    secret_key = settings['facebook.secret_key']
    access_token = get_application_access_token(app_id, secret_key)
    return GraphAPI(access_token).get('%s/subscriptions' % app_id)


@view_config(
    route_name='facebook_real_time_subscriptions_update',
    renderer='json',
    permission=UpdateSubscription,
    )
def update_real_time_subscription(request):
    settings = request.registry.settings
    fb_object = request.params['object']
    fields = request.params['fields']
    access_token = get_application_access_token(
        settings['facebook.app_id'],
        settings['facebook.secret_key'],
        )
    # note that url of route named `facebook_real_time_subscription_verification`
    # is the same as route named `facebook_real_time_notification` but with
    # different predicates
    url = request.route_url('facebook_real_time_subscription_verification')
    return (GraphAPI(access_token).post(
        '%s/subscriptions' % settings['facebook.app_id'],
        object=fb_object,
        fields=fields,
        callback_url=url,
        verify_token=access_token
        ))


@view_config(
    route_name='facebook_real_time_subscriptions_delete',
    renderer='json',
    permission=UpdateSubscription,
    )
def delete_real_time_subscription(request):
    settings = request.registry.settings
    fb_object = request.params.get('object')
    access_token = get_application_access_token(
        settings['facebook.app_id'],
        settings['facebook.secret_key'],
        )
    return (GraphAPI(access_token).delete(
        '%s/subscriptions' % settings['facebook.app_id'],
        object=fb_object
        ))


@view_config(
    route_name='facebook_real_time_notification',
    permission=NotifyRealTimeChanges,
    )
def process_real_time_notification(context, request):
    try:
        request.registry.notify(ChangeNotification(context, request))
    except:
        log.exception(
            'process_real_time_notification - json_body: %s',
            request.json_body
            )
        # raise an HTTP error so facebook will send back same update later
        raise HTTPInternalServerError()
    return HTTPOk()
