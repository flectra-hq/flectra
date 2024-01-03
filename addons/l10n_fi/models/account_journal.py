# Part of Flectra. See LICENSE file for full copyright and licensing details.
from flectra import models, fields


class AccountJournal(models.Model):

    _inherit = 'account.journal'

    invoice_reference_model = fields.Selection(selection_add=[
        ('fi', 'Finnish Standard Reference'),
        ('fi_rf', 'Finnish Creditor Reference (RF)'),
    ], ondelete={'fi': lambda recs: recs.write({'invoice_reference_model': 'flectra'}),
                 'fi_rf': lambda recs: recs.write({'invoice_reference_model': 'flectra'})})
