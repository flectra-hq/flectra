# -*- coding: utf-8 -*-

from flectra import api, fields, models


class Company(models.Model):
    _name = "res.company"
    _inherit = ["res.company"]

    branch_id = fields.Many2one('res.branch', 'Branch', ondelete="restrict")

    @api.model
    def create(self, vals):
        branch = self.env['res.branch'].create({
            'name': vals['name'],
            'code': vals['name'],
        })
        vals['branch_id'] = branch.id
        self.clear_caches()
        company = super(Company, self).create(vals)
        branch.write({'partner_id': company.partner_id.id,
                      'company_id': company.id})
        return company

class ResBranch(models.Model):
    _name = "res.branch"

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    active = fields.Boolean(string='Active', default=True)
    partner_id = fields.Many2one('res.partner', string='Partner',
                                 ondelete='restrict')
    company_id = fields.Many2one(
        'res.company', string="Company",
        default=lambda self: self.env.user.company_id, required=True)
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

    _sql_constraints = [('branch_code_company_uniq', 'unique (code,company_id)',
                         'The branch code must be unique per company!')]

    @api.model
    def create(self, vals):
        if not vals.get('partner_id', False):
            partner_id = self.env['res.partner'].create({'name': vals['name']})
            vals.update({'partner_id': partner_id.id})
        res = super(ResBranch, self).create(vals)
        vals.pop("name", None)
        vals.pop("code", None)
        vals.pop("partner_id", None)
        vals.update({'branch_id': res.id})
        res.partner_id.write(vals)
        return res

    @api.multi
    def write(self, vals):
        res = super(ResBranch, self).write(vals)
        vals.pop("name", None)
        vals.pop("code", None)
        vals.pop("company_id", None)
        vals.pop("partner_id", None)
        ctx = self.env.context.copy()
        if 'branch' not in ctx:
            self.partner_id.write(vals)
        return res


class Users(models.Model):

    _inherit = "res.users"

    @api.model
    def branch_default_get(self, user):
        if not user:
            user = self._uid
        branch_id = self.env['res.users'].browse(user).default_branch_id
        if not branch_id:
            branch_id = \
                self.env['res.users'].browse(user).company_id.branch_id
        return branch_id

    @api.model
    def _get_default_branch(self):
        return self.branch_default_get(self._uid)

    branch_ids = fields.Many2many('res.branch',
                                  'res_branch_users_rel',
                                  'user_id',
                                  'branch_id',
                                  'Branches')
    default_branch_id = fields.Many2one('res.branch', 'Default branch',
                                        default=_get_default_branch,
                                        domain="[('company_id','=',company_id)"
                                               "]")


