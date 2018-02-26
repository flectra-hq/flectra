# -*- coding: utf-8 -*-

from flectra import api, fields, models
from flectra.addons.http_routing.models.ir_http import slug


class WebsiteResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'website.seo.metadata', 'website.published.mixin']

    def _default_website(self):
        default_website_id = self.env.ref('website.default_website')
        return [default_website_id.id] if default_website_id else None

    website_description = fields.Html('Website Partner Full Description', strip_style=True)
    website_short_description = fields.Text('Website Partner Short Description')
    website_ids = fields.Many2many('website', 'website_partner_pub_rel',
                                   'website_id', 'partner_id',
                                   string='Websites', copy=False,
                                   default=_default_website,
                                   help='List of websites in which '
                                        'Partner will published.')

    @api.multi
    def _compute_website_url(self):
        super(WebsiteResPartner, self)._compute_website_url()
        for partner in self:
            partner.website_url = "/partners/%s" % slug(partner)
