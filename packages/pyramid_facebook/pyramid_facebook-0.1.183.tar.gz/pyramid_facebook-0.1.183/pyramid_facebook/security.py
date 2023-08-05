# -*- coding: utf-8 -*-
import hashlib
import hmac
import json
import logging

from facepy import FacepyError, GraphAPI, SignedRequest
from facepy.exceptions import SignedRequestError

from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.authentication import CallbackAuthenticationPolicy
from pyramid.decorator import reify
from pyramid.security import Allow

from pyramid_facebook.events import UserSignedRequestParsed

log = logging.getLogger(__name__)

RETRY_NB = 3

ViewCanvas = u'view_canvas'
Authenticate = u'authenticate'
UpdateSubscription = u'update_subscription'
NotifyRealTimeChanges = u'notify_real_time_changes'

FacebookUser = u'facebook-user'
RegisteredUser = u'registered-user'
AdminUser = u'admin-user'
# real time updates https://developers.facebook.com/docs/reference/api/realtime
XHubSigned = u'x-hub-signed'


def includeme(config):
    config.set_authentication_policy(FacebookAuthenticationPolicy())
    config.set_authorization_policy(ACLAuthorizationPolicy())


class SignedRequestContext(object):
    "Security context for facebook signed request routes."

    __acl__ = [
        (Allow, FacebookUser, Authenticate),
        (Allow, RegisteredUser, ViewCanvas),
        ]

    def __init__(self, request):
        self.request = request

    @property
    def facebook_data(self):
        """Contains facebook data provided in ``signed_request`` parameter
        decrypted with :meth:`SignedRequest.parse <facepy.SignedRequest.parse>`
        """
        try:
            return self._facebook_data
        except AttributeError:
            return None

    @facebook_data.setter
    def facebook_data(self, value):
        self._facebook_data = value

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
        status updates <http://developers.facebook.com/docs/credits/callback/
        #payments_status_update>`_."""
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
        <http://developers.facebook.com/docs/credits/callback/
        #payments_status_update_earn_app_currency>`_."""
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
        self._user_dict = {}
        self._user_id = None

    @property
    def user_dict(self):
        return self._user_dict

    @user_dict.setter
    def user_dict(self, value):
        self._user_dict = value

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        self._user_id = value


class AdminContext(AccessTokenContext):
    """Context which defines principals as facebook application id list that
    user administrates.
    """

    def __init__(self, request):
        super(AdminContext, self).__init__(request)
        self.__acl__ = (
            (Allow, request.registry.settings['facebook.app_id'],
             UpdateSubscription),
            )


class RealTimeNotificationContext(object):
    "Context for real-time changes notification route."

    __acl__ = (
        (Allow, XHubSigned, NotifyRealTimeChanges),
        )

    def __init__(self, request):
        self.request = request


class FacebookAuthenticationPolicy(CallbackAuthenticationPolicy):

    unauthenticated_methods = None
    effective_principals_methods = None

    def __init__(self, *args, **kwargs):
        super(FacebookAuthenticationPolicy, self).__init__(*args, **kwargs)

        self.unauthenticated_methods = {
            SignedRequestContext: self._parse_signed_request,
            FacebookCreditsContext: self._parse_signed_request,
            AccessTokenContext: self._validate_access_token,

            RealTimeNotificationContext: lambda req: None,
            }

        self.effective_principals_methods = {
            SignedRequestContext: self._get_principals_from_signed_request,
            FacebookCreditsContext: self._get_principals_from_signed_request,
            AccessTokenContext: self._get_principals_from_access_token,
            RealTimeNotificationContext: self._get_principals_from_signature,
            AdminContext: self._get_principals_from_admin_context,
            }

    def unauthenticated_userid(self, request):
        try:
            method = self.unauthenticated_methods[request.context.__class__]
        except KeyError:
            return None
        else:
            return method(request)

    def effective_principals(self, request):
        cls = FacebookAuthenticationPolicy
        p = super(cls, self).effective_principals(request)
        context = request.context
        try:
            method = self.effective_principals_methods[context.__class__]
        except KeyError:
            pass
        else:
            p.extend(method(request))
        return p

    def remember(self, request, principal, **kwargs):
        return []

    def forget(self, request):
        return []

    def callback(self, user_id, request):
        # by default, having a user id means that user is registered
        return [RegisteredUser]

    def _parse_signed_request(self, request):
        context = request.context
        if 'signed_request' not in request.params:
            return None
        context.facebook_data = None
        try:
            context.facebook_data = SignedRequest.parse(
                request.params[u'signed_request'],
                request.registry.settings[u'facebook.secret_key'],
                )
        except SignedRequestError:
            log.warn(
                'SignedRequestError with signature: %s',
                request.params['signed_request'],
                exc_info=True
                )
            return None
        try:
            user_id = int(context.facebook_data[u'user_id'])
        except KeyError:
            # user_id not in facebook_data => user has not authorized app
            log.debug('User has not authorized app.')
        except ValueError:
            log.warn('Invalid user id %r', context.facebook_data[u'user_id'])
        else:
            request.registry.notify(
                UserSignedRequestParsed(request.context, request)
                )
            return user_id
        return None

    def _validate_access_token(self, request):
        try:
            access_token = request.params['access_token']
        except KeyError:
            return None
        request.context.access_token = access_token
        api = GraphAPI(access_token)
        try:
            request.context.user_dict = api.get('me', retry=RETRY_NB)
        except FacepyError:
            log.warn('Authentication failed', exc_info=True)
        try:
            request.context.user_id = long(request.context.user_dict['id'])
            return request.context.user_id
        except KeyError:
            return None
        except ValueError:
            log.warn('Malformated Facebook response', exc_info=True)
        return None

    def _get_principals_from_signed_request(self, request):
        try:
            if request.context.facebook_data['user_id']:
                return [FacebookUser]
        except:
            pass
        return []

    def _get_principals_from_access_token(self, request):
        p = []
        if request.context.user_id:
            p.append(FacebookUser)
        return p

    def _get_principals_from_admin_context(self, request):
        p = self._get_principals_from_access_token(request)

        try:
            return p + request.context.application_ids
        except AttributeError:
            pass
        # check what apps user owns.
        api = GraphAPI(request.params['access_token'])
        try:
            accounts = api.get('me/accounts', retry=RETRY_NB)
        except FacepyError:
            log.warn('Get accounts failed', exc_info=True)
        else:
            request.context.application_ids = [app['id']
                                               for app in accounts['data']]
            p.extend(request.context.application_ids)
        return p

    def _get_principals_from_signature(self, request):
        # route predicates already check presence of X-Hub-Signature header
        sig = request.headers[u'X-Hub-Signature']
        verif = hmac.new(
            request.registry.settings['facebook.secret_key'],
            request.body,
            hashlib.sha1
            ).hexdigest()
        if sig == ('sha1=%s' % verif):
            return [XHubSigned]
        else:
            log.warn(
                'X-Hub-Signature invalid - expected %s, received %s',
                verif,
                sig,
                )
        return []
