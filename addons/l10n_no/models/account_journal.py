# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    invoice_reference_model = fields.Selection(selection_add=[
        ('no', 'Norway')
    ], ondelete={'no': lambda recs: recs.write({'invoice_reference_model': 'flectra'})})
