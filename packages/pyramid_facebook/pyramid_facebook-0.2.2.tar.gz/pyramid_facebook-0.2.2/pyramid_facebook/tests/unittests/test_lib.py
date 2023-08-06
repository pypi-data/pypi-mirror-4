# -*- coding: utf-8 -*-
import unittest

import mock

from facepy import SignedRequest


class TestLib(unittest.TestCase):

    def test_base(self):
        from pyramid_facebook.lib import Base
        req = mock.Mock()
        ctx = mock.Mock()

        b = Base(ctx, req)
        self.assertEqual(ctx, b._context)
        self.assertEqual(req, b._request)
        self.assertEqual(ctx, b.context)
        self.assertEqual(req, b.request)

    def test_encrypt_decrypt_request(self):
        from pyramid_facebook.lib import encrypt_signed_request
        data = {
            u'issued_at': 1297110048,
            u'user': {
                u'locale': u'en_US',
                u'country': u'ca'
                },
            u'algorithm': u'HMAC-SHA256'
            }

        req = encrypt_signed_request('secret key', data)

        res = SignedRequest.parse(req, 'secret key')
        self.assertEqual(data.keys(), res.keys())
        self.assertEqual(data, res)

    def test_request_params_predicate(self):
        from pyramid_facebook.lib import request_params_predicate

        predicate = request_params_predicate('a', 'b', 'c', d=123, e='yo')

        request = mock.Mock()
        request.params = dict(a=1, b=2, c=3, d=123, e='yo')
        self.assertTrue(predicate(None, request))

        request.params = dict(a=1, b=2)
        self.assertFalse(predicate(None, request))

        request.params = dict(a=1, b=2, c=1, d=321, e='oy')
        self.assertFalse(predicate(None, request))

    def test_nor_predicate(self):
        from pyramid_facebook.lib import nor_predicate
        predicate = nor_predicate(test=('a', 'b', 'c'))

        request = mock.Mock()
        request.params = dict(test='a')

        self.assertTrue(predicate(None, request))

        request.params = dict(test='c')
        self.assertTrue(predicate(None, request))

        request.params = dict(not_test='c')
        self.assertFalse(predicate(None, request))

        request.params = dict(test='d')
        self.assertFalse(predicate(None, request))

    def test_headers_predicate(self):
        from pyramid_facebook.lib import headers_predicate

        predicate = headers_predicate('X-header-1', **{'X-header-2': 'value'})

        request = mock.Mock()
        request.headers = {}

        self.assertFalse(predicate(None, request))

        request.headers = {'X-header-1': 'yo'}

        self.assertFalse(predicate(None, request))

        request.headers = {'X-header-1': 'yo', 'X-header-2': 'not value'}

        self.assertFalse(predicate(None, request))

        request.headers = {'X-header-1': 'yo', 'X-header-2': 'value'}

        self.assertTrue(predicate(None, request))


class TestMatchedRoutePredicate(unittest.TestCase):

    def test_predicate_matched(self):
        from pyramid_facebook.lib import MatchedRouteEventPredicate

        pred = MatchedRouteEventPredicate(u'route_name', None)

        event = mock.Mock()
        event.request.matched_route.name = u'route_name'

        self.assertTrue(pred(event))

    def test_predicate_unmatched(self):
        from pyramid_facebook.lib import MatchedRouteEventPredicate

        pred = MatchedRouteEventPredicate(u'route_name', None)

        event = mock.Mock()
        event.request.matched_route.name = u'not_same_route_name'

        self.assertFalse(pred(event))

    def test_text(self):
        from pyramid_facebook.lib import MatchedRouteEventPredicate

        pred = MatchedRouteEventPredicate(u'route_name', None)

        self.assertEqual(u'route_to_match = route_name', pred.text())


class TestContextEcentPredicate(unittest.TestCase):

    def test_predicate_matched(self):
        from pyramid_facebook.lib import ContextEventPredicate
        from pyramid_facebook.security import SignedRequestContext

        event = mock.Mock()
        event.request.context = SignedRequestContext(None)

        pred = ContextEventPredicate(SignedRequestContext, None)

        self.assertTrue(pred(event))

    def test_predicate_unmatched(self):
        from pyramid_facebook.lib import ContextEventPredicate
        from pyramid_facebook.security import (
            SignedRequestContext,
            RealTimeNotificationContext,
            )

        event = mock.Mock()
        event.request.context = RealTimeNotificationContext(None)

        pred = ContextEventPredicate(SignedRequestContext, None)

        self.assertFalse(pred(event))

    def test_text(self):
        from pyramid_facebook.lib import ContextEventPredicate
        from pyramid_facebook.security import SignedRequestContext

        pred = ContextEventPredicate(SignedRequestContext, None)

        self.assertEqual(
            u"expected_context_cls = <class 'pyramid_facebook.security.SignedRequestContext'>",
            pred.text()
            )
