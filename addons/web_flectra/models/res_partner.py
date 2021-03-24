# -*- coding: utf-8 -*-
# Copyright 2016, 2019 Openworx
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from flectra import models, fields


class Partner(models.Model):
    _inherit = "res.partner"

    customer = fields.Boolean(string='Is a Customer', default=True,
                               help="Check this box if this contact is a customer.")
    supplier = fields.Boolean(string='Is a Vendor',
                               help="Check this box if this contact is a vendor. "
                               "If it's not checked, purchase people will not see it when encoding a purchase order.")