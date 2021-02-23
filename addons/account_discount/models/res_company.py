import logging
from flectra import models, fields, api, _

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    document_discount_fixed_account_id = fields.Many2one(
            comodel_name='account.account',
            string='Account for fixed Discount',
    )

    document_discount_percent_account_id = fields.Many2one(
            comodel_name='account.account',
            string='Account for percent Discount',
    )
