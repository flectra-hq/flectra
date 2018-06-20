# Part of Flectra. See LICENSE file for full copyright and licensing
# details.

import logging

from flectra.exceptions import Warning
from flectra.tests.common import TransactionCase


class TestPurchaseOrder(TransactionCase):
    def setUp(self):
        super(TestPurchaseOrder, self).setUp()
        self.stock_move = self.env['stock.move']
        self.inv_obj = self.env['account.invoice']
        self.purchase_wizard = self.env['purchase.transfer.products']
        self.po1 = self.env.ref('blanket_so_po.blanket_purchase_order')
        self.po_line_with_blanket = self.env.ref(
            'blanket_so_po.blanket_purchase_order_line_1')
        self.po_line_without_blanket = self.env.ref(
            'blanket_so_po.blanket_purchase_order_line_2')
        self.po_line_without_blanket2 = self.env.ref(
            'blanket_so_po.blanket_purchase_order_line_3')

    def test_2_purchase_with_blanket(self):
        self.assertTrue(self.po1, 'Purchase: no purchase order created')
        self.po1.button_confirm()
        self.assertEqual(self.po1.state, 'purchase',
                         'Purchase: PO state should be "Purchase"')
        self.assertTrue(self.po1.picking_ids, "Picking should be created.")
        logging.info('Test Cases for Blanket Purchase order')
        logging.info('Purchase Order - %s' % (self.po1.name))
        logging.info(
            '============================================================='
            '==================+=====')
        logging.info(
            ' | Blanket Po Line | Product  |  Ordered Qty  | Remaining '
            'to transfer  |  Received Qty |')
        for line in self.po1.order_line:
            logging.info(
                ' %s            | %s       | %d            | %d          '
                '           | %d ' % (
                    line.blanket_po_line, line.product_id.name,
                    line.product_qty,
                    line.remaining_to_po_transfer, line.qty_received))
            logging.info(
                '========================================================='
                '========================')
        #
        blanket_lines_po = self.po1.order_line.search(
            [('order_id', '=', self.po1.id),
             ('blanket_po_line', '=', True)])
        uom_qty = self.po_line_with_blanket.product_qty
        transfer_qty = 2
        remaining_qty = 0.0

        len_blanket_lines = len(blanket_lines_po)
        total_po_line = len(self.po1.order_line)
        move_lines = len(self.po1.picking_ids.move_lines)
        logging.info(
            '*****************************************************')
        logging.info('Delivery Order for Purchase Order- %s' % (
            self.po1.picking_ids.name))
        logging.info(
            '============================================================'
            '===================+=====')
        logging.info(
            ' |  Product  | Initial Demand  | Reserved  |  Done |')
        for move in self.po1.picking_ids.move_lines:
            logging.info('| %s     | %d              |%d         | %d' % (
                move.product_id.name, move.product_uom_qty,
                move.reserved_availability, move.quantity_done))
            logging.info(
                '========================================================'
                '=========================')
        self.assertEqual(move_lines, total_po_line - len_blanket_lines,
                         'There is no equal number of move lines in move')

        self.assertTrue(self.po_line_with_blanket.blanket_po_line,
                        'Purchase: There is a Blanket po line')

        remaining_qty = uom_qty - transfer_qty
        transfer_wizard = self.purchase_wizard.create(
            {'ref_id': self.po_line_with_blanket.id,
             'transfer_qty': transfer_qty})
        transfer_wizard.split_qty_wt_newline_po()
        self.assertEqual(remaining_qty, uom_qty - transfer_qty,
                         'Remaining to transfer qty is different')

        total_po_line = len(self.po1.order_line)

        transfer_qty += 5
        remaining_qty = uom_qty - transfer_qty
        transfer_wizard = self.purchase_wizard.create(
            {'ref_id': self.po_line_with_blanket.id, 'transfer_qty': 5})
        transfer_wizard.split_qty_wt_newline_po()
        self.assertEqual(remaining_qty, uom_qty - transfer_qty,
                         'Remaining to transfer qty is different')

        logging.info(
            '*****************************************************')
        logging.info(
            'Purchase Order after Blanket Split lines- %s' % (
                self.po1.name))
        logging.info(
            '============================================================'
            '===================+=====')
        logging.info(
            ' | Blanket Po Line | Product  |  Ordered Qty  | Remaining '
            'to transfer  |  Received Qty |')
        for line in self.po1.order_line:
            logging.info(
                ' %s            | %s       | %d            | %d          '
                '           | %d ' % (
                    line.blanket_po_line, line.product_id.name,
                    line.product_qty,
                    line.remaining_to_po_transfer, line.qty_received))
            logging.info(
                '========================================================='
                '========================')

        with self.assertRaises(Warning):
            self.po1.button_cancel()

        self.picking = self.po1.picking_ids[0]
        self.assertEqual(self.picking.move_lines[-1].quantity_done, 0.0)
        self.assertEqual(self.picking.move_lines[-2].quantity_done, 0.0)
        self.picking.move_lines[-1].quantity_done = 2

        self.po1._compute_picking()
        self.po1._compute_is_shipped()

        logging.info(
            '*****************************************************')
        logging.info('Delivery Order - %s' % (self.picking.name))
        logging.info(
            '========================================================='
            '======================+=====')
        logging.info(
            ' id |  Product  | Initial Demand  | Reserved  |  Done |')
        for move in self.picking.move_lines:
            logging.info(
                '%d | %s     | %d              |%d         | %d' % (
                    move.id, move.product_id.name, move.product_uom_qty,
                    move.reserved_availability, move.quantity_done))
            logging.info(
                '========================================================='
                '========================')

        self.picking.force_assign()
        res_dict = self.picking.button_validate()
        backorder_wizard = self.env[(res_dict.get('res_model'))].browse(
            res_dict.get('res_id'))
        backorder_wizard.process()
        self.picking.action_done()

        logging.info(
            '*****************************************************')
        logging.info('Purchase Order after validate Delivery order- %s' % (
            self.po1.name))
        logging.info(
            '============================================================'
            '===================+=====')
        logging.info(
            ' | Blanket Po Line | Product  |  Ordered Qty  | Remaining '
            'to transfer  |  Received Qty |')
        for line in self.po1.order_line:
            logging.info(
                ' %s            | %s       | %d            | %d          '
                '           | %d        ' % (
                    line.blanket_po_line, line.product_id.name,
                    line.product_qty,
                    line.remaining_to_po_transfer, line.qty_received))
            logging.info(
                '========================================================='
                '========================')
