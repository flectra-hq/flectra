# Part of Flectra. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    FlectraHQ Inc.
#    Copyright (C) 2017-TODAY FlectraHQ Inc(<https://www.flectrahq.com>).
#
##############################################################################


from flectra import fields, models


class ModuleUpgradeWizard(models.TransientModel):
    _name = 'module.upgrade.wizard'
    _description = 'Module Upgrade Wizard'

    module_id = fields.Many2one('ir.module.module',
                                default=lambda self: self.env.context.get('active_id'))
    database_backup =\
        fields.Boolean("Do you want to take database backup?",
                       default=lambda self: self.env.context.get('auto_backup'))
    backup_option_id = fields.Many2one('db.backup.configure')

    def action_module_upgrade(self):
        if self.database_backup:
            self.backup_option_id.create_database_backup()
        self.module_id._button_immediate_function(type(self.module_id).button_upgrade)
