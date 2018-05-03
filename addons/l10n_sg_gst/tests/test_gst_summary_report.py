# Part of Flectra. See LICENSE file for full copyright and licensing
# details.

import time

from flectra.tests.common import TransactionCase


class TestGstF5(TransactionCase):
    def setUp(self):
        super(TestGstF5, self).setUp()
        self.res_partner_model = self.env['res.partner']
        self.product_model = self.env['product.product']
        self.account_tax = self.env['account.tax']
        self.account_invoice_model = self.env['account.invoice']
        self.account_invoice_line_model = self.env['account.invoice.line']
        self.currency_id = self.env.ref('base.SGD')
        self.product1 = self.env.ref('product.product_product_3')
        self.product2 = self.env.ref('product.product_product_4')
        self.product3 = self.env.ref('product.product_product_5b')
        self.product4 = self.env.ref('product.product_product_5')
        self.product5 = self.env.ref('product.product_product_6')
        self.product6 = self.env.ref('product.product_product_7')
        self.product7 = self.env.ref('product.product_product_8')
        self.product8 = self.env.ref('product.product_product_9')
        self.product9 = self.env.ref('product.product_product_10')
        self.standard_rates = self.env.ref('l10n_sg.tax_group_7').id
        self.zeroed = self.env.ref('l10n_sg.tax_group_0').id
        self.mes = self.env.ref('l10n_sg.tax_group_mes').id
        self.oos = self.env.ref('l10n_sg.tax_group_oos').id
        self.exempted = self.env.ref('l10n_sg.tax_group_exempted').id


        self.gst_customer_id_1 = self.res_partner_model.create(dict(
            name="Cyril",
            email="cyril_daufeldt@aufeldt.com",
        ))

        self.gst_supplier_id_1 = self.res_partner_model.create(dict(
            name="Ritz",
            email="ritz_daufeldt@yahoo.com",
            supplier=True
        ))

        self.sale_tax_id_1 = self.account_tax.search(
            [('name', '=', 'Sales Tax 7% SR')])
        self.sale_tax_id_1.write({'tax_group_id': self.standard_rates})

        self.sale_tax_id_2 = self.account_tax.search(
            [('name', '=', 'Sales Tax 0% ZR')])
        self.sale_tax_id_2.write({'tax_group_id': self.zeroed})

        self.sale_tax_id_3 = self.account_tax.search(
            [('name', '=', 'Sales Tax 0% OS')])
        self.sale_tax_id_3.write({'tax_group_id': self.oos})

        self.sale_tax_id_4 = self.account_tax.search(
            [('name', '=', 'Sales Tax 0% ESN33')])
        self.sale_tax_id_4.write({'tax_group_id': self.exempted})

        self.sale_tax_id_5 = self.account_tax.search(
            [('name', '=', 'Sales Tax 7% DS')])
        self.sale_tax_id_5.write({'tax_group_id': self.standard_rates})

        self.sale_tax_id_6 = self.account_tax.search(
            [('name', '=', 'Sales Tax 0% ES33')])
        self.sale_tax_id_6.write({'tax_group_id': self.exempted})

        self.purchase_tax_id_1 = self.account_tax.search(
            [('name', '=', 'Purchase Tax 7% TX-N33')])
        self.purchase_tax_id_1.write({'tax_group_id': self.standard_rates})

        self.purchase_tax_id_2 = self.account_tax.search(
            [('name', '=', 'Purchase Tax 7% BL')])
        self.purchase_tax_id_2.write({'tax_group_id': self.standard_rates})

        self.purchase_tax_id_3 = self.account_tax.search(
            [('name', '=', 'Purchase Tax 7% IM')])
        self.purchase_tax_id_3.write({'tax_group_id': self.standard_rates})

        self.purchase_tax_id_4 = self.account_tax.search(
            [('name', '=', 'Purchase Tax 7% TX-RE')])
        self.purchase_tax_id_4.write({'tax_group_id': self.standard_rates})

        self.purchase_tax_id_5 = self.account_tax.search(
            [('name', '=', 'Purchase Tax 0% ME')])
        self.purchase_tax_id_5.write({'tax_group_id': self.standard_rates})

        self.purchase_tax_id_6 = self.account_tax.search(
            [('name', '=', 'Purchase Tax 0% NR')])
        self.purchase_tax_id_6.write({'tax_group_id': self.standard_rates})

        self.purchase_tax_id_7 = self.account_tax.search(
            [('name', '=', 'Purchase Tax 0% ZP')])
        self.purchase_tax_id_7.write({'tax_group_id': self.standard_rates})

        self.purchase_tax_id_8 = self.account_tax.search(
            [('name', '=', 'Purchase Tax 0% OP')])
        self.purchase_tax_id_8.write({'tax_group_id': self.standard_rates})

        self.purchase_tax_id_9 = self.account_tax.search(
            [('name', '=', 'Purchase Tax 0% EP')])
        self.purchase_tax_id_9.write({'tax_group_id': self.exempted})

        self.purchase_tax_id_10 = self.account_tax.search(
            [('name', '=', 'Purchase Tax MES')])
        self.purchase_tax_id_10.write({'tax_group_id': self.mes})

        self.purchase_tax_id_11 = self.account_tax.search(
            [('name', '=', 'Purchase Tax 7% TX7')])
        self.purchase_tax_id_11.write({'tax_group_id': self.standard_rates})

    def test_create_customer_invoice(self):
        customer_invoice = self.account_invoice_model.create(
            {'partner_id': self.gst_customer_id_1.id,
             'reference_type': 'none',
             'currency_id': self.currency_id.id,
             'type': 'out_invoice',
             'date_invoice': time.strftime('%Y') + '-07-01',
             })
        account_id = self.env['account.account'].search(
            [('code', '=', '300004')])
        self.env['account.invoice.line'].create({
            'product_id': self.product1.id,
            'quantity': 1,
            'invoice_id': customer_invoice.id,
            'name': 'something',
            'price_unit': 2000,
            'account_id': account_id.id,
            'invoice_line_tax_ids': [(6, 0, [self.sale_tax_id_1.id])]
        })
        self.env['account.invoice.line'].create({
            'product_id': self.product2.id,
            'quantity': 2,
            'invoice_id': customer_invoice.id,
            'name': 'something',
            'price_unit': 2000,
            'account_id': account_id.id,
            'invoice_line_tax_ids': [(6, 0, [self.sale_tax_id_2.id])]
        })
        self.env['account.invoice.line'].create({
            'product_id': self.product3.id,
            'quantity': 2,
            'invoice_id': customer_invoice.id,
            'name': 'something',
            'price_unit': 3000,
            'account_id': account_id.id,
            'invoice_line_tax_ids': [(6, 0, [self.sale_tax_id_3.id])]
        })

        customer_invoice._onchange_invoice_line_ids()

        # I check that Initially customer invoice is in the "Draft" state
        self.assertEquals(customer_invoice.state, 'draft')

        # I check that there is no move attached to the invoice
        self.assertEquals(len(customer_invoice.move_id), 0)

        # I validate invoice by creating on
        customer_invoice.action_invoice_open()

        # I check that the invoice state is "Open"
        self.assertEquals(customer_invoice.state, 'open')

        # I check that now there is a move attached to the invoice
        assert customer_invoice.move_id, "Move not created " \
                                         "for open invoice"

    def test_create_supplier_invoice(self):
        supplier_invoice = self.account_invoice_model.create(
            {'partner_id': self.gst_supplier_id_1.id,
             'reference_type': 'none',
             'currency_id': self.currency_id.id,
             'type': 'in_invoice',
             'date_invoice': time.strftime('%Y') + '-07-01',
             'state': 'draft'
             })
        default_fields = supplier_invoice.fields_view_get(
            view_id=None,
            view_type='form',
            toolbar=False, submenu=False)
        invoice_dic = self.env['account.account'].default_get(
            default_fields)
        journal_id = \
            self.env['account.journal'].search(
                [('type', '=', 'purchase')])[0]
        account_id = self.env['account.account'].search(
            [('code', '=', '202001')])
        invoice_dic.update({'journal_id': journal_id.id,
                            'account_id': account_id.id,
                            'type': 'in_invoice'})
        supplier_invoice.update(invoice_dic)
        default_fields = self.account_invoice_line_model.fields_view_get(
            view_id=None,
            view_type='tree',
            toolbar=False, submenu=False)
        invoice_line_dic = self.account_invoice_line_model.default_get(
            default_fields)
        account_id = self.env['account.account'].search(
            [('code', '=', '401005')])
        invoice_line_dic.update(
            {'invoice_line_tax_ids': [(6, 0, [self.purchase_tax_id_1.id])],
             'product_id': self.product4.id,
             'name': 'Multi Block',
             'price_unit': 4090.0,
             'quantity': 50.0,
             'invoice_id': supplier_invoice.id,
             'account_id': account_id.id or False})
        self.account_invoice_line_model.create(invoice_line_dic)
        invoice_line_dic.update(
            {'invoice_line_tax_ids': [(6, 0, [self.purchase_tax_id_2.id])],
             'product_id': self.product5.id,
             'name': 'SuperMax',
             'price_unit': 2190.0,
             'quantity': 210.0,
             'invoice_id': supplier_invoice.id,
             'account_id': account_id.id or False})
        self.account_invoice_line_model.create(invoice_line_dic)
        invoice_line_dic.update(
            {'invoice_line_tax_ids': [(6, 0, [self.purchase_tax_id_3.id])],
             'product_id': self.product6.id,
             'name': 'Digital Wireless System',
             'price_unit': 2000.0,
             'quantity': 32.0,
             'invoice_id': supplier_invoice.id,
             'account_id': account_id.id or False})
        self.account_invoice_line_model.create(invoice_line_dic)
        invoice_line_dic.update(
            {'invoice_line_tax_ids': [(6, 0, [self.purchase_tax_id_4.id])],
             'product_id': self.product7.id,
             'name': 'Digital Mobile X-Ray System',
             'price_unit': 3002.0,
             'quantity': 45.0,
             'invoice_id': supplier_invoice.id,
             'account_id': account_id.id or False})
        self.account_invoice_line_model.create(invoice_line_dic)
        invoice_line_dic.update(
            {'invoice_line_tax_ids': [(6, 0, [self.purchase_tax_id_5.id])],
             'product_id': self.product8.id,
             'name': 'Electrical Medical Stimulator',
             'price_unit': 5037.0,
             'quantity': 12.0,
             'invoice_id': supplier_invoice.id,
             'account_id': account_id.id or False})
        self.account_invoice_line_model.create(invoice_line_dic)
        invoice_line_dic.update(
            {'invoice_line_tax_ids': [(6, 0, [self.purchase_tax_id_6.id])],
             'product_id': self.product9.id,
             'name': 'Hommage-Marble Stone',
             'price_unit': 2300.0,
             'quantity': 25.0,
             'invoice_id': supplier_invoice.id,
             'account_id': account_id.id or False})
        self.account_invoice_line_model.create(invoice_line_dic)

        supplier_invoice._onchange_invoice_line_ids()

        # I check that Initially customer invoice is in the "Draft" state
        self.assertEquals(supplier_invoice.state, 'draft')

        # I check that there is no move attached to the invoice
        self.assertEquals(len(supplier_invoice.move_id), 0)

        # I validate invoice by creating on
        supplier_invoice.action_invoice_open()

        # I check that the invoice state is "Open"
        self.assertEquals(supplier_invoice.state, 'open')
