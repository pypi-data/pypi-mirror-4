# -*- coding: utf-8 -*-
import json
import unittest

from pyramid.request import Request


class TestChangeNotification(unittest.TestCase):

    def test_json_body(self):
        from pyramid_facebook.events import ChangeNotification

        obj = dict(a=123, b=4321)
        request = Request(dict(), body=json.dumps(obj))

        cn = ChangeNotification(None, request)

        self.assertIsInstance(cn.json_body, dict)
        self.assertEqual(obj, cn.json_body)
