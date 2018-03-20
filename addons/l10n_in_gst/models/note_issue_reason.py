# Part of Flectra See LICENSE file for full copyright and licensing details.

""" Introduce following new models for GST related customization:
        * Note Issue Reasons
"""

from flectra import api, fields, models


class NoteIssueReason(models.Model):
    _name = 'note.issue.reason'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)

    @api.multi
    def name_get(self):
        """ It will display field data in proper format as specified in this
        method """
        result = []
        for record in self:
            result.append((record.id, '%s-%s' % (record.code, record.name)))
        return result
