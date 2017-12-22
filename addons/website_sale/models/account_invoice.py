# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    website_id = fields.Many2one('website', string="Website")


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.multi
    def _create_invoice(self, order, so_line, amount):
        res = super(SaleAdvancePaymentInv, self)._create_invoice(order,
                                                                 so_line,
                                                                 amount)

        res.website_id = order.website_id

        return res
