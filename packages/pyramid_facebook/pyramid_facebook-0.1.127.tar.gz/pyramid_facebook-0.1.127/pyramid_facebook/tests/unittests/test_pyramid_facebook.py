# -*- coding: utf-8 -*-
import unittest

import mock

class TestPyramidFacebook(unittest.TestCase):

    @mock.patch('pyramid_facebook.FacebookAuthenticationPolicy')
    @mock.patch('pyramid_facebook.ACLAuthorizationPolicy')
    def test_includeme(self, m_acl_policy, m_fb_policy):
        settings = {
            'facebook.namespace': 'namespace',
            'facebook.secret_key': 'secret_key'
            }

        config = mock.Mock()
        config.registry.settings = settings

        # TEST includeme
        from pyramid_facebook import includeme
        self.assertIsNone(includeme(config))

        # now we check if everything went as expected:
        m_fb_policy.assert_called_once_with()
        m_acl_policy.assert_called_once_with()

        config.set_authentication_policy.assert_called_once_with(
            m_fb_policy.return_value
            )
        config.set_authorization_policy.assert_called_once_with(
            m_acl_policy.return_value
            )

        self.assertEqual(4, config.include.call_count)
        prefix = '/namespace'

        self.assertEqual(
            mock.call('pyramid_facebook.auth', route_prefix=prefix),
            config.include.call_args_list[0]
            )

        self.assertEqual(
            mock.call('pyramid_facebook.canvas', route_prefix=prefix),
            config.include.call_args_list[1]
            )

        self.assertEqual(
            mock.call('pyramid_facebook.credits', route_prefix=prefix),
            config.include.call_args_list[2]
            )

        self.assertEqual(
            mock.call('pyramid_facebook.real_time', route_prefix=prefix),
            config.include.call_args_list[3]
            )

    @mock.patch('pyramid_facebook.FacebookAuthenticationPolicy')
    @mock.patch('pyramid_facebook.ACLAuthorizationPolicy')
    def test_includeme_exception(self, m_acl_policy, m_fb_policy):
        from pyramid_facebook import includeme
        bad_settings = {}

        config = mock.MagicMock()
        config.registry.settings = bad_settings

        self.assertRaises(KeyError, includeme, config)

        bad_settings = {
            'facebook.secret_key': 'secret_key'
        }

        config.registry.settings = bad_settings
        self.assertRaises(KeyError, includeme, config)
