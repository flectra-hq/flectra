import logging
from flectra import models, fields, api, _

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    document_discount_fixed_account_id = fields.Many2one(
            related='company_id.document_discount_fixed_account_id',
            readonly=False,
    )

    document_discount_percent_account_id = fields.Many2one(
            related='company_id.document_discount_percent_account_id',
            readonly=False,
    )
