# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.
from flectra import api, models


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def create(self, vals):
        """ Automatically subscribe employee users to default digest if activated """
        user = super(ResUsers, self).create(vals)
        config_obj = self.env['ir.config_parameter'].sudo()
        default_digest_emails = config_obj.get_param('digest.default_digest_emails')
        default_digest_id = config_obj.get_param('digest.default_digest_id')
        if user.has_group('base.group_user') and default_digest_emails and default_digest_id:
            digest = self.env['digest.digest'].sudo().browse(int(default_digest_id))
            digest.user_ids |= user
        return user
