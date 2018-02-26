# Part of Flectra. See LICENSE file for full copyright and licensing details.
from flectra import fields, models


class PaymentAcquirer(models.Model):
    _inherit = "payment.acquirer"

    website_id = fields.Many2one('website', string='Website', copy=False,
                                 help='Define website in which Payment '
                                      'Gateway will published.')
