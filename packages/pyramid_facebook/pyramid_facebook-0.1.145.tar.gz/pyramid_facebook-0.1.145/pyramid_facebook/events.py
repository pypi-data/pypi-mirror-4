# -*- coding: utf-8 -*-
from pyramid.decorator import reify

from pyramid_facebook.lib import Base


class OauthAccept(Base):
    "Event sent when a user accepts app authentication."


class OauthDeny(Base):
    "Event sent when a user denies app authentication."


class DisputedOrder(Base):
    "Event sent when a user disputes an order."


class RefundedOrder(Base):
    "Event sent when a user got refunded for an order."

class PlacedItemOrder(Base):
    "Event sent when a user placed an item order."


class EarnedCurrencyOrder(Base):
    "Event sent when a user placed an currency order."


class ChangeNotification(Base):
    """Event sent when Facebook notifies about a real-time update.

    For more info, read doc on `Facebook Documentation
    <https://developers.facebook.com/docs/reference/api/realtime/>`_.
    """

    @reify
    def json_body(self):
        """:returns: Request body as a dict. Raised an error if body is json
            decoding fails."""
        return self.request.json_body
