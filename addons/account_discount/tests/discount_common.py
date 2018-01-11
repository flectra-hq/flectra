# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra.tests.common import TransactionCase


class TestDiscountCommon(TransactionCase):
    def setUp(self):
        super(TestDiscountCommon, self).setUp()
        self.config = self.env['res.config.settings'].create({
            'global_discount_invoice_line': True,
            'global_discount_invoice_apply': True,
            'global_discount_fix_invoice_amount': 5000,
            'global_discount_percentage_invoice': 50,
        })
        self.config.onchange_global_discount_invoice_line()
        self.config.onchange_global_discount_invoice_apply()
        self.config.set_values()
        self.disc_config_1 = self.env['account.discount.config'].create({
            'group_id': self.env.ref('account.group_account_user').id,
            'fix_amount': 3000.0,
            'percentage': 20.0,
        })
