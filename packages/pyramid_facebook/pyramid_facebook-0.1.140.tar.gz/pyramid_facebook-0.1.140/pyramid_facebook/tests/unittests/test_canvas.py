# -*- coding: utf-8 -*-
import unittest

import mock

from pyramid_facebook.tests import conf


class TestFacebookCanvas(unittest.TestCase):

    def test_includeme(self):
        from pyramid_facebook.canvas import includeme
        config = mock.Mock()

        self.assertIsNone(includeme(config))

        self.assertEqual(1, config.add_route.call_count)

        expected = mock.call(
            'facebook_canvas',
            '/',
            request_method='POST',
            request_param='signed_request',
            factory='pyramid_facebook.security.SignedRequestContext',
            )

        self.assertEqual(expected, config.add_route.call_args_list[0])

        config.scan.assert_called_once_with(package='pyramid_facebook.canvas')

    def test_prompt_authorize(self):
        from pyramid_facebook.canvas import prompt_authorize

        settings = conf

        request = mock.MagicMock()
        request.scheme = 'http'
        request.GET = {'fetchez': 'la vache', 'code': '342435634blab'}
        request.route_path.return_value = '/facebook/oauth'
        request.registry.settings = settings

        result = prompt_authorize(request.context, request)

        request.route_path.assert_called_once_with('facebook_canvas_oauth')

        expected = """200 OK
Content-Type: text/html; charset=UTF-8
Content-Length: 244

<html>
  <body>
    <script>
      window.top.location = "https://www.facebook.com/dialog/oauth/?client_id=1234567890&redirect_uri=http%3A%2F%2Fapps.facebook.com%2Ffacebook%2Foauth%3Ffetchez%3Dla%2Bvache&scope=";
    </script>
  </body>
</html>"""
        self.assertEqual(expected, str(result))

    def test_canvas(self):
        from pyramid_facebook.canvas import canvas
        request = mock.MagicMock()
        self.assertRaises(NotImplementedError, canvas, request.context, request)


class TestFacebookCanvasDecorator(unittest.TestCase):

    def test_init(self):
        from pyramid_facebook.canvas import facebook_canvas
        from pyramid_facebook.security import ViewCanvas

        dec = facebook_canvas(**{})

        self.assertEqual(ViewCanvas, dec.permission)
        self.assertEqual('facebook_canvas', dec.route_name)
