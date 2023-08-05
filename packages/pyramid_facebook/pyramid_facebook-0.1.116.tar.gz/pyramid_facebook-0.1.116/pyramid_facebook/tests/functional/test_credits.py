# -*- coding: utf-8 -*-
from __future__ import absolute_import

import json

import webtest
from pyramid.config import Configurator

from pyramid_facebook.tests import get_signed_request, conf
from pyramid_facebook.tests.functional import TestView

# Do not ask why facebook payment callback is that twisted:
# 1 - Read the docs https://developers.facebook.com/docs/credits/callback/
# 2 - if headache take aspirin and go back to point 1

USER_ID = 123
ORDER_ID = 987

credits_data = {
        'buyer': USER_ID,
        'receiver': USER_ID,
        'order_id': ORDER_ID,
        'order_info': '{"item_id":"1"}'
        }

request_data = {
    'user':{
        'country': 'us',
        'locale': 'en_US',
        'age': {
            'min': 21,
            'max': 45
            }
        },
    'user_id': USER_ID,
    'oauth_token':'AAAE0yTNwOxgBABXrDk9tNR0DoWyxwuLLNtpaJCRve8jbUZCr4YbxiIJqdwtHHZBt5uK8wV9ELHFfZBl9DmZAyvcXOuTZC9JZC22BCSfzky1gZDZD',
    'expires': 1325210400,
    'issued_at': 1325203762
    }

order_details = {
    'order_id': ORDER_ID,
    'buyer': USER_ID,
    'app': 9876,
    'receiver': USER_ID,
    'amount': 10,
    'time_placed': 1329243276,
    'update_time': 1329243277,
    'data':'',
    'items':[{
        'item_id': '0',
        'title':'100 Diamonds',
        'description': 'Spend Diamonds in dimonds game.',
        'image_url': 'http://image.com/diamonds.png',
        'product_url':'',
        'price': 10,
        'data':''
        }],
    'status': 'placed'}

earned_app_currency = {
    'modified':{
        'product': 'URL_TO_APP_CURR_WEBPAGE',
        'product_title': 'Diamonds',
        'product_amount': 3,
        'credits_amount':10
        }
    }


def dummy_payments_get_items(context, request):
    return {
        # Required:
        "title":       "100 diamonds",
        "description": "100 shiny diamonds!",
        "price":       1000,
        "image_url":   "http://hadriendavid.com/images/100dimonds.png",

        # Optional (according to facebook doc):
        "item_id": "123",
        "data":    "whatever"
        }


class TestFacebookCredits(TestView):
    """Test based on fb documentation:
    https://developers.facebook.com/docs/credits/callback/"""

    def test_payments_get_items_404(self):
        params = request_data.copy()
        params.update(credits=credits_data)
        params = {
            'signed_request': get_signed_request(**params),
            'method': 'payments_get_items'
            }
        params.update(credits_data)

        self.app.post(
            '/%s/credits' % conf['facebook.namespace'],
            params,
            status=404
            )

    def test_payments_get_items(self):
        from pyramid_facebook import includeme
        from pyramid_facebook.credits import facebook_payments_get_items
        from pyramid_facebook.tests import conf
        # to test pyramid integration of facebook_payments_get_items decorator
        # we create a specific config which register dummy_payments_get_items
        # as if it has been decorated with facebook_payments_get_items
        #
        config = Configurator(settings=conf)
        config.include(includeme)
        scanner = type('scanner', (object,) , dict(config=config))
        fbgi = facebook_payments_get_items()
        fbgi._register(scanner, '', dummy_payments_get_items)

        app = webtest.TestApp(config.make_wsgi_app())

        params = request_data.copy()
        params.update(credits=credits_data)
        params = {
            'signed_request': get_signed_request(**params),
            'method': 'payments_get_items'
            }
        params.update(credits_data)

        result = app.post(
            '/%s/credits' % conf['facebook.namespace'],
            params,
            )

        # result musts be a facebook credits compatible json stream
        res_obj = json.loads(result.body)
        expected = {
            'content': [
                {'description': '100 shiny diamonds!',
                'title': '100 diamonds',
                'price': 1000,
                'image_url': 'http://hadriendavid.com/images/100dimonds.png',
                'item_id': '123',
                'data': 'whatever'}
            ],
            'method': 'payments_get_items'
            }
        self.assertEqual(
            expected,
            res_obj
            )


    def test_payments_status_update_placed_item_order(self):
        params = request_data.copy()
        params.update(
            {
            'credits':{
                'order_details': json.dumps(order_details.copy()),
                'status': 'placed',
                'order_id': ORDER_ID
                }
            })

        params = {
            'signed_request': get_signed_request(**params),
            'order_details': json.dumps(order_details.copy()),
            'order_id': ORDER_ID,
            'method': 'payments_status_update',
            'status': 'placed',
            }

        result = self.app.post(
            '/%s/credits' % conf['facebook.namespace'],
            params,
            )

        expected = {
            'content': {
                'status': 'settled',
                'order_id': 987
                },
            'method': 'payments_status_update'
            }
        self.assertDictEqual(expected, json.loads(result.body))


    def test_payments_status_update_earned_app_currency(self):
        params = request_data.copy()
        details = order_details.copy()
        details['items'][0]['data'] = json.dumps(earned_app_currency)
        params.update(
            {
            'credits':{
                'order_details': json.dumps(details),
                'status': 'placed',
                'order_id': ORDER_ID
                }
            })

        params = {
            'signed_request': get_signed_request(**params),
            'order_details': json.dumps(details),
            'order_id': ORDER_ID,
            'method': 'payments_status_update',
            'status': 'placed',
            }

        result = self.app.post(
            '/%s/credits' % conf['facebook.namespace'],
            params,
            )

        expected = {
            'content': {
                'status': 'settled',
                'order_id': 987
                },
            'method': 'payments_status_update'
            }
        self.assertDictEqual(expected, json.loads(result.body))
