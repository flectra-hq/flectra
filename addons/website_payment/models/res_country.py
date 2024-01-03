# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models
from flectra.addons.payment_stripe.const import SUPPORTED_COUNTRIES as STRIPE_SUPPORTED_COUNTRIES


class ResCountry(models.Model):
    _inherit = 'res.country'

    is_stripe_supported_country = fields.Boolean(compute='_compute_is_stripe_supported_country')

    @api.depends('code')
    def _compute_is_stripe_supported_country(self):
        for country in self:
            country.is_stripe_supported_country = country.code in STRIPE_SUPPORTED_COUNTRIES
