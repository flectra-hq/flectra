# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import models
from flectra.tools import populate


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    def _populate_factories(self):
        return super()._populate_factories() + [
            ('visibility', populate.randomize(['visible', 'hidden'], [6, 3])),
        ]
