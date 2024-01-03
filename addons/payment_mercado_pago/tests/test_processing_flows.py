# Part of Flectra. See LICENSE file for full copyright and licensing details.

from unittest.mock import patch

from flectra.tests import tagged
from flectra.tools import mute_logger

from flectra.addons.payment.tests.http_common import PaymentHttpCommon
from flectra.addons.payment_mercado_pago.controllers.main import MercadoPagoController
from flectra.addons.payment_mercado_pago.tests.common import MercadoPagoCommon


@tagged('post_install', '-at_install')
class TestProcessingFlows(MercadoPagoCommon, PaymentHttpCommon):

    @mute_logger('flectra.addons.payment_mercado_pago.controllers.main')
    def test_redirect_notification_triggers_processing(self):
        """ Test that receiving a redirect notification triggers the processing of the notification
        data. """
        self._create_transaction(flow='redirect')
        url = self._build_url(MercadoPagoController._return_url)
        with patch(
            'flectra.addons.payment.models.payment_transaction.PaymentTransaction'
            '._handle_notification_data'
        ) as handle_notification_data_mock:
            self._make_http_get_request(url, params=self.redirect_notification_data)
        self.assertEqual(handle_notification_data_mock.call_count, 1)

    @mute_logger('flectra.addons.payment_mercado_pago.controllers.main')
    def test_webhook_notification_triggers_processing(self):
        """ Test that receiving a valid webhook notification triggers the processing of the
        notification data. """
        tx = self._create_transaction(flow='redirect')
        url = self._build_url(f'{MercadoPagoController._webhook_url}/{tx.reference}')
        with patch(
            'flectra.addons.payment.models.payment_transaction.PaymentTransaction'
            '._handle_notification_data'
        ) as handle_notification_data_mock:
            self._make_json_request(url, data=self.webhook_notification_data)
        self.assertEqual(handle_notification_data_mock.call_count, 1)
