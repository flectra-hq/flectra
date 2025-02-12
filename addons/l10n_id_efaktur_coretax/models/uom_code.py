# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import fields, models

class EfakturUomCode(models.Model):
    _name = "l10n_id_efaktur_coretax.uom.code"
    _description = "UOM categorization according to E-Faktur"

    code = fields.Char()
    name = fields.Char()
