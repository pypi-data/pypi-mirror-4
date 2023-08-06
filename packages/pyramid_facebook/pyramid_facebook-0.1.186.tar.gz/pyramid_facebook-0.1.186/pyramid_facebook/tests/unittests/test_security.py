# -*- coding: utf-8 -*-
import unittest
import json

import mock


from pyramid import testing
from pyramid.config import Configurator
from pyramid.security import Allow

from pyramid_facebook.security import SignedRequestContext
from pyramid_facebook.tests import conf

TEST_USER = 123


def _get_signed_request(user_id=None):
    from pyramid_facebook.lib import encrypt_signed_request
    return encrypt_signed_request(
        conf['facebook.secret_key'],
        {
            'user_id': user_id if user_id else TEST_USER,
            'user': {
                'country': 'ca'
                }
            }
        )


def _get_request(signed_request=None):
    request = mock.MagicMock()
    signed_request = (signed_request
                      if signed_request else _get_signed_request())
    request.params = {'signed_request': signed_request}
    request.registry.settings = conf.copy()
    return request


class TestIncludeme(unittest.TestCase):

    @mock.patch('pyramid_facebook.security.ACLAuthorizationPolicy')
    @mock.patch('pyramid_facebook.security.FacebookAuthenticationPolicy')
    def test_includeme(self, FacebookAuthenticationPolicy,
                       ACLAuthorizationPolicy):
        from pyramid_facebook.security import includeme

        config = mock.MagicMock(spec=Configurator)

        includeme(config)

        config.set_authentication_policy.assert_called_once_with(
            FacebookAuthenticationPolicy.return_value
            )
        config.set_authorization_policy.assert_called_once_with(
            ACLAuthorizationPolicy.return_value
            )
        FacebookAuthenticationPolicy.assert_called_once_with()
        ACLAuthorizationPolicy.assert_called_once_with()


class TestFacebookCreditsContext(unittest.TestCase):

    @mock.patch('pyramid_facebook.security.json')
    def test_order_details(self, m_json):
        from pyramid_facebook.security import FacebookCreditsContext
        ctx = FacebookCreditsContext(_get_request())
        ctx.facebook_data = data = mock.MagicMock()

        self.assertEqual(m_json.loads.return_value, ctx.order_details)
        m_json.loads.assert_called_once_with(data['credits']['order_details'])

    def test_earned_currency_data(self):
        from pyramid_facebook.security import FacebookCreditsContext
        ctx = FacebookCreditsContext(_get_request())
        ctx.facebook_data = {
            'credits': {
                'order_details': json.dumps({
                    'items': [
                        {'data': '{"modified": "earned_currency_data"}'}
                        ]
                    })
                }
            }
        self.assertEqual(
            'earned_currency_data',
            ctx.earned_currency_data
            )

    def test_earned_currency_data_invalid_json(self):
        from pyramid_facebook.security import FacebookCreditsContext
        ctx = FacebookCreditsContext(_get_request())
        # with Invalid json data:
        ctx.facebook_data = {
            'credits': {
                'order_details': json.dumps({
                    'items': [
                        {'data': '{INVALID JSON "}'}
                        ]
                    })
                }
            }
        self.assertEqual(
            None,
            ctx.earned_currency_data
            )

    def test_order_info(self):
        from pyramid_facebook.security import FacebookCreditsContext
        ctx = FacebookCreditsContext(_get_request())
        ctx.facebook_data = mock.MagicMock()

        self.assertEqual(ctx.facebook_data["credits"]["order_info"],
                         ctx.order_info)

    def test_item(self):
        from pyramid_facebook.security import FacebookCreditsContext
        ctx = FacebookCreditsContext(_get_request())
        ctx.facebook_data = mock.MagicMock()
        t = json.dumps({'items': [{'title': 'an item'}]})
        ctx.facebook_data.__getitem__.return_value.__getitem__.return_value = t

        self.assertEqual(
            {'title': 'an item'},
            ctx.item,
            )


