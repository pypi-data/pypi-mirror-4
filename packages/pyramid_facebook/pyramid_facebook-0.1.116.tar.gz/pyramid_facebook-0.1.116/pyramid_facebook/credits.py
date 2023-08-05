# -*- coding: utf-8 -*-
import logging
import functools

import venusian
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPOk

from pyramid_facebook.lib import request_params_predicate
from pyramid_facebook.events import (
    DisputedOrder,
    EarnedCurrencyOrder,
    PlacedItemOrder,
    RefundedOrder,
    )
from pyramid_facebook.security import ViewCanvas

log = logging.getLogger(__name__)


def includeme(config):
    """Adds routes related to facebook credits.

    Routes Added:

    * ``facebook_payments_get_items`` associated to url ``/{namespace}/credits``.

    * ``facebook_payments_status_update_placed`` associated to url
      ``/{namespace}/credits``.

    * ``facebook_payments_status_update_disputed`` associated to url
      ``/{namespace}/credits``.

    * ``facebook_payments_status_update_refunded`` associated to url
      ``/{namespace}/credits``.
    """
    log.debug('Adding route "facebook_payments_get_items".')
    config.add_route(
        'facebook_payments_get_items',
        '/credits',
        request_method='POST',
        custom_predicates=[
            request_params_predicate(
                'signed_request',
                'buyer',
                'receiver',
                'order_id',
                'order_info',
                method='payments_get_items',
                )
            ],
        factory='pyramid_facebook.security.FacebookCreditsContext',
        )

    update_predicate = request_params_predicate(
        'signed_request',
        'order_details',
        'order_id',
        method='payments_status_update',
        )

    log.debug('Adding route "facebook_payments_status_update_placed".')
    config.add_route(
        'facebook_payments_status_update_placed',
        '/credits',
        request_method='POST',
        custom_predicates=[
            update_predicate,
            request_params_predicate(status='placed'),
            ],
        factory='pyramid_facebook.security.FacebookCreditsContext',
        )

    log.debug('Adding route "facebook_payments_status_update_disputed".')
    config.add_route(
        'facebook_payments_status_update_disputed',
        '/credits',
        request_method='POST',
        custom_predicates=[
            update_predicate,
            request_params_predicate(status='disputed'),
            ],
        factory='pyramid_facebook.security.FacebookCreditsContext',
        )

    log.debug('Adding route "facebook_payments_status_update_refunded".')
    config.add_route(
        'facebook_payments_status_update_refunded',
        '/credits',
        request_method='POST',
        custom_predicates=[
            update_predicate,
            request_params_predicate(status='refunded'),
            ],
        factory='pyramid_facebook.security.FacebookCreditsContext',
        )

    config.scan(package='pyramid_facebook.credits')


class facebook_payments_get_items(object):
    """Decorator to register the function to process facebook credits
    `payments_get_items <http://developers.facebook.com/docs/credits/callback/#payments_get_items>`_.

    Decorated function receives 2 positional parameters:

    * ``context``: The :class:`~pyramid_facebook.security.SignedRequestContext`
      the request is associated with. ``context.facebook_data["user"]`` gives
      information about user's locale which would permit to return different
      languages.

    * ``request``: The request itself.

    It is possible to access `order_info` via :attr:`context.order_info
    <pyramid_facebook.security.FacebookCreditsContext.order_info>`:

    Decorated function must return a dictionary structured as::

        {
            # Required:
            "title":       "100 diamonds",
            "description": "100 shiny diamonds!",
            "price":       1000,
            "image_url":   "http://hadriendavid.com/images/100dimonds.png",

            # Optional (according to facebook doc):
            "item_id": "123",
            "data":    "whatever"
        }

    Example::

        @facebook_payments_get_items()
        def get_item(context, request):
            ...
            return {
                "title": a_title,
                "description": a_description,
                "price": a_price_in_facebook_credits,
                "image_url": an_image_url
                }
    """
    def __call__(self, wrapped):
        # as documented on http://docs.pylonsproject.org/projects/pyramid/en/1.3-branch/narr/hooks.html#registering-configuration-decorators
        venusian.attach(wrapped, self._register)

        log.debug('facebook_payments_get_items provided by %s', wrapped)
        return wrapped

    def _register(self, scanner, name, wrapped):
        """Register view to pyramid framework.
        """
        config = scanner.config
        config.add_view(
            view=self._decorate(wrapped),
            permission=ViewCanvas,
            route_name='facebook_payments_get_items',
            renderer='json',
            )
        log.debug('Adding views %s for route facebook_payments_get_items', wrapped)

    def _validate(self, item_content):
        "Validate item content"
        if not isinstance(item_content, dict):
            raise TypeError('dict expected, received %s' % type(item_content))
        expected = {
            'title'      : (str, unicode,),
            'description': (str, unicode,),
            'price'      : (int,         ),
            'image_url'  : (str, unicode,),
            }
        for k, v in expected.iteritems():
            if type(item_content.get(k)) not in v:
                raise TypeError('Expected %r, received %r' % (
                    expected,
                    item_content
                    ))
        return item_content

    def _decorate(self, wrapped):
        @functools.wraps(wrapped)
        def wrapper(context, request):
            log.debug(
                'facebook_payments_get_items call with facebook_data=%s',
                context.facebook_data
                )
            result = self._validate(wrapped(context, request))
            return {
                "content": [result],
                "method": "payments_get_items"
                }
        return wrapper



@view_config(route_name='facebook_payments_status_update_disputed')
def facebook_payments_status_update_disputed(context, request):
    try:
        log.debug('Order Status Update Disputed')
        request.registry.notify(DisputedOrder(context, request))
    except Exception:
        log.exception(
            'facebook_payments_status_update_disputed with context=%r, '
            'request.params=%r',
            context,
            request,
            )
    return HTTPOk()


@view_config(route_name='facebook_payments_status_update_refunded')
def facebook_payments_status_update_refunded(context, request):
    try:
        log.debug('Order Status Update Refunded')
        request.registry.notify(RefundedOrder(context, request))
    except Exception:
        log.exception(
            'facebook_payments_status_update_refunded with context=%r, '
            'request.params=%r.',
            context,
            request,
            )
    return HTTPOk()


@view_config(
    route_name='facebook_payments_status_update_placed',
    permission=ViewCanvas,
    renderer='json'
    )
def facebook_payments_status_update_placed(context, request):
    if context.earned_currency_data:
        log.debug('Order Status Update - Earned App Currency')
        event_class = EarnedCurrencyOrder
    else:
        log.debug('Order Status Update - Placed Item Order')
        event_class = PlacedItemOrder
    try:
        request.registry.notify(event_class(context, request))
    except Exception:
        log.exception(
            'facebook_payments_status_update_placed with context=%r, '
            'request.params=%r.',
            context,
            request,
            )
        status = 'canceled'
    else:
        log.debug(
            'facebook_payments_status_update_placed settled %r',
            context.order_details,
            )
        status = 'settled'
    return {
        'content': {
            'status': status,
            'order_id': context.order_details['order_id'],
            },
        'method': 'payments_status_update',
        }
