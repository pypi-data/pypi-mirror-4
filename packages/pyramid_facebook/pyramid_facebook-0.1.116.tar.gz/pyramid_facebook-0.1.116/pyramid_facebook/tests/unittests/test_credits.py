# -*- coding: utf-8 -*-
import unittest

import mock

from pyramid.httpexceptions import HTTPOk


class TestFacebookPaymentsGetItemsDecorator(unittest.TestCase):

    @mock.patch('pyramid_facebook.credits.request_params_predicate')
    def test_includeme(self, m_predicate):
        from pyramid_facebook.credits import includeme

        config = mock.Mock()

        self.assertIsNone(includeme(config))

        self.assertEqual(4, config.add_route.call_count)

        expected = mock.call(
            'facebook_payments_get_items',
            '/credits',
            request_method='POST',
            custom_predicates=[
                m_predicate.return_value
                ],
            factory='pyramid_facebook.security.FacebookCreditsContext',
            )
        self.assertEqual(expected, config.add_route.call_args_list[0])

        expected = mock.call(
            'facebook_payments_status_update_placed',
            '/credits',
            request_method='POST',
            custom_predicates=[
                m_predicate.return_value,
                m_predicate.return_value,
                ],
            factory='pyramid_facebook.security.FacebookCreditsContext',
            )
        self.assertEqual(expected, config.add_route.call_args_list[1])

        expected = mock.call(
            'facebook_payments_status_update_disputed',
            '/credits',
            request_method='POST',
            custom_predicates=[
                m_predicate.return_value,
                m_predicate.return_value,
                ],
            factory='pyramid_facebook.security.FacebookCreditsContext',
            )
        self.assertEqual(expected, config.add_route.call_args_list[2])

        expected = mock.call(
        'facebook_payments_status_update_refunded',
        '/credits',
        request_method='POST',
        custom_predicates=[
                m_predicate.return_value,
                m_predicate.return_value,
            ],
        factory='pyramid_facebook.security.FacebookCreditsContext',
        )
        self.assertEqual(expected, config.add_route.call_args_list[3])

        config.scan.assert_called_once_with(package='pyramid_facebook.credits')

        self.assertEqual(5, m_predicate.call_count)

        expected = mock.call(
            'signed_request',
            'buyer',
            'receiver',
            'order_id',
            'order_info',
            method='payments_get_items',
            )
        self.assertEqual(expected, m_predicate.call_args_list[0])

        expected = mock.call(
            'signed_request',
            'order_details',
            'order_id',
            method='payments_status_update',
            )
        self.assertEqual(expected, m_predicate.call_args_list[1])

        self.assertEqual(mock.call(status='placed'), m_predicate.call_args_list[2])
        self.assertEqual(mock.call(status='disputed'), m_predicate.call_args_list[3])
        self.assertEqual(mock.call(status='refunded'), m_predicate.call_args_list[4])

    @mock.patch('pyramid_facebook.credits.venusian')
    def test_call(self, m_venusian):
        from pyramid_facebook.credits import facebook_payments_get_items
        wrapped = mock.Mock()

        dec = facebook_payments_get_items()
        res = dec(wrapped)

        m_venusian.attach.assert_called_once_with(wrapped, dec._register)
        self.assertEqual(wrapped, res)

    def test_register(self):
        from pyramid_facebook.security import ViewCanvas
        from pyramid_facebook.credits import facebook_payments_get_items
        wrapped = mock.Mock()
        scanner = mock.Mock()
        scanner.config = config = mock.Mock()

        dec = facebook_payments_get_items()
        dec._decorate = mock.Mock()

        dec._register(scanner, 'name', wrapped)

        config.add_view.assert_called_once_with(
            view=dec._decorate.return_value,
            permission=ViewCanvas,
            route_name='facebook_payments_get_items',
            renderer='json',
            )

    def test_validate(self):
        from pyramid_facebook.credits import facebook_payments_get_items

        dec = facebook_payments_get_items()

        self.assertRaises(TypeError, dec._validate, ['not_a_dict'])

        self.assertRaises(TypeError, dec._validate, {'not': 'good_keys'})

        bad_type = {
            'title'      : u"A title",
            'description': u"A description",
            'price'      : 1.2,  # not an int
            'image_url'  : "can be a wrong url :-(",
            }
        self.assertRaises(TypeError, dec._validate, bad_type)

        good_content =  {
            'title'      : u"A title",
            'description': u"A description",
            'price'      : 100,
            'image_url'  : u"any str or unicode",
            }

        self.assertEqual(good_content, dec._validate(good_content))

    def test_decorate(self):
        from pyramid_facebook.credits import facebook_payments_get_items
        context = mock.MagicMock()
        request = mock.Mock()
        # set function attributes needed by functools.wraps
        wrapped = mock.Mock()
        wrapped.__name__ = 'somefunction'

        dec = facebook_payments_get_items()
        dec._validate = mock.Mock()

        wrapper = dec._decorate(wrapped)

        # test wrapper call:
        res = wrapper(context, request)

        # assertions:
        dec._validate.assert_called_once_with(wrapped.return_value)
        wrapped.assert_called_once_with(
            context,
            request
            )
        self.assertEqual(res, {
            "content": [dec._validate.return_value],
            "method": "payments_get_items"
            })


