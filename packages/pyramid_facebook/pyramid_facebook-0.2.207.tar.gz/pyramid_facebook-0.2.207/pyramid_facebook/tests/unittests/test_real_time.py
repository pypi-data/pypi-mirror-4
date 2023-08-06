# -*- coding: utf-8 -*-
import unittest

from facepy import FacepyError
import mock
from pyramid.httpexceptions import HTTPOk, HTTPForbidden


class TestRealTimeSubscriptions(unittest.TestCase):

    @mock.patch('pyramid_facebook.real_time.nor_predicate')
    @mock.patch('pyramid_facebook.real_time.headers_predicate')
    @mock.patch('pyramid_facebook.real_time.request_params_predicate')
    def test_includeme(self, m_req_predicate, m_header_predicate, m_nor_predicate):
        from pyramid_facebook.real_time import includeme
        config = mock.Mock()

        self.assertIsNone(includeme(config))

        self.assertEqual(5, config.add_route.call_count)

        expected = mock.call(
            'facebook_real_time_subscription_verification',
            '/real-time',
            request_method='GET',
            custom_predicates=[
                m_req_predicate.return_value,
                ]
            )
        self.assertEqual(expected, config.add_route.call_args_list[0])

        expected = mock.call(
            'facebook_real_time_notification',
            '/real-time',
            request_method='POST',
            factory='pyramid_facebook.security.RealTimeNotificationContext',
            custom_predicates=[m_header_predicate.return_value]
            )
        self.assertEqual(expected, config.add_route.call_args_list[1])

        expected = mock.call(
            'facebook_real_time_subscriptions',
            '/real-time/subscriptions',
            request_method='GET',
            request_param='access_token',
            factory='pyramid_facebook.security.AdminContext',
            )
        self.assertEqual(expected, config.add_route.call_args_list[2])

        expected = mock.call(
            'facebook_real_time_subscriptions_update',
            '/real-time/subscriptions',
            request_method='POST',
            custom_predicates=[
                m_nor_predicate.return_value,
                m_req_predicate.return_value
                ],
            factory='pyramid_facebook.security.AdminContext',
            )
        self.assertEqual(expected, config.add_route.call_args_list[3])

        expected = mock.call(
            'facebook_real_time_subscriptions_delete',
            '/real-time/subscriptions',
            request_method='DELETE',
            request_param='access_token',
            factory='pyramid_facebook.security.AdminContext',
            )
        self.assertEqual(expected, config.add_route.call_args_list[4])

        self.assertEqual(2, m_req_predicate.call_count)

        self.assertEqual(
            mock.call('hub.challenge','hub.verify_token',**{'hub.mode': 'subscribe'}),
            m_req_predicate.call_args_list[0]
            )
        self.assertEqual(
            mock.call('fields', 'access_token'),
            m_req_predicate.call_args_list[1]
            )

        m_header_predicate.assert_called_once_with(
            'X-Hub-Signature',
            **{'Content-Type': 'application/json'}
            )

        m_nor_predicate.assert_called_once_with(object=('user', 'permissions', 'page', 'errors'))


    @mock.patch('pyramid_facebook.real_time.get_application_access_token')
    def test_verify_real_time_subscription(self, m_req):
        from pyramid_facebook.real_time import verify_real_time_subscription

        m_req.return_value = 'token'

        request = mock.MagicMock()
        request.params = {
            'hub.verify_token':'token',
            'hub.challenge': 'challenge'
            }

        result = verify_real_time_subscription(request)

        self.assertEqual(request.params['hub.challenge'], result.body)

    @mock.patch('pyramid_facebook.real_time.get_application_access_token')
    def test_verify_real_time_subscription_wrong_token(self, m_req):
        from pyramid_facebook.real_time import verify_real_time_subscription

        m_req.return_value = 'not the same token'

        request = mock.MagicMock()
        request.params = {
            'hub.verify_token':'token',
            'hub.challenge': 'challenge'
            }

        self.assertRaises(HTTPForbidden, verify_real_time_subscription, request)


    @mock.patch('pyramid_facebook.real_time.get_application_access_token')
    def test_verify_real_time_subscription_facepy_error(self, m_req):
        from pyramid_facebook.real_time import verify_real_time_subscription

        m_req.side_effect = FacepyError('shit happens.')

        request = mock.MagicMock()
        request.params = {
            'hub.verify_token':'token',
            'hub.challenge': 'challenge'
            }

        self.assertRaises(HTTPForbidden, verify_real_time_subscription, request)


    @mock.patch('pyramid_facebook.real_time.GraphAPI')
    @mock.patch('pyramid_facebook.real_time.get_application_access_token')
    def test_list_real_time_subscriptions(self, m_get_token, m_graph_api):
        from pyramid_facebook.real_time import list_real_time_subscriptions

        request = mock.MagicMock()

        result = list_real_time_subscriptions(request)

        self.assertEqual(m_graph_api.return_value.get.return_value, result)

        m_get_token.assert_called_once_with(
            request.registry.settings.__getitem__.return_value,
            request.registry.settings.__getitem__.return_value,
            )

        self.assertEqual(2, request.registry.settings.__getitem__.call_count)
        self.assertEqual(
            mock.call('facebook.app_id'),
            request.registry.settings.__getitem__.call_args_list[0]
            )
        self.assertEqual(
            mock.call('facebook.secret_key'),
            request.registry.settings.__getitem__.call_args_list[1]
            )

        m_graph_api.assert_called_once_with(m_get_token.return_value)
        m_graph_api.return_value.get.assert_called_once_with(
            '%s/subscriptions' % request.registry.settings.__getitem__.return_value,
            )

    @mock.patch('pyramid_facebook.real_time.GraphAPI')
    @mock.patch('pyramid_facebook.real_time.get_application_access_token')
    def test_update_real_time_subscriptions(self, m_get_token, m_graph_api):
        from pyramid_facebook.real_time import update_real_time_subscription

        request = mock.MagicMock()

        result = update_real_time_subscription(request)

        self.assertEqual(m_graph_api.return_value.post.return_value, result)

        m_get_token.assert_called_once_with(
            request.registry.settings.__getitem__.return_value,
            request.registry.settings.__getitem__.return_value,
            )

        self.assertEqual(3, request.registry.settings.__getitem__.call_count)
        self.assertEqual(
            mock.call('facebook.app_id'),
            request.registry.settings.__getitem__.call_args_list[0]
            )
        self.assertEqual(
            mock.call('facebook.secret_key'),
            request.registry.settings.__getitem__.call_args_list[1]
            )
        self.assertEqual(
            mock.call('facebook.app_id'),
            request.registry.settings.__getitem__.call_args_list[2]
            )

        request.route_url.assert_called_once_with(
            'facebook_real_time_subscription_verification'
            )

        m_graph_api.assert_called_once_with(m_get_token.return_value)

        m_graph_api.return_value.post.assert_called_once_with(
            '%s/subscriptions' % request.registry.settings.__getitem__.return_value,
            object=request.params.__getitem__.return_value,
            fields=request.params.__getitem__.return_value,
            callback_url=request.route_url.return_value,
            verify_token=m_get_token.return_value,
            )

    @mock.patch('pyramid_facebook.real_time.GraphAPI')
    @mock.patch('pyramid_facebook.real_time.get_application_access_token')
    def test_delete_real_time_subscriptions(self, m_get_token, m_graph_api):
        from pyramid_facebook.real_time import delete_real_time_subscription

        request = mock.MagicMock()

        delete_real_time_subscription(request)

        request.params.get.assert_called_once_with('object')

        self.assertEqual(
            mock.call('facebook.app_id'),
            request.registry.settings.__getitem__.call_args_list[0]
            )
        self.assertEqual(
            mock.call('facebook.secret_key'),
            request.registry.settings.__getitem__.call_args_list[1]
            )
        self.assertEqual(
            mock.call('facebook.app_id'),
            request.registry.settings.__getitem__.call_args_list[2]
            )

        m_get_token.assert_called_once_with(
            request.registry.settings.__getitem__.return_value,
            request.registry.settings.__getitem__.return_value,
            )

        m_graph_api.assert_called_once_with(m_get_token.return_value)

        m_graph_api.return_value.delete.assert_called_once_with(
            '%s/subscriptions' % request.registry.settings.__getitem__.return_value,
            object=request.params.get.return_value,
            )

    def test_render_facepy_error(self):
        from pyramid_facebook.real_time import render_facepy_error
        exc = FacepyError('error message')
        exc.code = 190

        result = render_facepy_error(exc, None)

        self.assertEqual(
            dict(error=dict(type='FacepyError', code=190, message='error message')),
            result
            )

    @mock.patch('pyramid_facebook.real_time.ChangeNotification')
    def test_process_real_time_notification(self, m_change):
        from pyramid_facebook.real_time import process_real_time_notification
        request = mock.Mock()

        result = process_real_time_notification(request.context, request)

        self.assertIsInstance(result, HTTPOk)

        request.registry.notify.assert_called_once_with(m_change.return_value)

        m_change.assert_called_once_with(request.context, request)
