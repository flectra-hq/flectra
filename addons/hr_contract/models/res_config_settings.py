# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    contract_expiration_notice_period = fields.Integer(string="Contract Expiry Notice Period", related='company_id.contract_expiration_notice_period', readonly=False)
    work_permit_expiration_notice_period = fields.Integer(string="Work Permit Expiry Notice Period", related='company_id.work_permit_expiration_notice_period', readonly=False)
