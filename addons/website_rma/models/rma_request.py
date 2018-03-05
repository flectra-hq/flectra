# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models


class RmaReuqest(models.Model):
    _inherit = ['rma.request']

    type = fields.Selection([
        ('return_replace', 'Return/Replace'),
        ('web_return_replace', 'Web Return/Replace')
    ], string='Request Type', help="Type of return request")

    @api.multi
    def _compute_is_website(self):
        for request in self:
            request.is_website = request.type and request.type == \
                                                  'web_return_replace' or False
