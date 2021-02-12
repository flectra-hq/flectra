import logging
from flectra import models, fields, api, _

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    exclude_from_document_discount = fields.Boolean(
            string='No Document Discount',
            help='When enabled the position is excluded from Document Discount',
    )
