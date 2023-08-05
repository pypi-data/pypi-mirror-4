# -*- coding: utf-8 -*-
import base64
import hashlib
import hmac
import json


js_redirect_tpl = """<html>
  <body>
    <script>
      window.top.location = "%(location)s";
    </script>
  </body>
</html>"""


class Base(object):
    "Base class for views and events"
    def __init__(self, context, request):
        # request and context as properties to prevent modification
        self._context = context
        self._request = request

    @property
    def context(self):
        """Route context which can be of 2 types:

        * :class:`~pyramid_facebook.security.SignedRequestContext`
        * :class:`~pyramid_facebook.security.FacebookCreditsContext`
        """
        return self._context

    @property
    def request(self):
        "Request object for this route."
        return self._request


def _base64_url_encode(inp):
    """ Facebook base64 decoder based on `Sunil Arora's blog post
    <http://sunilarora.org/parsing-signedrequest-parameter-in-python-bas>`_.

    :param inp: input `str` to be encoded
    :return: `base64` encoded utf8 unicode data
    """
    return unicode(base64.b64encode(inp, '-_').strip('=').encode('utf8'))


def encrypt_signed_request(secret_key, data):
    """Encrypts data the way facebook does for permit testing. Adds algorithm
    key to dict.

    :param secret_key: Facebook application' secret key.
    :param data: a dictionary of data to sign.
    :return: Signed request as defined by `Facebook documentation
             <http://developers.facebook.com/docs/authentication/signed_request/>`_

    """
    data = data.copy()
    data.update(algorithm='HMAC-SHA256')

    payload = _base64_url_encode(json.dumps(data)).encode('utf8')
    signature = _base64_url_encode(
        hmac.new(
            secret_key.encode('utf8'),
            msg=payload.encode('utf8'),
            digestmod=hashlib.sha256
            ).digest()
        )
    return '%s.%s' % (signature, payload)


def request_params_predicate(*required_param_keys, **required_params):
    """Custom predicates to check if required parameter are in request
    parameters. Read :ref:`custom route predicates <pyramid:custom_route_predicates>`
    for more info::

        # /example?param1&param2=321
        config.add_route(
            'example',
            '/example',
            custom_predicates=[request_params_predicate('param1', param2=321)]
            )
    """
    required = set(required_param_keys)
    def predicate(info, request):
        if not required.issubset(set(request.params.keys())):
            return False
        for k, v in required_params.items():
            if v != request.params.get(k):
                return False
        return True
    return predicate


def nor_predicate(**params):
    """Custom predicate which checks if a parameter is present with possible
    values being one in list values.

    :param params: A dictionary structured as `dict(param_name=(value1, value2))`
    """
    names = set(params.keys())
    def predicate(info, request):
        if not names.issubset(request.params):
            return False
        if [request.params[n] for n in names if request.params[n] not in params[n]]:
            return False
        return True
    return predicate


def headers_predicate(*header_names, **headers):
    """Custom predicate which check that `header_names` and  `headers` name/value
    pairs are in `request.headers`.
    """
    def predicate(info, request):
        if [_ for _ in header_names if _ not in request.headers]:
            return False
        if [(k, v) for k, v in headers.iteritems() if k not in request.headers or
            request.headers[k] != v]:
            return False
        return True
    return predicate
