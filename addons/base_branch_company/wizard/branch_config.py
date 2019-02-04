# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, models, fields


class BarnchConfiguration(models.TransientModel):
    _name = 'branch.config'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    branch_id = fields.Many2one('res.branch', 'Branch')
    company_id = fields.Many2one('res.company', string="Company",
        default=lambda self: self.env.user.company_id, required=True)
    partner_id = fields.Many2one('res.partner', string='Partner')
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State',
                               ondelete='restrict')
    country_id = fields.Many2one('res.country', string='Country',
                                 ondelete='restrict')
    email = fields.Char()
    phone = fields.Char()
    mobile = fields.Char()
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm')],
        default='draft')
    user_ids = fields.Many2many('res.users', 'res_users_branch_rel',
                                 'user_id', 'branch_id', 'Allowed Branch for users',
                                 domain="[('company_id','=',company_id)]")
    default_user_ids = fields.Many2many('res.users', 'res_users_branch_default_rel',
                                 'user_id', 'branch_id', 'Default Branch for users',
                                 domain="[('company_id','=',company_id)]")

    @api.onchange('state_id')
    def _onchange_state(self):
        self.country_id = self.state_id.country_id

    @api.multi
    def branch_config(self):
        s_ids = self.search_read([('id', '=', self.id)], [])[0]
        branch = self.env['res.branch'].create({
            'name': s_ids['name'],
            'code': s_ids['code'],
            'street': s_ids['street'],
            'street2': s_ids['street2'],
            'zip': s_ids['zip'],
            'city': s_ids['city'],
            'state_id': s_ids['state_id'] and s_ids['state_id'][0],
            'country_id': s_ids['country_id'] and s_ids['country_id'][0],
            'email': s_ids['email'],
            'phone': s_ids['phone'],
            'company_id': s_ids['company_id'] and s_ids['company_id'][0],
            'mobile': s_ids['mobile'],
        })
        self.write({'state': 'confirm',
                    'partner_id': branch.partner_id.id,
                    'branch_id': branch.id})
        view_id = self.env.ref(
            'base_branch_company.view_branch_config')
        context = dict(self._context)
        return {'views': [(view_id.id, 'form')], 'view_id': view_id.id,
                'type': 'ir.actions.act_window', 'view_type': 'form',
                'view_mode': 'form', 'res_model': 'branch.config',
                'target': 'new', 'res_id': self.id, 'context': context, }


    @api.multi
    def finish_branch_config(self):
        for user_id in self.user_ids:
            user_id.write({'branch_ids': [(4, self.branch_id.id)]})
        for user_id in self.user_ids:
            user_id.write({'default_branch_id': self.branch_id.id})

