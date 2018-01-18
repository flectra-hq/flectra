# -*- coding: utf-8 -*-
from flectra.addons.stock.tests import common


class TestStockBranch(common.TestStockCommon):

    def setUp(self):
        super(TestStockBranch, self).setUp()

        self.branch_1 = self.env.ref('base_branch_company.data_branch_1')
        self.branch_2 = self.env.ref('base_branch_company.data_branch_2')
        self.main_company = self.env.ref('base.main_company')
        self.stock_manager_group = self.env.ref('stock.group_stock_manager')
        warehouse_wt = self.env.ref('stock.stock_warehouse_WW')

        self.destination_loc_id = warehouse_wt.lot_stock_id.id
        self.picking_type_id = warehouse_wt.in_type_id

        self.user_1 = self.create_stock_user(
            self.main_company, 'Test Stock User 1', self.branch_1,
            [self.branch_1, self.branch_2])
        self.user_2 = self.create_stock_user(
            self.main_company, 'Test Stock User 2', self.branch_2,
            [self.branch_2])
        self.picking_1 = self.pickings_create(
            self.picking_type_id, self.branch_2, self.user_1,
            self.supplier_location, self.stock_location)
        self.picking_2 = self.pickings_create(
            self.picking_type_id, self.branch_2, self.user_2,
            self.supplier_location, self.destination_loc_id)
        self.internal_picking = self.pickings_create(
            self.picking_type_id, self.branch_2, self.user_1,
            self.stock_location, self.destination_loc_id)

    def pickings_create(self, picking_type_id, branch_id, user_id,
                        source_loc_id, destination_loc_id):
        picking_id = self.PickingObj.sudo(user_id).create(
            {
                'location_id': source_loc_id,
                'picking_type_id': picking_type_id.id,
                'branch_id': branch_id.id,
                'location_dest_id': destination_loc_id,
            }
        )
        self.MoveObj.sudo(user_id).create(
            {
                'picking_id': picking_id.id,
                'product_uom_qty': 6.0,
                'name': 'Test Move of Picking',
                'location_id': source_loc_id,
                'location_dest_id': destination_loc_id,
                'product_id': self.productC.id,
                'product_uom': self.productC.uom_id.id,
            }
        )
        return picking_id

    def create_stock_user(self, company_id, login_name, branch_id, branch_ids):
        user_obj = \
            self.env['res.users'].with_context(
                {'no_reset_password': True}).create(
                {
                    'company_id': company_id.id,
                    'default_branch_id': branch_id.id,
                    'branch_ids': [(4, branch.id) for branch in branch_ids],
                    'company_ids': [(4, company_id.id)],
                    'login': login_name,
                    'groups_id': [(6, 0, [self.stock_manager_group.id])],
                    'name': 'Stock User ' + login_name,
                    'email': 'demo@yourcompany.com',
                    'password': '123'
                }
            )
        return user_obj.id

    def test_stock_picking_branch(self):
        picking_ids = self.PickingObj.sudo(self.user_1).search([('id', '=', self.picking_1.id)]).ids
        self.assertNotEqual(picking_ids, [], '')

        picking_ids = self.PickingObj.sudo(self.user_2).search([('id', '=', self.picking_2.id)]).ids
        self.assertNotEqual(picking_ids, [])

        picking_ids = self.PickingObj.sudo(self.user_1).search([('id', '=', self.internal_picking.id)]).ids
        self.assertNotEqual(picking_ids, [])
