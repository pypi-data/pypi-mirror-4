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
