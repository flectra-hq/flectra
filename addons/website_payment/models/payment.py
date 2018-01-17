# Part of Flectra. See LICENSE file for full copyright and licensing details.
from flectra import fields, models


class PaymentAcquirer(models.Model):
    _inherit = "payment.acquirer"

    website_id = fields.Many2many('website', 'website_payment_rel',
                                  'website_id', 'payment_id',
                                  string='Website')