class TestFacebookPaymentsCallback(unittest.TestCase):

    @mock.patch('pyramid_facebook.credits.DisputedOrder')
    def test_facebook_payments_status_update_disputed(self, m_order):
        from pyramid_facebook.credits import facebook_payments_status_update_disputed
        ctx = mock.Mock()
        req = mock.Mock()

        res = facebook_payments_status_update_disputed(ctx, req)

        req.registry.notify.assert_called_once_with(m_order.return_value)
        self.assertIsInstance(res, HTTPOk)

        # test exception
        req.reset_mock()
        req.registry.notify.side_effect = Exception('boom!')

        res = facebook_payments_status_update_disputed(ctx, req)

        req.registry.notify.assert_called_once_with(m_order.return_value)
        self.assertIsInstance(res, HTTPOk)

    @mock.patch('pyramid_facebook.credits.RefundedOrder')
    def test_facebook_payments_status_update_refunded(self, m_order):
        from pyramid_facebook.credits import facebook_payments_status_update_refunded
        ctx = mock.Mock()
        req = mock.Mock()

        res = facebook_payments_status_update_refunded(ctx, req)

        req.registry.notify.assert_called_once_with(m_order.return_value)
        self.assertIsInstance(res, HTTPOk)

        # test exception
        req.reset_mock()
        req.registry.notify.side_effect = Exception('boom!')

        res = facebook_payments_status_update_refunded(ctx, req)

        req.registry.notify.assert_called_once_with(m_order.return_value)
        self.assertIsInstance(res, HTTPOk)


    @mock.patch('pyramid_facebook.credits.EarnedCurrencyOrder')
    def test_facebook_payments_status_update_placed_currency_app_order(self, m_order):
        from pyramid_facebook.credits import facebook_payments_status_update_placed
        ctx = mock.MagicMock()
        req = mock.Mock()

        res = facebook_payments_status_update_placed(ctx, req)

        req.registry.notify.assert_called_once_with(m_order.return_value)

        expected = {
            'content':{
                'status': 'settled',
                'order_id': ctx.order_details['order_id']
                },
            'method': 'payments_status_update',
            }
        self.assertDictEqual(expected, res)

    @mock.patch('pyramid_facebook.credits.PlacedItemOrder')
    def test_facebook_payments_status_update_placed_item_order(self, m_order):
        from pyramid_facebook.credits import facebook_payments_status_update_placed
        ctx = mock.MagicMock()
        ctx.earned_currency_data = None
        req = mock.Mock()

        facebook_payments_status_update_placed(ctx, req)

        req.registry.notify.assert_called_once_with(m_order.return_value)

    @mock.patch('pyramid_facebook.credits.EarnedCurrencyOrder')
    def test_facebook_payments_status_update_exception(self, m_order):
        from pyramid_facebook.credits import facebook_payments_status_update_placed
        ctx = mock.MagicMock()
        req = mock.Mock()
        req.registry.notify.side_effect = Exception('boooom!')

        res = facebook_payments_status_update_placed(ctx, req)

        req.registry.notify.assert_called_once_with(m_order.return_value)

        expected = {
            'content':{
                'status': 'canceled',
                'order_id': ctx.order_details['order_id']
                },
            'method': 'payments_status_update',
            }
        self.assertDictEqual(expected, res)
