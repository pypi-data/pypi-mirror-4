# -*- coding: utf-8 -*-
import unittest
import json
import hashlib

import mock

from facepy.exceptions import OAuthError

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
        request.context = mock.MagicMock(spec=SignedRequestContext)
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

    def test_unauthenticated_userid_attribute_error(self):
        from pyramid_facebook.security import FacebookAuthenticationPolicy
        request = self._get_request()

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


class TestAccessTokenContext(unittest.TestCase):

    def test_init(self):
        from pyramid_facebook.security import AccessTokenContext
        request = mock.Mock()
        atc = AccessTokenContext(request)

        self.assertEqual(atc.request, request)

    @mock.patch('pyramid_facebook.security.GraphAPI')
    def test_user_dict(self, m_graph_api):
        from pyramid_facebook.security import AccessTokenContext, FacebookUser
        m_graph_api.return_value.get.return_value = dict(id=12345)
        request = mock.Mock()
        atc = AccessTokenContext(request)

        atc.user_dict

        self.assertEqual(12345, atc.unauthenticated_userid())
        self.assertEqual([FacebookUser], atc.effective_principals())

        request.params.get.assert_called_once_with('access_token')
        m_graph_api.assert_called_once_with(request.params.get.return_value)
        m_graph_api.return_value.get.assert_called_once_with('me', retry=0)

    @mock.patch('pyramid_facebook.security.GraphAPI')
    def test_user_dict_facepy_error(self, m_graph_api):
        from pyramid_facebook.security import AccessTokenContext
        oe = OAuthError(code=190, message='OAuth Error')
        m_graph_api.return_value.get.side_effect = oe
        request = mock.Mock()

        atc = AccessTokenContext(request)
        result = atc.user_dict

        self.assertEqual(dict(), result)
        self.assertIsNone(atc.unauthenticated_userid())
        self.assertEqual([], atc.effective_principals())


class TestAdminContext(unittest.TestCase):

    @mock.patch('pyramid_facebook.security.GraphAPI')
    def test_effective_principals(self, m_graph_api):
        from pyramid_facebook.security import AdminContext, UpdateSubscription
        rv = dict(data=[dict(id=12345), dict(id=54321)])
        m_graph_api.return_value.get.return_value = rv
        request = mock.MagicMock()

        ac = AdminContext(request)

        result = ac.effective_principals()

        for i in range(2):
            self.assertEqual(
                mock.call(request.params.get.return_value),
                m_graph_api.call_args_list[i]
                )

        self.assertEqual(
            mock.call('me/accounts', retry=0),
            m_graph_api.return_value.get.call_args_list[1]
            )

        self.assertEqual(
            ((Allow, request.registry.settings.__getitem__.return_value,
              UpdateSubscription),),
            ac.__acl__
            )

        self.assertEqual([12345, 54321], result)

    @mock.patch('pyramid_facebook.security.GraphAPI')
    def test_effective_principals_facepy_error(self, m_graph_api):
        from pyramid_facebook.security import AdminContext
        oe = OAuthError(code=190, message='OAuth Error')
        m_graph_api.return_value.get.side_effect = oe
        request = mock.MagicMock()

        ac = AdminContext(request)
        result = ac.effective_principals()

        self.assertEqual([], result)


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
        self.assertIsNone(rtnc.principals)
        self.assertEqual(
            ((Allow, XHubSigned, NotifyRealTimeChanges), ),
            rtnc.__acl__
            )

    @mock.patch('pyramid_facebook.security.hmac')
    def test_effective_principals(self, m_hmac):
        from pyramid_facebook.security import (
            RealTimeNotificationContext,
            XHubSigned,
            )

        request = mock.MagicMock()
        request.headers = {'X-Hub-Signature': 'sha1=signature'}

        m_hmac.new.return_value.hexdigest.return_value = 'signature'

        rtnc = RealTimeNotificationContext(request)
        result = rtnc.effective_principals()

        self.assertEqual((XHubSigned,), result)

        m_hmac.new.assert_called_once_with(
            request.registry.settings.__getitem__.return_value,
            request.body,
            hashlib.sha1
            )
        m_hmac.new.return_value.hexdigest.assert_called_once_with()

    @mock.patch('pyramid_facebook.security.hmac')
    def test_effective_principals_bad_signature(self, m_hmac):
        from pyramid_facebook.security import (
            RealTimeNotificationContext,
            )

        request = mock.MagicMock()
        request.headers = {'X-Hub-Signature': 'sha1=signature'}

        m_hmac.new.return_value.hexdigest.return_value = 'not same signature'

        rtnc = RealTimeNotificationContext(request)
        result = rtnc.effective_principals()

        self.assertEqual(tuple(), result)
