# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models, _


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    def _eligible_for_qr_code(self, qr_method, debtor_partner, currency):
        if qr_method == 'ch_qr':

            return self.acc_type == 'iban' and \
                   self.partner_id.country_id.code in ('CH', 'LI') and \
                   (not debtor_partner or debtor_partner.country_id.code in ('CH', 'LI')) \
                   and currency.name in ('EUR', 'CHF')

        return super()._eligible_for_qr_code(qr_method, debtor_partner, currency)
