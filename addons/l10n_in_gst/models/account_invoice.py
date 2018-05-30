# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models, _
from flectra.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    gst_invoice = fields.Selection(
        [('b2b', 'B2B'), ('b2cl', 'B2CL'), ('b2cs', 'B2CS'),
         ('b2bur', 'B2BUR')], string='GST Invoice',
        help='B2B Supplies: Taxable supplies made to other registered '
             'taxpayers.\n\nB2C Large [For outward supplies]: Taxable '
             'outward '
             'supplies to consumers where\na)The place of supply is '
             'outside the state where the supplier is registered and '
             'b)The '
             'total invoice value is more than the limit defined in '
             'company B2C lines.\ne.g., If in B2C line, B2CL limit is '
             'set to Rs 2,50,000 and invoice is of amount Rs 3,00,000 then'
             'invoice '
             'will be considered as of type B2CL.\n\nB2C Small '
             '[For outward supplies]: Supplies made to consumers and '
             'unregistered persons of the following nature\n'
             'a) Intra-State: any value b) Inter-State: Total invoice '
             'value is'
             ' less than the limit defined in company B2C lines.\n'
             'e.g., If in B2C line, B2CS limit is set to Rs 2,50,000 '
             '(for period 01-01-2017 to 31-12-2017) for inter state '
             'supply '
             'and invoice value is Rs 2,00,000 then invoice will be '
             'considered as of type B2CS.\n\nB2BUR [For inward supplies]: '
             'Inward supplies received from an unregistered supplier \n\n',
        copy=False)
    e_commerce_partner_id = fields.Many2one('res.partner',
                                            string='E-Commerce Partner')
    vat = fields.Char(string='GSTIN',
                      help='Goods and Services Taxpayer Identification '
                           'Number', size=15, copy=False)
    gst_type = fields.Selection(
        [('regular', 'Regular'), ('unregistered', 'Unregistered'),
         ('composite', 'Composite'), ('volunteer', 'Volunteer')],
        string='GST Type', copy=False)
    partner_location = fields.Selection(
        [('inter_state', 'Inter State'), ('intra_state', 'Intra State'),
         ('inter_country', 'Inter Country')],
        related='partner_id.partner_location', string="Partner Location")
    fiscal_position_id = fields.Many2one('account.fiscal.position',
                                         string='Nature of Transaction',
                                         oldname='fiscal_position',
                                         readonly=True,
                                         states={
                                             'draft': [('readonly', False)]})

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        super(AccountInvoice, self)._onchange_partner_id()
        if self.partner_id and not self.partner_id.partner_location:
            self.partner_id.partner_location = \
                self.partner_id._get_partner_location_details(self.company_id)


    @api.onchange('fiscal_position_id')
    def _onchange_fiscal_position_id(self):
        """ Onchange of Fiscal Position update tax values in invoice lines. """
        for line in self.invoice_line_ids:
            line._set_taxes()

    @api.multi
    def action_move_create(self):
        """ Do not apply taxes if company has been registered under
        composition scheme. """
        for invoice in self:
            if invoice.type in ('out_invoice',
                                'out_refund') and \
                    invoice.company_id.gst_type == 'composite':
                for line in invoice.invoice_line_ids:
                    line.invoice_line_tax_ids = [(6, 0, [])]
                    line.invoice_id._onchange_invoice_line_ids()
        return super(AccountInvoice, self).action_move_create()

    @api.multi
    def invoice_validate(self):
        """ Apply GST invoice type at the time of invoice validation. """
        for invoice in self:
            partner_location = self.partner_id.partner_location
            if invoice.partner_id.vat:
                invoice.write({
                    'vat': invoice.partner_id.vat,
                    'gst_type': invoice.partner_id.gst_type,
                    'gst_invoice': 'b2b'
                })
            elif invoice.type == 'out_invoice' and partner_location:
                b2c_limit = self.env['res.company.b2c.limit'].search(
                    [('date_from', '<=', invoice.date_invoice),
                     ('date_to', '>=', invoice.date_invoice),
                     ('company_id', '=', invoice.company_id.id)])
                if not b2c_limit:
                    raise ValidationError(_('Please define B2C limit line in '
                                            'company for current period!'))
                if partner_location == 'inter_state' and \
                        invoice.amount_total > b2c_limit.b2cl_limit:
                    invoice.write({'gst_invoice': 'b2cl'})
                if partner_location == 'intra_state' or partner_location == \
                        'inter_state' and invoice.amount_total < \
                        b2c_limit.b2cs_limit:
                    invoice.write({'gst_invoice': 'b2cs'})
            elif invoice.type == 'in_invoice' and partner_location and \
                    partner_location != 'inter_country':
                invoice.write({'gst_invoice': 'b2bur'})

        return super(AccountInvoice, self).invoice_validate()

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None,
                        description=None, journal_id=None):
        """ Refund invoice creation, update value of GST Invoice from
        base invoice. """
        result = super(AccountInvoice, self)._prepare_refund(
            invoice, date_invoice=date_invoice, date=date,
            description=description, journal_id=journal_id)
        if result.get('refund_invoice_id'):
            invoice = self.env['account.invoice'].browse(
                result.get('refund_invoice_id'))
            result.update({
                'gst_invoice': invoice.gst_invoice, 'vat': invoice.vat,
                'gst_type': invoice.gst_type,
            })
        return result
