# Part of Flectra. See LICENSE file for full copyright and licensing
# details.

from flectra.tests.common import TransactionCase


class TestSaleOrder(TransactionCase):

    def setUp(self):
        super(TestSaleOrder, self).setUp()
        self.so_model = self.env['sale.order']
        self.so_line_model = self.env['sale.order.line']
        self.stock_picking_model = self.env['stock.picking']
        self.stock_move_model = self.env['stock.move']
        self.stock_location_model = self.env['stock.location']
        self.sale_wizard = self.env['sale.transfer.products']
        self.invoice_wizard = self.env['sale.advance.payment.inv']
        self.sale1 = self.env.ref('blanket_so_po.sale_order_blanket1')
        self.so_line_with_blanket = self.env.ref(
            'blanket_so_po.sale_order_line_blanket_1')
        self.so_line_without_blanket = self.env.ref(
            'blanket_so_po.sale_order_line_blanket_2')
        self.so_line_without_blanket2 = self.env.ref(
            'blanket_so_po.sale_order_line_blanket_3')
        self.inv_obj = self.env['account.invoice']

    def test_1_sale_with_blanket(self):
        self.sale1.force_quotation_send()
        self.sale1.action_confirm()
        self.assertTrue(self.sale1.state, 'sale')
        self.assertTrue(self.sale1.invoice_status, 'to invoice')
        uom_qty = self.so_line_with_blanket.product_uom_qty
        transfer_qty = 2
        remaining_qty = uom_qty - transfer_qty
        transfer_wizard = self.sale_wizard.create(
            {'ref_id': self.so_line_with_blanket.id,
             'transfer_qty': transfer_qty})
        transfer_wizard.split_qty_wt_newline()
        self.assertEqual(remaining_qty, uom_qty - transfer_qty,
                         'Remaining to transfer qty is different')
        transfer_qty += 5
        remaining_qty = uom_qty - transfer_qty
        transfer_wizard = self.sale_wizard.create(
            {'ref_id': self.so_line_with_blanket.id, 'transfer_qty': 5})
        transfer_wizard.split_qty_wt_newline()
        self.assertEqual(remaining_qty, uom_qty - transfer_qty,
                         'Remaining to transfer qty is different')
        self.assertEqual(self.sale1.picking_ids.move_lines[-1].quantity_done,
                         0.0)
        self.assertEqual(self.sale1.picking_ids.move_lines[-2].quantity_done,
                         0.0)
        self.sale1.picking_ids.move_lines[-1].quantity_done = 2
        self.sale1.picking_ids.action_confirm()
        self.sale1.picking_ids.action_assign()
        res_dict = self.sale1.picking_ids.button_validate()
        backorder_wizard = self.env[(res_dict.get('res_model'))].browse(
            res_dict.get('res_id'))
        backorder_wizard.process()
        self.assertEqual(len(self.sale1.picking_ids), 2,
                         'There is no 2 pickings are available')
        context = {"active_model": 'sale.order',
                   "active_ids": [self.sale1.id],
                   "active_id": self.sale1.id}
