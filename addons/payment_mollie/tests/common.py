# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra.addons.payment.tests.common import PaymentCommon


class MollieCommon(PaymentCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.mollie = cls._prepare_provider('mollie', update_values={
            'mollie_api_key': 'dummy',
        })
        cls.provider = cls.mollie
        cls.currency = cls.currency_euro

        cls.notification_data = {
            'ref': cls.reference,
            'id': 'tr_ABCxyz0123',
        }
