# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    asset_depreciation_ids = fields.One2many('account.asset.depreciation.line', 'move_id', string='Assets Depreciation Lines', ondelete="restrict")
    asset_id = fields.Many2one('account.asset.asset', string="Asset")

    @api.multi
    def button_cancel(self):
        for move in self:
            for line in move.asset_depreciation_ids:
                line.move_posted_check = False
        return super(AccountMove, self).button_cancel()

    @api.multi
    def post(self):
        self.mapped('asset_depreciation_ids').post_lines_and_close_asset()
        return super(AccountMove, self).post()


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    asset_id = fields.Many2one(related='move_id.asset_id', string="Asset")
