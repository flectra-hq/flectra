# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra.tests.common import TransactionCase
from datetime import datetime
from dateutil.relativedelta import relativedelta


class TestSaleOrder(TransactionCase):
    def setUp(self):
        super(TestSaleOrder, self).setUp()

        self.demo_product1_id = self.env.ref('rma.demo_product_1')
        self.demo_product2_id = self.env.ref('rma.demo_product_2')

        self.product1_lot_id = self.env['stock.production.lot'].create({
            'name': 'L001',
            'product_id': self.demo_product1_id.id,
            'warranty_date': datetime.now() + relativedelta(years=1)
        })
        self.change_prod1_qty_id = self.env[
            'stock.change.product.qty'].create({
                'product_id': self.demo_product1_id.id,
                'new_quantity': 10,
                'lot_id': self.product1_lot_id.id
            })
        self.change_prod1_qty_id.change_product_qty()
        self.sale_order_id_1 = self.env.ref(
            'rma.demo_sale_order_rma_request1')

        self.product2_lot_id = self.env['stock.production.lot'].create({
            'name': 'L002',
            'product_id': self.demo_product2_id.id,
            'warranty_date': datetime.now() - relativedelta(years=1)
        })
        self.change_prod2_qty_id = self.env[
            'stock.change.product.qty'].create({
                'product_id': self.demo_product2_id.id,
                'new_quantity': 10,
                'lot_id': self.product2_lot_id.id
            })
        self.change_prod2_qty_id.change_product_qty()
        self.sale_order_id_2 = self.env.ref(
            'rma.demo_sale_order_rma_request2')

    def test_00_rma_request(self):
        self.sale_order_id_1.action_confirm()
        picking_ids = self.sale_order_id_1.picking_ids[0]
        for move_line in picking_ids.move_lines[0].move_line_ids:
            move_line.lot_id = self.product1_lot_id.id
            move_line.qty_done = 5
        picking_ids.button_validate()
        picking_ids.action_done()

        self.rma_id_1 = self.env['rma.request'].create({
            'sale_order_id': self.sale_order_id_1.id,
            'picking_id': picking_ids[0].id,
            'date': datetime.now() - relativedelta(days=15),
            'partner_id': self.sale_order_id_1.partner_id.id,
            'type': 'return_replace'
        })
        self.assertEquals(self.rma_id_1.state, 'draft')

        self.rma_id_1._get_rma_lines()
        self.assertTrue((len(self.rma_id_1.rma_line.ids)) != 0,
                        'You can not create RMA request!')

        self.rma_id_1._get_warranty_lines()
        self.assertEquals((len(self.rma_id_1.warranty_expire_line.ids)), 0,
                          'This RMA request should not have expiry '
                          'product!')

        for rma_line in self.rma_id_1.rma_line:
            can_be_return_qty = sum(line.qty_done for line in
                                    rma_line.move_line_id.move_line_ids if
                                    line.lot_id.warranty_date and
                                    line.lot_id.warranty_date >=
                                    self.rma_id_1.date)
            self.assertTrue(rma_line.qty_return <= can_be_return_qty,
                            "You can only return %d quantity for %s" %
                            (can_be_return_qty, rma_line.product_id.name))

        self.rma_id_1.action_confirm_request()
        self.assertEquals(self.rma_id_1.state, 'confirmed')

        context = {"active_model": 'rma.request',
                   "active_ids": [self.rma_id_1.id], "active_id":
                       self.rma_id_1.id, "rma": True}
        self.return_picking_id_1 = self.env[
            'stock.return.picking'].with_context(context).create(dict(
                picking_id=self.rma_id_1.picking_id.id,
            ))
        self.return_picking_id_1.create_returns()
        self.assertEquals(self.rma_id_1.state, 'rma_created')
        self.assertTrue(len(self.sale_order_id_1.picking_ids.ids) > 1,
                        'Product has not been returned yet')

        incoming_shipment = False
        for pick in self.sale_order_id_1.picking_ids:
            if pick.picking_type_code == 'incoming':
                incoming_shipment = True
                for move_line in pick.move_lines[0].move_line_ids:
                    move_line.lot_id = self.product1_lot_id.id
                    move_line.qty_done = 5
                pick.button_validate()
                pick.action_done()
        self.assertTrue(incoming_shipment, 'Incoming shipment is not created')
        self.assertEqual(len(self.sale_order_id_1.picking_ids.filtered(
            lambda pick: pick.picking_type_code == 'outgoing')), 1,
            "Replacement request can not be created!")

    def test_01_rma_request(self):
        self.sale_order_id_2.action_confirm()
        picking_ids = self.sale_order_id_2.picking_ids[0]
        for move_line in picking_ids.move_lines[0].move_line_ids:
            move_line.lot_id = self.product2_lot_id.id
            move_line.qty_done = 10
        for move_line in picking_ids.move_lines[1].move_line_ids:
            move_line.lot_id = self.product1_lot_id.id
            move_line.qty_done = 5
        picking_ids.button_validate()
        picking_ids.action_done()

        self.rma_id_2 = self.env['rma.request'].create({
            'sale_order_id': self.sale_order_id_2.id,
            'picking_id': picking_ids[0].id,
            'date': datetime.now() - relativedelta(days=10),
            'partner_id': self.sale_order_id_2.partner_id.id,
            'type': 'return_replace',
            'is_replacement': True
        })
        self.assertEquals(self.rma_id_2.state, 'draft')
        self.rma_id_2._get_rma_lines()
        self.assertTrue((len(self.rma_id_2.rma_line.ids)) != 0,
                        'You can not create RMA request!')

        self.rma_id_2._get_warranty_lines()
        self.assertEquals((len(self.rma_id_2.warranty_expire_line.ids)), 1,
                          'RMA request must have expiry product!')

        for rma_line in self.rma_id_2.rma_line:
            can_be_return_qty = sum(line.qty_done for line in
                                    rma_line.move_line_id.move_line_ids if
                                    line.lot_id.warranty_date and
                                    line.lot_id.warranty_date >=
                                    self.rma_id_2.date)
            self.assertTrue(rma_line.qty_return <= can_be_return_qty,
                            "You can only return %d quantity for %s" %
                            (can_be_return_qty, rma_line.product_id.name))

        self.rma_id_2.state = 'confirmed'
        self.assertEquals(self.rma_id_2.state, 'confirmed')

        context = {"active_model": 'rma.request',
                   "active_ids": [self.rma_id_2.id], "active_id":
                       self.rma_id_2.id, "rma": True}
        self.return_picking_id_2 = self.env[
            'stock.return.picking'].with_context(context).create(dict(
                picking_id=self.rma_id_2.picking_id.id,
            ))
        picking = self.return_picking_id_2.create_returns()
        self.assertEquals(self.rma_id_2.state, 'rma_created')
        self.assertTrue(len(self.sale_order_id_2.picking_ids.ids) > 1,
                        'Product has not been returned yet')

        incoming_shipment = False
        for pick in self.sale_order_id_2.picking_ids:
            if pick.picking_type_code == 'incoming':
                incoming_shipment = True
                for move_line in pick.move_lines[0].move_line_ids:
                    move_line.lot_id = self.product1_lot_id.id
                    move_line.qty_done = 10
                self.assertEquals(len(pick.move_lines[0].move_line_ids.ids), 1,
                                  'Only one product can be returned')
                pick.button_validate()
                pick.action_done()
        self.assertTrue(incoming_shipment, 'Incoming shipment is not created')

        replace_context = {"active_model": 'stock.picking',
                           "active_ids": [picking['res_id']], "active_id":
                               picking['res_id']}
        self.replace_picking_id_2 = self.env[
            'stock.return.picking'].with_context(replace_context).create(
            dict(picking_id=picking['res_id']))
        self.replace_picking_id_2.create_returns()
        self.assertEquals(self.rma_id_2.state, 'replacement_created')
