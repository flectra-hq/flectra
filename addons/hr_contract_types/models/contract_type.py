# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models, _


class ContractType(models.Model):
    _name = 'hr.contract.type'
    _description = 'Contract Type'
    _order = 'sequence, id'

    name = fields.Char(string='Contract Type', required=True, help="Name")
    sequence = fields.Integer(help="Gives the sequence when displaying a list of Contract.", default=10)


class ContractInherit(models.Model):
    _inherit = 'hr.contract'

    type_id = fields.Many2one('hr.contract.type', string="Employee Category",
                              help="Employee category",
                              default=lambda self: self.env['hr.contract.type'].sudo().search([], limit=1))
