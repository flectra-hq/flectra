# Part of Flectra See LICENSE file for full copyright and licensing details.

import logging
from .test_gst_common import TestGSTCommon


class TestCreateInvoice(TestGSTCommon):
    def setUp(self):
        super(TestCreateInvoice, self).setUp()

    def details_of_invoice(self, invoice_id):
        logging.info('\n\n')
        logging.info('|=== Test case for %s type invoice ===|' %
                     invoice_id.gst_invoice)
        logging.info('Invoice No.   : %s' % invoice_id.number)
        logging.info('Invoice Type  : %s' % invoice_id.gst_invoice)
        logging.info('Customer Name : %s' % invoice_id.partner_id.name)
        logging.info('Invoice date  : %s' % invoice_id.date_invoice)
        logging.info('GST Type      : %s' % invoice_id.gst_type)
        logging.info('GST Number    : %s' % (invoice_id.vat or 'N/A'))
        logging.info('Journal       : %s' % invoice_id.journal_id.name)
        logging.info('Account       : %s' % invoice_id.account_id.name)
        logging.info('Source Doc.   : %s' % (invoice_id.origin or '-'))
        logging.info('Invoice lines :')
        for line in invoice_id.invoice_line_ids:
            logging.info('\t\t Product name : %s' % line.product_id.name)
            logging.info('\t\t Quantity     : %d' % line.quantity)
            logging.info('\t\t Price unit   : %d' % line.price_unit)
            logging.info('\t\t Total        : %d' % line.price_subtotal)
            logging.info('\t\t Taxes        : %s' %
                         (line.invoice_line_tax_ids.name or 'N/A'))

    def test_invoice_b2b(self):
        # Add tax for product
        for line in self.account_invoice_b2b.invoice_line_ids:
            line.write({
                'invoice_line_tax_ids': [(4, self.tax_gst_5.id)]
            })

        # Test for state initially
        self.assertEquals(self.account_invoice_b2b.state, 'draft')

        # Test for invoice type before validation
        assert not self.account_invoice_b2b.gst_invoice, \
            'Invoice type should be null'

        # Test state of invoice after validation
        self.account_invoice_b2b.action_invoice_open()
        self.assertEquals(self.account_invoice_b2b.state, 'open')

        # Test for move attachment
        assert self.account_invoice_b2b.move_id, \
            'Move is not created for open invoice'

        # Test for GST Invoice type
        if self.account_invoice_b2b.partner_id.vat:
            self.assertTrue(self.account_invoice_b2b.gst_invoice == 'b2b',
                            'Invoice must be a type B2B')

        # Test GST number of a partner
        if self.account_invoice_b2b.partner_id.gst_type != 'unregistered':
            assert self.account_invoice_b2b.vat,\
                'Registered partner must have GST Number'

        self.details_of_invoice(self.account_invoice_b2b)

        # Create refund invoice
        self.account_invoice_refund_b2b = self.account_invoice_b2b.refund()

        # Test case for invoice type
        assert self.account_invoice_refund_b2b.gst_invoice, \
            'Invoice type should be null'

        # Test for state initially
        self.assertEquals(self.account_invoice_refund_b2b.state, 'draft')

        # Test the state after invoice validation
        self.account_invoice_refund_b2b.action_invoice_open()
        self.assertEquals(self.account_invoice_refund_b2b.state, 'open')

        # Test whether refund invoice is created
        assert self.account_invoice_refund_b2b.refund_invoice_id, \
            'Refund invoice is not created'

        # Test for refund invoice created for B2B type invoice
        self.assertEquals(self.account_invoice_refund_b2b.refund_invoice_id.id,
                          self.account_invoice_b2b.id,
                          'Refund invoice for B2B type is not created')

        # Test refunded amount total
        self.assertEquals(
            -self.account_invoice_refund_b2b.amount_untaxed_signed,
            self.account_invoice_b2b.amount_untaxed_signed,
            'Amount total is wrong in refund')

        self.details_of_invoice(self.account_invoice_refund_b2b)
        self.env.ref('l10n_in_gst.l10n_in_gst_report_action')

    def test_invoice_b2cs(self):
        # Add tax for product
        for line in self.account_invoice_b2cs.invoice_line_ids:
            line.write({
                'invoice_line_tax_ids': [(4, self.tax_gst_18.id)]
            })

        # Test for invoice type before validation
        assert not self.account_invoice_b2cs.gst_invoice, \
            'Invoice type should be null'

        # Test the state of invoice before validation
        self.assertEquals(self.account_invoice_b2cs.state, 'draft')

        # Test state of invoice after validation
        self.account_invoice_b2cs.action_invoice_open()
        self.assertEquals(self.account_invoice_b2cs.state, 'open')

        # Test for move attachment
        assert self.account_invoice_b2cs.move_id, \
            'Move is not created for open invoice'
        partner_location = \
            self.account_invoice_b2cs.partner_id.partner_location

        # Test for GST Invoice type
        if self.account_invoice_b2cs.partner_id and not self.\
                account_invoice_b2cs.vat and partner_location == \
                'intra_state' or partner_location == 'inter_state' and \
                self.account_invoice_b2cs.amount_total < \
                self.b2c_limit_b2cs.b2cs_limit:
            self.assertTrue(self.account_invoice_b2cs.gst_invoice == 'b2cs',
                            'Invoice must be a type B2CS')

        # Test GST number of a partner
        if self.account_invoice_b2cs.partner_id.gst_type != 'unregistered':
            self.assertTrue(self.account_invoice_b2cs.vat, False,
                            'Registered partner must have GST Number')

        self.details_of_invoice(self.account_invoice_b2cs)

    def test_invoice_b2cl(self):
        # Add tax for product
        for line in self.account_invoice_b2cl.invoice_line_ids:
            line.write({
                'invoice_line_tax_ids': [(4, self.tax_igst_5.id)]
            })
        # Test for invoice type before validation
        assert not self.account_invoice_b2cl.gst_invoice, \
            'Invoice type should be null'

        # Test the state of invoice before validation
        self.assertEquals(self.account_invoice_b2cl.state, 'draft')

        # Test state of invoice after validation
        self.account_invoice_b2cl.action_invoice_open()
        self.assertEquals(self.account_invoice_b2cl.state, 'open')

        # Test for move attachment
        assert self.account_invoice_b2cl.move_id, \
            'Move is not created for open invoice'
        partner_location = \
            self.account_invoice_b2cl.partner_id.partner_location
        # Test for GST Invoice type
        if self.account_invoice_b2cl.partner_id and not \
                self.account_invoice_b2cl.vat and \
                partner_location == 'inter_state' and \
                self.account_invoice_b2cl.amount_total > \
                self.b2c_limit_b2cl.b2cl_limit:
            self.assertTrue(self.account_invoice_b2cl.gst_invoice == 'b2cl',
                            'Invoice must be a type B2CL')

        # Test GST number of a partner
        if self.account_invoice_b2cl.partner_id.gst_type != 'unregistered':
            self.assertTrue(self.account_invoice_b2cl.vat, False,
                            'Registered partner must have GST Number')

        self.details_of_invoice(self.account_invoice_b2cl)

        # Create refund invoice
        self.account_invoice_refund_b2cl = self.account_invoice_b2cl.refund()

        # Test for invoice type
        assert self.account_invoice_refund_b2cl.gst_invoice, \
            'Invoice type should be null'

        # Test for state initially
        self.assertEquals(self.account_invoice_refund_b2cl.state, 'draft')

        # Test the state after invoice validation
        self.account_invoice_refund_b2cl.action_invoice_open()
        self.assertEquals(self.account_invoice_refund_b2cl.state, 'open')

        # Test whether refund invoice is created
        assert self.account_invoice_refund_b2cl.refund_invoice_id, \
            'Refund invoice is not created'

        # Test for refund invoice created for B2CL type invoice
        self.assertEquals(self.account_invoice_refund_b2cl.
                          refund_invoice_id.id, self.account_invoice_b2cl.id,
                          'Refund invoice for B2CL type is not created')

        # Test refunded amount total
        self.assertEquals(
            -self.account_invoice_refund_b2cl.amount_untaxed_signed,
            self.account_invoice_b2cl.amount_untaxed_signed,
            'Amount total is wrong in refund')

        self.details_of_invoice(self.account_invoice_refund_b2cl)

    def test_invoice_composite(self):
        company_id = self.account_invoice_composite.company_id
        company_id.write({'gst_type': 'composite'})

        # Add tax for product
        for line in self.account_invoice_b2cl.invoice_line_ids:
            line.write({
                'invoice_line_tax_ids': [(4, self.tax_gst_18.id)]
            })

        # Test for state initially
        self.assertEquals(self.account_invoice_composite.state, 'draft')

        # Test for invoice type before validation
        assert not self.account_invoice_composite.gst_invoice, \
            'Invoice type should be null'

        # Test state of invoice after validation
        self.account_invoice_composite.action_invoice_open()
        self.assertEquals(self.account_invoice_composite.state, 'open')

        # If company is composite then tax computation is not there
        if company_id.gst_type == 'composite':
            self.assertEquals(len(
                self.account_invoice_composite.tax_line_ids.ids), 0,
                'Taxes should not be calculated if company is composite')

        self.details_of_invoice(self.account_invoice_composite)

        company_id.write({'gst_type': 'regular'})
