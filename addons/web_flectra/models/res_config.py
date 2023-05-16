from flectra import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    allow_suggested_recipient = fields.Boolean(string='Allow Suggested Recipient',
                                               config_parameter='web_flectra.allow_suggested_recipient')


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        res = super(IrHttp, self).session_info()
        res['allow_suggested_recipient'] = self.env['ir.config_parameter'].sudo().\
            get_param('web_flectra.allow_suggested_recipient')
        return res
