# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra.tests.common import TransactionCase


class PurchaseRecurringTransactionCase(TransactionCase):

    def setUp(self):
        super(PurchaseRecurringTransactionCase, self).setUp()
        self.purchase_order = self.env.ref(
            "purchase.purchase_order_2")

    def create_purchase_recurring(self):
        recurring_id = self.env['recurring'].create({
            'name': 'PO00002',
            'exec_init': 5,
        })
        recurring_id.btn_recurring()

    def test_01_recurring(self):
        self.create_purchase_recurring()
