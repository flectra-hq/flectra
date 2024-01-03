# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra.fields import Command

from flectra.addons.payment.tests.common import PaymentCommon


class AuthorizeCommon(PaymentCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.authorize = cls._prepare_provider('authorize', update_values={
            'authorize_login': 'dummy',
            'authorize_transaction_key': 'dummy',
            'authorize_signature_key': '00000000',
            'available_currency_ids': [Command.set(cls.currency_usd.ids)]
        })

        cls.provider = cls.authorize
        cls.currency = cls.currency_usd
