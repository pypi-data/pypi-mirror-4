import unittest

import mock


class TestPredicate(unittest.TestCase):
    def test_request_params_predicate(self):
        from pyramid_facebook.predicates import request_params_predicate

        predicate = request_params_predicate('a', 'b', 'c', d=123, e='yo')

        request = mock.Mock()
        request.params = dict(a=1, b=2, c=3, d=123, e='yo')
        self.assertTrue(predicate(None, request))

        request.params = dict(a=1, b=2)
        self.assertFalse(predicate(None, request))

        request.params = dict(a=1, b=2, c=1, d=321, e='oy')
        self.assertFalse(predicate(None, request))

    def test_nor_predicate(self):
        from pyramid_facebook.predicates import nor_predicate
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
        from pyramid_facebook.predicates import headers_predicate

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
        from pyramid_facebook.predicates import MatchedRouteEventPredicate

        pred = MatchedRouteEventPredicate(u'route_name', None)

        event = mock.Mock()
        event.request.matched_route.name = u'route_name'

        self.assertTrue(pred(event))

    def test_predicate_unmatched(self):
        from pyramid_facebook.predicates import MatchedRouteEventPredicate

        pred = MatchedRouteEventPredicate(u'route_name', None)

        event = mock.Mock()
        event.request.matched_route.name = u'not_same_route_name'

        self.assertFalse(pred(event))

    def test_text(self):
        from pyramid_facebook.predicates import MatchedRouteEventPredicate

        pred = MatchedRouteEventPredicate(u'route_name', None)

        self.assertEqual(u'route_to_match = route_name', pred.text())


class TestContextEcentPredicate(unittest.TestCase):

    def test_predicate_matched(self):
        from pyramid_facebook.predicates import ContextEventPredicate
        from pyramid_facebook.security import SignedRequestContext

        event = mock.Mock()
        event.request.context = SignedRequestContext(None)

        pred = ContextEventPredicate(SignedRequestContext, None)

        self.assertTrue(pred(event))

    def test_predicate_unmatched(self):
        from pyramid_facebook.predicates import ContextEventPredicate
        from pyramid_facebook.security import (
            SignedRequestContext,
            RealTimeNotificationContext,
            )

        event = mock.Mock()
        event.request.context = RealTimeNotificationContext(None)

        pred = ContextEventPredicate(SignedRequestContext, None)

        self.assertFalse(pred(event))

    def test_text(self):
        from pyramid_facebook.predicates import ContextEventPredicate
        from pyramid_facebook.security import SignedRequestContext

        pred = ContextEventPredicate(SignedRequestContext, None)

        self.assertEqual(
            u"expected_context_cls = <class "
            "'pyramid_facebook.security.SignedRequestContext'>",
            pred.text()
            )


class TestPermissionEventPredicate(unittest.TestCase):

    def test_call(self):
        from pyramid_facebook.predicates import PermissionEventPredicate

        pred = PermissionEventPredicate('view-canvas', None)

        pred(mock.Mock())

    def test_text(self):
        from pyramid_facebook.predicates import PermissionEventPredicate
        pred = PermissionEventPredicate('view-canvas', None)

        self.assertEqual(u"permission = 'view-canvas'", pred.text())