class TestSignedRequestContext(unittest.TestCase):

    def test_init(self):
        from pyramid_facebook.security import (
            SignedRequestContext,
            ViewCanvas,
            Authenticate,
            FacebookUser,
            RegisteredUser,
            )

        self.assertEqual(
            [
                (Allow, FacebookUser, Authenticate),
                (Allow, RegisteredUser, ViewCanvas),
                ],
            SignedRequestContext.__acl__
            )

        SignedRequestContext(None)

    def test_facebook_data_not_set(self):
        from pyramid_facebook.security import SignedRequestContext
        sr = SignedRequestContext(None)
        self.assertEqual(None, sr.facebook_data)

    def test_facebook_data_property(self):
        from pyramid_facebook.security import SignedRequestContext
        sr = SignedRequestContext(None)
        sr.facebook_data = 'something'
        self.assertEqual('something', sr.facebook_data)

    def test_repr(self):
        from pyramid_facebook.security import SignedRequestContext

        ctx = SignedRequestContext(_get_request())
        ctx.facebook_data = 'something'

        self.assertEqual(
            "<SignedRequestContext facebook_data='something'>",
            ctx.__repr__()
            )

    def test_user(self):
        from pyramid_facebook.security import SignedRequestContext
        sr = SignedRequestContext(None)
        sr.facebook_data = {'user': 12345}
        self.assertEqual(12345, sr.user)

    def test_country(self):
        from pyramid_facebook.security import SignedRequestContext
        sr = SignedRequestContext(None)
        sr.facebook_data = {'user': {'country': 'FR'}}
        self.assertEqual('FR', sr.user_country)


class TestAccessTokenContext(unittest.TestCase):

    def test_access_token(self):
        from pyramid_facebook.security import AccessTokenContext
        request = mock.Mock()
        atc = AccessTokenContext(request)
        atc.user_dict = {u'k': 123}
        atc.user_id = 1000

        self.assertEqual(atc.request, request)
        self.assertEqual({u'k': 123}, atc.user_dict)
        self.assertEqual(1000, atc.user_id)


class TestRealTimeNotificationContext(unittest.TestCase):

    def test_init(self):
        from pyramid_facebook.security import (
            RealTimeNotificationContext,
            Allow,
            XHubSigned,
            NotifyRealTimeChanges
            )

        request = mock.Mock()

        rtnc = RealTimeNotificationContext(request)

        self.assertEqual(request, rtnc.request)
        self.assertEqual(
            ((Allow, XHubSigned, NotifyRealTimeChanges), ),
            rtnc.__acl__
            )


