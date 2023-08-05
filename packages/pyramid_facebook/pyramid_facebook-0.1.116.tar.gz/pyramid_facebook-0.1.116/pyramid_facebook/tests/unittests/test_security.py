# -*- coding: utf-8 -*-
import unittest
import json
import hashlib

import mock

from facepy.exceptions import OAuthError

from pyramid.security import Allow

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
    signed_request = signed_request if signed_request else _get_signed_request()
    request.params = {'signed_request': signed_request}
    request.registry.settings = conf.copy()
    return request


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
                'order_details':json.dumps({
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
                'order_details':json.dumps({
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

        self.assertEqual(ctx.facebook_data["credits"]["order_info"], ctx.order_info)

    def test_item(self):
        from pyramid_facebook.security import FacebookCreditsContext
        ctx = FacebookCreditsContext(_get_request())
        ctx.facebook_data = mock.MagicMock()
        ctx.facebook_data.__getitem__.return_value.__getitem__.return_value = json.dumps(
            {'items': [{'title': 'an item'}]}
            )

        self.assertEqual(
            {'title': 'an item'},
            ctx.item,
            )


class TestSignedRequestContext(unittest.TestCase):

    def test_init(self):
        from pyramid_facebook.security import(
            SignedRequestContext,
            ViewCanvas,
            Authenticate,
            FacebookUser,
            RegisteredUser,
            )

        request = _get_request()

        ctx = SignedRequestContext(request)

        self.assertEqual(
            [
                (Allow, FacebookUser, Authenticate),
                (Allow, RegisteredUser, ViewCanvas),
                ],
            ctx.__acl__
            )
        self.assertEqual(
            {u'user_id': 123, u'algorithm': u'HMAC-SHA256', u'user': {u'country': u'ca'}},
            ctx.facebook_data
            )
        self.assertEqual({u'country': u'ca'}, ctx.user)
        self.assertEqual(u'ca', ctx.user_country)

    def test_init_malformated_signed_request(self):
        from pyramid_facebook.security import SignedRequestContext
        request = _get_request(signed_request='malformated')

        ctx = SignedRequestContext(request)
        self.assertIsNone(ctx.unauthenticated_userid())

    def test_init_no_user_id(self):
        from pyramid_facebook.lib import encrypt_signed_request
        from pyramid_facebook.security import SignedRequestContext
        request = _get_request(
            encrypt_signed_request(
                conf['facebook.secret_key'],
                {'no_user_id': '-_-'})
            )

        ctx = SignedRequestContext(request)
        self.assertIsNone(ctx.unauthenticated_userid())

        self.assertEqual([], ctx.effective_principals())

    def test_user_id_attribute_error(self):
        from pyramid_facebook.security import SignedRequestContext
        request = mock.MagicMock()
        request.params.get.return_value = None

        context = SignedRequestContext(request) # to raise AttributeError

        self.assertIsNone(context.unauthenticated_userid())

    def test_extract_user_id__error(self):
        from pyramid_facebook.security import SignedRequestContext

        request = _get_request(_get_signed_request('not a numeric value'))

        ctx = SignedRequestContext(request)

        self.assertIsNone(ctx.unauthenticated_userid())

    def test_repr(self):
        from pyramid_facebook.security import SignedRequestContext

        ctx = SignedRequestContext(_get_request())

        self.assertEqual(
            "<SignedRequestContext facebook_data={u'user_id': 123, u'user': {u'country': u'ca'}, u'algorithm': u'HMAC-SHA256'}>",
            ctx.__repr__()
            )


class TestFacebookAuthenticationPolicy(unittest.TestCase):

    def test_unauthenticated_userid(self):
        from pyramid_facebook.security import FacebookAuthenticationPolicy
        request = mock.Mock()

        fap = FacebookAuthenticationPolicy()
        self.assertEqual(
            request.context.unauthenticated_userid(),
            fap.unauthenticated_userid(request)
            )

    def test_unauthenticated_userid_attribute_error(self):
        from pyramid_facebook.security import FacebookAuthenticationPolicy
        request = mock.Mock()
        request.context.unauthenticated_userid.side_effect = AttributeError('no!')

        fap = FacebookAuthenticationPolicy()
        self.assertIsNone(fap.unauthenticated_userid(request))

    def test_effective_principals(self):
        from pyramid_facebook.security import FacebookAuthenticationPolicy, RegisteredUser
        request = mock.Mock()
        request.context.unauthenticated_userid.return_value = 123
        request.context.effective_principals.return_value = ['user']
        fap = FacebookAuthenticationPolicy()
        self.assertEqual(
            ['system.Everyone', 'system.Authenticated', 123, RegisteredUser, 'user'],
            fap.effective_principals(request)
            )

    def test_effective_principals_attribute_error(self):
        from pyramid_facebook.security import FacebookAuthenticationPolicy
        request = mock.Mock()
        request.context.unauthenticated_userid.side_effect = AttributeError('no!')
        request.context.effective_principals.side_effect = AttributeError('no!')
        fap = FacebookAuthenticationPolicy()
        self.assertEqual(['system.Everyone'], fap.effective_principals(request))


    def test_remember(self):
        from pyramid_facebook.security import FacebookAuthenticationPolicy

        fap = FacebookAuthenticationPolicy()

        request = mock.MagicMock()
        principal = "principal"
        kwargs = {"a": "a_val", "b": "b_val"}

        # FacebookAuthenticationPolicy does not support a remember/forget
        # mecanism, user is authenticated on each request
        self.assertListEqual([], fap.remember(request, principal, **kwargs))


    def test_forget(self):
        from pyramid_facebook.security import FacebookAuthenticationPolicy

        fap = FacebookAuthenticationPolicy()

        request = mock.MagicMock()

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

        result = atc.user_dict

        self.assertEqual(12345, atc.unauthenticated_userid())
        self.assertEqual([FacebookUser], atc.effective_principals())

        request.params.get.assert_called_once_with('access_token')
        m_graph_api.assert_called_once_with(request.params.get.return_value)
        m_graph_api.return_value.get.assert_called_once_with('me', retry=0)


    @mock.patch('pyramid_facebook.security.GraphAPI')
    def test_user_dict_facepy_error(self, m_graph_api):
        from pyramid_facebook.security import AccessTokenContext
        m_graph_api.return_value.get.side_effect = OAuthError(code=190, message='OAuth Error')
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
        m_graph_api.return_value.get.return_value = dict(data=[dict(id=12345), dict(id=54321)])
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
            ((Allow, request.registry.settings.__getitem__.return_value, UpdateSubscription),),
            ac.__acl__
            )

        self.assertEqual([12345, 54321], result)


    @mock.patch('pyramid_facebook.security.GraphAPI')
    def test_effective_principals_facepy_error(self, m_graph_api):
        from pyramid_facebook.security import AdminContext
        m_graph_api.return_value.get.side_effect = OAuthError(code=190, message='OAuth Error')
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

        m_hmac.new.return_value.hexdigest.return_value = 'not the same signature'

        rtnc = RealTimeNotificationContext(request)
        result = rtnc.effective_principals()

        self.assertEqual(tuple(), result)
