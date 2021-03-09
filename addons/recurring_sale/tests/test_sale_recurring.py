# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra.tests.common import TransactionCase


class RecurringTransactionCase(TransactionCase):

    def setUp(self):
        super(RecurringTransactionCase, self).setUp()
        self.sale_order = self.env.ref("sale.sale_order_2")

    def create_sale_recurring(self):
        recurring_id = self.env['recurring'].create({
            'name': 'SO0002',
            'exec_init': 5,
        })
        recurring_id.btn_recurring()

    def test_01_recurring(self):
        self.create_sale_recurring()
