# Part of Flectra. See LICENSE file for full copyright and licensing
# details.

import logging

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
        logging.info('Test Cases for Blanket Sale order')
        logging.info('Sale Order - %s' % (self.sale1.name))
        logging.info(
            '============================================================'
            '===================+=====')
        logging.info(
            ' | Blanket So Line | Product  |  Ordered Qty  | Remaining '
            'to transfer  |  Delivered |')
        for line in self.sale1.order_line:
            logging.info(
                ' %s            | %s       | %d            | %d          '
                '           | %d ' % (
                    line.blanket_so_line, line.product_id.name,
                    line.product_uom_qty, line.remaining_to_so_transfer,
                    line.qty_delivered))
            logging.info(
                '========================================================'
                '=========================')
        uom_qty = self.so_line_with_blanket.product_uom_qty
        transfer_qty = 2
        remaining_qty = 0.0

        logging.info(
            '*****************************************************')
        logging.info(
            '========================================================='
            '======================+=====')
        logging.info(
            ' |  Product  | Initial Demand  | Reserved  |  Done |')
        for picking in self.sale1.picking_ids:
            for line in picking.move_lines:
                logging.info('| %s     | %d              |%d         | %d' % (
                    line.product_id.name, line.product_uom_qty,
                    line.reserved_availability, line.quantity_done))
                logging.info(
                    '======================================================='
                    '==========================')

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

        logging.info(
            '*****************************************************')
        logging.info(
            'Sale Order after Blanket Split lines- %s' % (self.sale1.name))
        logging.info(
            '========================================================='
            '======================+=====')
        logging.info(
            ' | Blanket So Line | Product  |  Ordered Qty  | Remaining '
            'to transfer  |  Delivered |')
        for line in self.sale1.order_line:
            logging.info(
                ' %s            | %s       | %d            | %d          '
                '           | %d ' % (
                    line.blanket_so_line, line.product_id.name,
                    line.product_uom_qty, line.remaining_to_so_transfer,
                    line.qty_delivered))
            logging.info(
                '======================================================='
                '==========================')

        self.assertEqual(self.sale1.picking_ids.move_lines[-1].quantity_done,
                         0.0)
        self.assertEqual(self.sale1.picking_ids.move_lines[-2].quantity_done,
                         0.0)
        self.sale1.picking_ids.move_lines[-1].quantity_done = 2

        logging.info(
            '*****************************************************')
        logging.info('Delivery Order - %s' % (self.sale1.picking_ids.name))
        logging.info(
            '==========================================================='
            '====================+=====')
        logging.info(
            ' |  Product  | Initial Demand  | Reserved  |  Done |')
        for move in self.sale1.picking_ids.move_lines:
            logging.info('| %s     | %d              |%d         | %d' % (
                move.product_id.name, move.product_uom_qty,
                move.reserved_availability, move.quantity_done))
            logging.info(
                '======================================================='
                '==========================')

        self.sale1.picking_ids.action_confirm()
        self.sale1.picking_ids.action_assign()
        res_dict = self.sale1.picking_ids.button_validate()
        backorder_wizard = self.env[(res_dict.get('res_model'))].browse(
            res_dict.get('res_id'))
        backorder_wizard.process()

        logging.info(
            '*****************************************************')
        logging.info(
            'Sale Order after validate Delivery order- %s' % (
                self.sale1.name))
        logging.info(
            '=========================================================='
            '=====================+=====')
        logging.info(
            ' | Blanket So Line | Product  |  Ordered Qty  | Remaining '
            'to transfer  |  Delivered |invoice status')
        for line in self.sale1.order_line:
            logging.info(
                ' %s            | %s       | %d            | %d          '
                '           | %d         |%s' % (
                    line.blanket_so_line, line.product_id.name,
                    line.product_uom_qty, line.remaining_to_so_transfer,
                    line.qty_delivered, line.invoice_status))
            logging.info(
                '======================================================='
                '==========================')

        self.assertEqual(len(self.sale1.picking_ids), 2,
                         'There is no 2 pickings are available')

        context = {"active_model": 'sale.order',
                   "active_ids": [self.sale1.id],
                   "active_id": self.sale1.id}

        for invoice in self.sale1.invoice_ids:
            logging.info('Invoice of Delivered Quantity.')
            for line in invoice.invoice_line_ids:
                logging.info(
                    '==================================================')
                logging.info(
                    '| Product | Quantity | Unit Price | Subtotal |')
                logging.info(
                    '=================================================|')
                logging.info(
                    '|%s       |%d        |%d          |%d        |   ' % (
                        line.product_id.name, line.quantity,
                        line.price_unit,
                        line.price_subtotal))
            invoice.with_context(context).invoice_validate()
