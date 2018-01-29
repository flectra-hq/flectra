# Part of Flectra See LICENSE file for full copyright and licensing details.

import logging
from datetime import datetime
from flectra.exceptions import Warning
from flectra.tests.common import TransactionCase
from flectra.tools.misc import formatLang
from flectra import _


class TestPurchaseIndent(TransactionCase):

    def setUp(self):
        super(TestPurchaseIndent, self).setUp()
        self.PurchaseIndent = self.env['purchase.indent']
        self.PurchaseIndentLine = self.env['purchase.indent.line']
        self.Requisition_Req = self.env['wiz.requisition.request']
        self.company_id = self.env.ref('base.main_company')
        self.branch_id = self.env.ref('base_branch_company.data_branch_2')
        self.partner_id = self.env.ref('base.res_partner_address_12')
        self.category_id = self.env.ref('product.product_category_5')
        self.product_id_1 = self.env.ref('product.product_product_24')
        self.product_id_2 = self.env.ref('product.product_product_16')
        self.product_id_3 = self.env.ref('product.consu_delivery_03')
        self.agreement_type_id = \
            self.env.ref('purchase_requisition.type_multi')

        purchase_indent_vals = {
            'company_id': self.company_id.id,
            'category_id': self.category_id.id,
            'request_date': datetime.today(),
            'user_id': self.env.user.id,
            'branch_id': self.branch_id.id
            }

        self.purchase_indent_id = \
            self.PurchaseIndent.create(purchase_indent_vals)
        self.purchase_indent_id_1 = self.purchase_indent_id.copy()

    def test_00_purchase_indent_flow(self):
        self.purchase_indent_id.write({
            'indent_line': [
                (0, 0, {
                    'name': self.product_id_1.name,
                    'product_id': self.product_id_1.id,
                    'product_qty': 5.0,
                    'product_uom': self.product_id_1.uom_po_id.id,
                }),
                (0, 0, {
                    'name': self.product_id_2.name,
                    'product_id': self.product_id_2.id,
                    'product_qty': 15.0,
                    'product_uom': self.product_id_2.uom_po_id.id,
                })],
            })

        self.purchase_indent_id_1.write({
            'indent_line': [
                (0, 0, {
                    'name': self.product_id_3.name,
                    'product_id': self.product_id_3.id,
                    'product_qty': 20.0,
                    'product_uom': self.product_id_3.uom_po_id.id,
                }),
                (0, 0, {
                    'name': self.product_id_1.name,
                    'product_id': self.product_id_1.id,
                    'product_qty': 25.0,
                    'product_uom': self.product_id_1.uom_po_id.id,
                }),
                (0, 0, {
                    'name': self.product_id_2.name,
                    'product_id': self.product_id_2.id,
                    'product_qty': 5.0,
                    'product_uom': self.product_id_2.uom_po_id.id,
                })],
            })

        self.assertTrue(
            self.purchase_indent_id,
            'Purchase Indent: no purchase indent created')
        self.assertTrue(
            self.purchase_indent_id_1,
            'Purchase Indent: no purchase indent created')

        for line in self.purchase_indent_id.indent_line:
            if line.product_qty < 0:
                raise Warning(_("Quantity (%s) can not be Negative!") % (
                    formatLang(self.env, line.product_qty, digits=2)))

        for line in self.purchase_indent_id_1.indent_line:
            if line.product_qty < 0:
                raise Warning(_("Quantity (%s) can not be Negative!") % (
                    formatLang(self.env, line.product_qty, digits=2)))

        self.purchase_indent_id.action_confirm()
        self.purchase_indent_id_1.action_confirm()

        requisition_id = self.Requisition_Req.create({
            'category_id': self.category_id.id,
            'order_type': 'po',
            'purchase_indent_id': self.purchase_indent_id.id,
            })
        requisition_id.onchange_purchase_indent_id()
        requisition_id.dummy_wiz_indent_line[0].write({'requisition_qty': 5})
        requisition_id.dummy_wiz_indent_line[2].write({'requisition_qty': 20})
        requisition_id.act_next()
        requisition_id.write({'partner_id': self.partner_id.id})
        for line in requisition_id.wiz_indent_line:
            line.write({'price_unit': 100})
        requisition_id.action_create()
        logging.info('Successful: Purchase Order Created!')

        # Cancel Purchase Order
        self.purchase_indent_id.indent_history_ids[0].order_id.button_cancel()

        requisition_id_1 = self.Requisition_Req.create({
            'category_id': self.category_id.id,
            'order_type': 'pa',
            'purchase_indent_id': self.purchase_indent_id_1.id,
            'requisition_type_id': self.agreement_type_id.id,
            })

        requisition_id_1.onchange_purchase_indent_id()
        requisition_id_1.dummy_wiz_indent_line[1].write({'requisition_qty': 4})
        requisition_id_1.dummy_wiz_indent_line[2].write({'requisition_qty': 5})
        requisition_id_1.act_next()
        for line in requisition_id_1.wiz_indent_line:
            line.write({'price_unit': 100})
        requisition_id_1.action_create()
        logging.info('Successful: Purchase Agreement Created!')
