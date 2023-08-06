from pyramid.security import has_permission


def includeme(config):
    config.add_subscriber_predicate('matched_route',
                                    MatchedRouteEventPredicate)
    config.add_subscriber_predicate('expected_context', ContextEventPredicate)
    config.add_subscriber_predicate('permission', PermissionEventPredicate)


def request_params_predicate(*required_param_keys, **required_params):
    """Custom predicates to check if required parameter are in request
    parameters. Read :ref:`custom route predicates <pyramid:
    custom_route_predicates>`
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
        if not required.issubset(set(request.params)):
            return False

        if any((k, v) for k, v in required_params.iteritems()
               if v != request.params[k]):
                return False
        return True
    return predicate


def nor_predicate(**params):
    """Custom predicate which checks if a parameter is present with possible
    values being one in list values.

    :param **params: parameter names and values list::

        nor_predicate(param_name=(value1, value2))

    """
    names = set(params.keys())

    def predicate(info, request):
        if not names.issubset(request.params):
            return False
        if any(request.params[n]
               for n in names if request.params[n] not in params[n]):
            return False
        return True
    return predicate


def headers_predicate(*header_names, **headers):
    """Custom predicate which check that `header_names` and  `headers`
    name/value pairs are in `request.headers`.
    """
    def predicate(info, request):
        if any(header for header in header_names
               if header not in request.headers):
            return False
        if any((k, v) for k, v in headers.iteritems()
               if k not in request.headers or request.headers[k] != v):
            return False
        return True
    return predicate


class MatchedRouteEventPredicate(object):

    def __init__(self, route_to_match, config):
        self.route_to_match = route_to_match

    def text(self):
        return u'route_to_match = %s' % self.route_to_match

    # predicate hash
    phash = text

    def __call__(self, event):
        try:
            return event.request.matched_route.name == self.route_to_match
        except AttributeError:
            return False


class ContextEventPredicate(object):
    """Filter a request based event subscriber on context class.
    Only works with request based event which have request as an attribute.
    """

    def __init__(self, expected_context_cls, config):
        self.expected_context_cls = expected_context_cls

    def text(self):
        return u'expected_context_cls = %r' % self.expected_context_cls

    # predicate hash
    phash = text

    def __call__(self, event):
        try:
            return isinstance(event.request.context, self.expected_context_cls)
        except AttributeError:
            return False


class PermissionEventPredicate(object):
    """Filter a request based event subscriber with a permission check.
    Only works with request based event which have request as an attribute.

    :param permission: Permission to check.
    """

    def __init__(self, permission, config):
        self.permission = permission

    def text(self):
        return u'permission = %r' % self.permission

    # predicate hash
    phash = text

    def __call__(self, event):
        try:
            access = has_permission(self.permission, event.request.context,
                                    event.request)
            return access.boolval
        except AttributeError:
            return False