class TestFacebookAuthenticationPolicy(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _get_request(self, context_cls=SignedRequestContext):
        request = testing.DummyRequest()
        request.params = {'signed_request': mock.MagicMock(spec=str)}
        request.registry.settings = {
            'facebook.secret_key': 'a secret',
            }
        request.context = mock.MagicMock(spec=context_cls)
        return request

    @mock.patch('pyramid_facebook.security.SignedRequest')
    def test_parse_signed_request(self, SignedRequest):
        from pyramid_facebook.security import FacebookAuthenticationPolicy
        request = self._get_request()
        SignedRequest.parse.return_value = {u'user_id': 123}
        fap = FacebookAuthenticationPolicy()
        result = fap._parse_signed_request(request)

        SignedRequest.parse.assert_called_once_with(
            request.params['signed_request'],
            request.registry.settings['facebook.secret_key'],
            )
        self.assertEqual(123, result)

    def test_unauthenticated_userid(self):
        from pyramid_facebook.security import FacebookAuthenticationPolicy
        request = self._get_request()
        fap = FacebookAuthenticationPolicy()
        self.assertIsNone(fap.unauthenticated_userid(request))

    def test_unauthenticated_userid_key_error(self):
        from pyramid_facebook.security import FacebookAuthenticationPolicy
        request = self._get_request()
        request.context = 'Whatever which causes a KeyError'
        fap = FacebookAuthenticationPolicy()
        self.assertIsNone(fap.unauthenticated_userid(request))

    @mock.patch('pyramid_facebook.security.SignedRequest')
    def test_effective_principals(self, SignedRequest):
        from pyramid_facebook.security import (
            FacebookAuthenticationPolicy,
            RegisteredUser,
            FacebookUser,
            )
        request = self._get_request()
        SignedRequest.parse.return_value = {u'user_id': 123}
        fap = FacebookAuthenticationPolicy()
        self.assertEqual(
            ['system.Everyone', 'system.Authenticated', 123, RegisteredUser,
             FacebookUser],
            fap.effective_principals(request)
            )

    def test_effective_principals_attribute_error(self):
        from pyramid_facebook.security import FacebookAuthenticationPolicy
        request = self._get_request()
        fap = FacebookAuthenticationPolicy()
        self.assertEqual(['system.Everyone'],
                         fap.effective_principals(request))

    def test_effective_principals_key_error(self):
        from pyramid_facebook.security import FacebookAuthenticationPolicy
        request = self._get_request(
            context_cls=type('UnknownContext', (object, ), {})
            )
        fap = FacebookAuthenticationPolicy()

        # Key Error handling:
        self.assertEqual(['system.Everyone'],
                         fap.effective_principals(request))

    def test_remember(self):
        from pyramid_facebook.security import FacebookAuthenticationPolicy
        request = self._get_request()

        fap = FacebookAuthenticationPolicy()

        principal = "principal"
        kwargs = {"a": "a_val", "b": "b_val"}

        # FacebookAuthenticationPolicy does not support a remember/forget
        # mecanism, user is authenticated on each request
        self.assertListEqual([], fap.remember(request, principal, **kwargs))

    def test_forget(self):
        from pyramid_facebook.security import FacebookAuthenticationPolicy
        request = self._get_request()

        fap = FacebookAuthenticationPolicy()

        # FacebookAuthenticationPolicy does not support a remember/forget
        # mecanism, user is authenticated on each request
        self.assertListEqual([], fap.forget(request))

    def test_parse_signed_request_with_no_signed_request(self):
        from pyramid_facebook.security import FacebookAuthenticationPolicy
        request = self._get_request()
        del request.params['signed_request']

        fap = FacebookAuthenticationPolicy()

        self.assertIsNone(fap._parse_signed_request(request))

    @mock.patch('pyramid_facebook.security.SignedRequest')
    def test_parse_signed_request_with_no_user_id(self, SignedRequest):
        from pyramid_facebook.security import FacebookAuthenticationPolicy
        request = self._get_request()
        SignedRequest.parse.return_value = {'no_user_id': ':-o'}

        fap = FacebookAuthenticationPolicy()

        self.assertIsNone(fap._parse_signed_request(request))

    @mock.patch('pyramid_facebook.security.SignedRequest')
    def test_parse_signed_request_with_invalid_user_id(self, SignedRequest):
        from pyramid_facebook.security import FacebookAuthenticationPolicy
        request = self._get_request()
        SignedRequest.parse.return_value = {u'user_id': u'not an int'}

        fap = FacebookAuthenticationPolicy()

        self.assertIsNone(fap._parse_signed_request(request))

    @mock.patch('pyramid_facebook.security.GraphAPI')
    def test_validate_access_token_with_no_access_token(self, GraphAPI):
        from pyramid_facebook.security import FacebookAuthenticationPolicy
        request = self._get_request()

        fap = FacebookAuthenticationPolicy()

        self.assertIsNone(fap._validate_access_token(request))

    @mock.patch('pyramid_facebook.security.GraphAPI')
    def test_validate_access_token_with_facepy_error(self, GraphAPI):
        from pyramid_facebook.security import (
            FacebookAuthenticationPolicy,
            FacepyError,
            AccessTokenContext,
            )
        request = self._get_request(context_cls=AccessTokenContext)
        request.context.user_dict = {}
        request.params = {u'access_token': u'123qwerty'}

        api = GraphAPI.return_value = mock.Mock()
        api.get.side_effect = FacepyError('oooops')

        fap = FacebookAuthenticationPolicy()

        self.assertIsNone(fap._validate_access_token(request))

    @mock.patch('pyramid_facebook.security.GraphAPI')
    def test_validate_access_token_malformed_fb_response(self, GraphAPI):
        from pyramid_facebook.security import (
            FacebookAuthenticationPolicy,
            AccessTokenContext,
            )
        request = self._get_request(context_cls=AccessTokenContext)
        request.params = {u'access_token': u'123qwerty'}

        api = GraphAPI.return_value = mock.Mock()
        api.get.return_value = {u'id': u'not an int'}

        fap = FacebookAuthenticationPolicy()

        self.assertEqual(None, fap._validate_access_token(request))

    @mock.patch('pyramid_facebook.security.GraphAPI')
    def test_validate_access_token(self, GraphAPI):
        from pyramid_facebook.security import (
            FacebookAuthenticationPolicy,
            AccessTokenContext,
            )
        request = self._get_request(context_cls=AccessTokenContext)
        request.params = {u'access_token': u'123qwerty'}

        api = GraphAPI.return_value = mock.Mock()
        api.get.return_value = {u'id': u'12345'}

        fap = FacebookAuthenticationPolicy()

        self.assertEqual(12345, fap._validate_access_token(request))

    def test_get_principals_from_access_token(self):
        from pyramid_facebook.security import (
            FacebookAuthenticationPolicy,
            AccessTokenContext,
            FacebookUser
            )
        request = self._get_request(context_cls=AccessTokenContext)
        request.context.user_id = 1234

        fap = FacebookAuthenticationPolicy()

        self.assertEqual(
            [FacebookUser],
            fap._get_principals_from_access_token(request)
            )

    @mock.patch('pyramid_facebook.security.GraphAPI')
    def test_get_principals_from_admin_context_with_facepy_error(self,
                                                                 GraphAPI):
        from pyramid_facebook.security import (
            FacebookAuthenticationPolicy,
            AdminContext,
            FacepyError,
            )
        request = self._get_request(context_cls=AdminContext)
        request.params = {u'access_token': u'123qwerty'}

        api = GraphAPI.return_value = mock.Mock()
        api.get.side_effect = FacepyError('opps')

        fap = FacebookAuthenticationPolicy()

        self.assertEqual(
            ['facebook-user'],
            fap._get_principals_from_admin_context(request)
            )

    @mock.patch('pyramid_facebook.security.GraphAPI')
    def test_get_principals_from_admin_context(self, GraphAPI):
        from pyramid_facebook.security import (
            FacebookAuthenticationPolicy,
            AdminContext,
            )
        request = self._get_request(context_cls=AdminContext)
        request.params = {u'access_token': u'123qwerty'}

        api = GraphAPI.return_value = mock.Mock()
        api.get.return_value = {u'data': [{u'id': u'123'}, {u'id': u'234'}]}

        fap = FacebookAuthenticationPolicy()

        self.assertEqual(
            ['facebook-user', u'123', u'234'],
            fap._get_principals_from_admin_context(request)
            )

    @mock.patch('pyramid_facebook.security.hmac')
    def test_get_principals_from_signature_wrong_signature(self, hmac):
        from pyramid_facebook.security import (
            FacebookAuthenticationPolicy,
            RealTimeNotificationContext,
            )
        request = self._get_request(context_cls=RealTimeNotificationContext)
        request.headers[u'X-Hub-Signature'] = u'sha1=signature'

        hmac.new.return_value.hexdigest.return_value = u'WRONG'

        fap = FacebookAuthenticationPolicy()

        self.assertEqual(
            [],
            fap._get_principals_from_signature(request)
            )

    @mock.patch('pyramid_facebook.security.hmac')
    def test_get_principals_from_signature(self, hmac):
        from pyramid_facebook.security import (
            FacebookAuthenticationPolicy,
            RealTimeNotificationContext,
            XHubSigned,
            )
        request = self._get_request(context_cls=RealTimeNotificationContext)
        request.headers[u'X-Hub-Signature'] = u'sha1=signature'

        hmac.new.return_value.hexdigest.return_value = u'signature'

        fap = FacebookAuthenticationPolicy()

        self.assertEqual(
            [XHubSigned],
            fap._get_principals_from_signature(request)
            )
