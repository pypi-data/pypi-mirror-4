# -*- coding: utf-8 -*-
import hashlib
import hmac
import json
import logging

from facepy import FacepyError, GraphAPI, SignedRequest
from facepy.exceptions import SignedRequestError

from pyramid.authentication import CallbackAuthenticationPolicy
from pyramid.decorator import reify
from pyramid.security import Allow

log = logging.getLogger(__name__)

ViewCanvas = 'view_canvas'
Authenticate = 'authenticate'
UpdateSubscription = 'update_subscription'
NotifyRealTimeChanges = 'notify_real_time_changes'

FacebookUser = 'facebook-user'
RegisteredUser = 'registered-user'
AdminUser = 'admin_user'
XHubSigned = 'x-hub-signed' # real time updates https://developers.facebook.com/docs/reference/api/realtime/


class SignedRequestContext(object):
    "Security context for facebook signed request routes."

    __acl__ = [
        (Allow, FacebookUser, Authenticate),
        (Allow, RegisteredUser, ViewCanvas),
        ]

    def __init__(self, request):
        self.request = request

    def unauthenticated_userid(self):
        try:
            return int(self.facebook_data["user_id"])
        except KeyError:
            # user_id not in facebook_data => user has not authorized app
            log.debug('User has not authorized app.')
        except ValueError:
            log.warn('Invalid user id %r', self.facebook_data["user_id"])
        except TypeError:
            # in case signature is malformated. fb_data inexists
            # no need to log as it is already done in __init__
            pass
        return None

    def effective_principals(self):
        if self.unauthenticated_userid():
            return [FacebookUser]
        return []

    @reify
    def facebook_data(self):
        """Contains facebook data provided in ``signed_request`` parameter
        decrypted with :meth:`SignedRequest.parse <facepy.SignedRequest.parse>`.
        """
        if self.request.params.get('signed_request'):
            try:
                return SignedRequest.parse(
                    self.request.params['signed_request'],
                    self.request.registry.settings['facebook.secret_key'],
                    )
            except SignedRequestError as e:
                log.warn(
                    '%r with signature: %s',
                    e,
                    self.request.params['signed_request']
                    )
        return None

    @reify
    def user(self):
        return self.facebook_data['user']

    @reify
    def user_country(self):
        return self.user['country']

    def __repr__(self):
        return '<%s facebook_data=%r>' % (
            self.__class__.__name__,
            self.facebook_data
            )


class FacebookCreditsContext(SignedRequestContext):
    "Context for facebook credits callback requests."

    @reify
    def order_details(self):
        """Order details received in `facebook credits callback for payment
        status updates <http://developers.facebook.com/docs/credits/callback/#payments_status_update>`_."""
        return json.loads(
            self.facebook_data['credits']['order_details']
            )

    @reify
    def order_info(self):
        """Order info being the order information passed when the `FB.ui method
        <http://developers.facebook.com/docs/reference/javascript/FB.ui/>`_
        is invoked."""
        return self.facebook_data["credits"]["order_info"]

    @reify
    def earned_currency_data(self):
        """Modified field received in `facebook credits callback for payment
        status update for earned app currency
        <http://developers.facebook.com/docs/credits/callback/#payments_status_update_earn_app_currency>`_."""
        data = self.item['data']
        if data:
            try:
                data = json.loads(data)
                data = data['modified'] if 'modified' in data else None
            except:
                data = None
        return data

    @reify
    def item(self):
        """The item info as passed when `FB.ui method
        <http://developers.facebook.com/docs/reference/javascript/FB.ui/>`_
        is invoked."""
        return self.order_details['items'][0]


class AccessTokenContext(object):

    def __init__(self, request):
        self.request = request

    @reify
    def user_dict(self):
        self.access_token = self.request.params.get('access_token')
        if self.access_token:
            try:
                return GraphAPI(self.access_token).get('me', retry=0)
            except FacepyError as e:
                log.warn('Authentication failed: %r', e)
        return dict()

    def unauthenticated_userid(self):
        return long(self.user_dict['id']) if 'id' in self.user_dict else None

    def effective_principals(self):
        p = []
        if self.unauthenticated_userid():
            p.append(FacebookUser)
        return p


class AdminContext(AccessTokenContext):
    """Context which defines principals as facebook application id list that user
    administrates."""

    def __init__(self, request):
        super(AdminContext, self).__init__(request)
        self.principals = None
        self.__acl__ = (
            (Allow, request.registry.settings['facebook.app_id'], UpdateSubscription),
            )

    def effective_principals(self):
        if self.principals is None:
            self.principals = super(AdminContext, self).effective_principals()
            # check what apps user owns.
            try:
                accounts = GraphAPI(self.access_token).get('me/accounts', retry=0)
                self.principals.extend([a['id'] for a in accounts['data']])
            except FacepyError as e:
                log.warn('Get accounts failed: %r', e)
        return self.principals


class RealTimeNotificationContext(object):
    "Context for real-time changes notification route."

    __acl__ = (
        (Allow, XHubSigned, NotifyRealTimeChanges),
        )

    def __init__(self, request):
        self.request = request
        self.principals = None

    def effective_principals(self):
        if self.principals is None:
            # route predicates already check presence of X-Hub-Signature header
            sig = self.request.headers['X-Hub-Signature']
            verif = hmac.new(
                self.request.registry.settings['facebook.secret_key'],
                self.request.body,
                hashlib.sha1
                ).hexdigest()
            if sig == ('sha1=%s' % verif):
                self.principals = (XHubSigned, )
            else:
                log.warn(
                    'X-Hub-Signature invalid - expected %s, received %s',
                    verif,
                    sig,
                    )
                self.principals = tuple()
        return self.principals


class FacebookAuthenticationPolicy(CallbackAuthenticationPolicy):

    def unauthenticated_userid(self, request):
        try:
            return request.context.unauthenticated_userid()
        except AttributeError:
            return None

    def effective_principals(self, request):
        p = super(FacebookAuthenticationPolicy, self).effective_principals(request)
        try:
            p.extend(request.context.effective_principals())
        except AttributeError:
            pass
        return p

    def remember(self, request, principal, **kwargs):
        return []

    def forget(self, request):
        return []

    def callback(self, user_id, request):
        # by default, having a user id means that user is registered
        return [RegisteredUser]
