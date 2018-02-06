# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models

class HrEmployee(models.Model):
    _name = 'hr.employee'
    _inherit = ['hr.employee', 'website.published.mixin']

    def _default_website(self):
        default_website_id = self.env.ref('website.default_website')
        return [default_website_id.id] if default_website_id else None

    public_info = fields.Char(string='Public Info')
    website_ids = fields.Many2many('website', 'website_hr_emp_pub_rel',
                                   'website_id', 'emp_id',
                                   default=_default_website,
                                   string='Websites', copy=False,
                                   help='List of websites in which Employee '
                                        'will published.')

    @api.multi
    def _compute_website_url(self):
        super(HrEmployee, self)._compute_website_url()
        for employee in self:
            employee.website_url = '/aboutus#team'
