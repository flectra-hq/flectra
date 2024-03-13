# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, models


class Company(models.Model):
    _inherit = 'res.company'

    @api.ondelete(at_uninstall=False)
    def _unlink_onboarding_progress(self):
        progress = self.env['onboarding.progress'].sudo().search([('company_id', 'in', self.ids)])
        progress.unlink()
