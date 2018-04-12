# Part of Flectra. See LICENSE file for full copyright and licensing
# details.

from flectra import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    is_gst = fields.Boolean(string='Is GST Applicable?', default=False)
    gst_number = fields.Char(string='GST Number', size=256)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_gst = fields.Boolean(string='Is GST Applicable?', default=False)
    gst_number = fields.Char(string='GST Number', size=256)
