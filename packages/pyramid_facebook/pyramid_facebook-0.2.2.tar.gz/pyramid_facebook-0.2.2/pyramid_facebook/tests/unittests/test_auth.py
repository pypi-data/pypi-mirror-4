# -*- coding: utf-8 -*-
import unittest

import mock

from pyramid.response import Response

from pyramid_facebook.tests import conf


class TestAuth(unittest.TestCase):

    def test_includeme(self):
        from pyramid_facebook.auth import includeme
        config = mock.Mock()

        self.assertIsNone(includeme(config))

        self.assertEqual(1, config.add_route.call_count)

        expected = mock.call(
            'facebook_canvas_oauth',
            '/oauth',
            request_method='POST',
            request_param='signed_request',
            factory='pyramid_facebook.security.SignedRequestContext',
            )

        self.assertEqual(expected, config.add_route.call_args_list[0])

        config.scan.assert_called_once_with(package='pyramid_facebook.auth')


class TestFacebookOauth(unittest.TestCase):

    maxDiff = None

    def test_init(self):
        from pyramid_facebook.auth import FacebookCanvasOAuth
        request = mock.MagicMock()
        canvas = FacebookCanvasOAuth(request.context, request)
        self.assertEqual(request, canvas.request)
        self.assertEqual(request.context, canvas.context)

    def test_oauth_accept(self):
        from pyramid_facebook.auth import FacebookCanvasOAuth
        from pyramid_facebook.events import OauthAccept
        from pyramid_facebook.lib import js_redirect_tpl

        settings = conf

        request = mock.MagicMock()
        request.scheme = 'http'
        request.GET = {'spam': 'ham', 'code': '2342342345gibberish'}
        request.route_path.return_value = '/facebook'
        request.registry.settings = settings

        view = FacebookCanvasOAuth(request.context, request)

        result = view.oauth_accept()

        request.route_path.assert_called_once_with('facebook_canvas')
        self.assertTrue(request.registry.notify.called)

        self.assertIsInstance(
            request.registry.notify.call_args[0][0],
            OauthAccept
            )

        expected = str(Response(
            js_redirect_tpl %
            {'location': "//apps.facebook.com/facebook?spam=ham"}
            ))

        self.assertEqual(expected, str(result))

    def test_oauth_deny(self):
        from pyramid_facebook.auth import FacebookCanvasOAuth
        from pyramid_facebook.events import OauthDeny
        from pyramid_facebook.lib import js_redirect_tpl

        settings = conf

        request = mock.MagicMock()
        request.scheme = 'http'
        request.GET = {'spam': 'ham'}
        request.route_path.return_value = '/facebook'
        request.registry.settings = settings

        view = FacebookCanvasOAuth(request.context, request)

        result = view.oauth_deny()

        request.route_path.assert_called_once_with('facebook_canvas')
        self.assertTrue(request.registry.notify.called)

        self.assertIsInstance(
            request.registry.notify.call_args[0][0],
            OauthDeny
            )
        expected = str(Response(
            js_redirect_tpl %
            {'location': "//apps.facebook.com/facebook?spam=ham"}
            ))

        self.assertEqual(expected, str(result))

    @mock.patch('pyramid_facebook.auth.log')
    def test_oauth_exception(self, m_log):
        from pyramid_facebook.auth import FacebookCanvasOAuth

        request = mock.MagicMock()
        request.registry.notify.side_effect = Exception('boooom!')

        view = FacebookCanvasOAuth(request.context, request)
        view.oauth_accept()
        self.assertTrue(m_log.exception.called)

        m_log.error.reset_mock()
        view.oauth_deny()
        self.assertTrue(m_log.exception.called)
