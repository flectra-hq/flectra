# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models

class HrEmployee(models.Model):
    _name = 'hr.employee'
    _inherit = ['hr.employee', 'website.published.mixin']

    public_info = fields.Char(string='Public Info')
    website_ids = fields.Many2many('website', 'website_hr_emp_pub_rel',
                                   'website_id', 'emp_id',
                                   string='Websites', copy=False,
                                   help='List of websites in which Employee is published.')

    @api.multi
    def _compute_website_url(self):
        super(HrEmployee, self)._compute_website_url()
        for employee in self:
            employee.website_url = '/aboutus#team'
