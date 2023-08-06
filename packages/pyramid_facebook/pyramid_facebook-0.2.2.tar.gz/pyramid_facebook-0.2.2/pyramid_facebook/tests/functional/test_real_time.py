# -*- coding: utf-8 -*-
import mock

from facepy.exceptions import OAuthError

from pyramid_facebook.tests import conf
from pyramid_facebook.tests.functional import TestView


class TestRealTimeSubscription(TestView):

    def _get_namespace(self):
        return conf['facebook.namespace']

    @mock.patch('pyramid_facebook.real_time.get_application_access_token')
    def test_verify_real_time_subscription(self, m_token):
        m_token.return_value = u'token'

        result = self.app.get(
            '/%s/real-time' % self._get_namespace(),
            {
                'hub.mode': 'subscribe',
                'hub.challenge': u'a challenge to return if success',
                'hub.verify_token': u'token',
                }
            )
        self.assertEqual(u'a challenge to return if success', result.body)

    @mock.patch('pyramid_facebook.real_time.get_application_access_token')
    def test_verify_real_time_subscription_exception(self, m_token):
        m_token.side_effect = OAuthError(code=190, message='Invalid Secret Key')

        self.app.get(
            '/%s/real-time' % self._get_namespace(),
            {
                'hub.mode': 'subscribe',
                'hub.challenge': u'a challenge to return if success',
                'hub.verify_token': u'token',
                },
            status=403,
            )

    @mock.patch('pyramid_facebook.real_time.get_application_access_token')
    def test_verify_real_time_subscription_not_good_token(self, m_token):
        m_token.return_value = u'token'

        self.app.get(
            '/%s/real-time' % self._get_namespace(),
            {
                'hub.mode': 'subscribe',
                'hub.challenge': u'a challenge to return if success',
                'hub.verify_token': u'not the good token',
                },
            status=403,
            )

    @mock.patch('pyramid_facebook.real_time.get_application_access_token')
    @mock.patch('pyramid_facebook.real_time.GraphAPI')
    def test_list_real_time_subscription(self, m_graph_api, m_token):
        m_graph_api.return_value.get.return_value = dict(
            data=[
                dict(
                    active=True,
                    fields=["friends"],
                    object="user",
                    callback_url="http://wow/ww_dev_local_app/real-time"
                    )
                ]
            )
        result = self.permissive_app.get(
            '/%s/real-time/subscriptions' % self._get_namespace(),
            {
                'access_token': 'token'
                }
            )

        self.assertEqual(m_graph_api.return_value.get.return_value, result.json)

    @mock.patch('pyramid_facebook.real_time.get_application_access_token')
    @mock.patch('pyramid_facebook.real_time.GraphAPI')
    def test_list_real_time_subscription_facepy_error(self, m_graph_api, m_token):
        m_graph_api.return_value.get.side_effect = OAuthError(code=190, message='Invalid Secret Key')

        result = self.permissive_app.get(
            '/%s/real-time/subscriptions' % self._get_namespace(),
            {
                'access_token': 'token'
                }
            )
        self.assertEqual(
            {"error": {"message": "Invalid Secret Key", "code": 190, "type": "OAuthError"}},
            result.json
            )

    @mock.patch('pyramid_facebook.real_time.get_application_access_token')
    @mock.patch('pyramid_facebook.real_time.GraphAPI')
    def test_update_real_time_subscription(self, m_graph_api, m_token):
        m_graph_api.return_value.post.return_value = None
        m_token.return_value = 'token'

        result = self.permissive_app.post(
            '/%s/real-time/subscriptions' % self._get_namespace(),
            {
                'access_token': 'token',
                'object': 'user',
                'fields': 'friends,name',
                }
            )
        # facebook returns 'null' which decodes as None
        self.assertIsNone(result.json)

        m_graph_api.return_value.post.assert_called_once_with(
            '%s/subscriptions' % conf['facebook.app_id'],
            object='user',
            fields='friends,name',
            callback_url='http://localhost/%s/real-time' % conf['facebook.namespace'],
            verify_token='token',
            )


    @mock.patch('pyramid_facebook.real_time.get_application_access_token')
    @mock.patch('pyramid_facebook.real_time.GraphAPI')
    def test_update_real_time_subscription_facepy_error(self, m_graph_api, m_token):
        m_graph_api.return_value.post.side_effect = OAuthError(code=190, message='Invalid Secret Key')

        result = self.permissive_app.post(
            '/%s/real-time/subscriptions' % self._get_namespace(),
            {
                'access_token': 'token',
                'object': 'user',
                'fields': 'friends,name',
                }
            )

        self.assertEqual(
            {"error": {"message": "Invalid Secret Key", "code": 190, "type": "OAuthError"}},
            result.json
            )

    @mock.patch('pyramid_facebook.real_time.get_application_access_token')
    @mock.patch('pyramid_facebook.real_time.GraphAPI')
    def test_delete_real_time_subscription(self, m_graph_api, m_token):
        m_graph_api.return_value.delete.return_value = None
        m_token.return_value = 'token'

        result = self.permissive_app.delete(
            '/%s/real-time/subscriptions?access_token=token' % self._get_namespace(),
            )
        # facebook returns 'null' which decodes as None
        self.assertIsNone(result.json)

    @mock.patch('pyramid_facebook.real_time.get_application_access_token')
    @mock.patch('pyramid_facebook.real_time.GraphAPI')
    def test_delete_real_time_subscription_facepy_error(self, m_graph_api, m_token):
        m_graph_api.return_value.delete.side_effect = OAuthError(code=190, message='Invalid Secret Key')

        result = self.permissive_app.delete(
            '/%s/real-time/subscriptions?access_token=token' % self._get_namespace(),
            )

        self.assertEqual(
            {"error": {"message": "Invalid Secret Key", "code": 190, "type": "OAuthError"}},
            result.json
            )

    def test_process_real_time_notification(self):
        headers={'X-Hub-Signature': 'signature', 'Content-Type': 'application/json'}
        result = self.permissive_app.post(
            '/%s/real-time' % self._get_namespace(),
            params='{"object":"user","entry":[{"uid":"1351121254","id":"1351121254","time":1344440243,"changed_fields":["name"]}]}',
            headers=headers,
            )

        self.assertEqual('200 OK', result.status)

    @mock.patch('pyramid_facebook.real_time.ChangeNotification')
    def test_process_real_time_notification_internal_server_error(self, m_event):
        m_event.side_effect = Exception()
        headers={'X-Hub-Signature': 'signature', 'Content-Type': 'application/json'}

        self.permissive_app.post(
            '/%s/real-time' % self._get_namespace(),
            params='{"object":"user","entry":[{"uid":"1351121254","id":"1351121254","time":1344440243,"changed_fields":["name"]}]}',
            headers=headers,
            status=500
            )
