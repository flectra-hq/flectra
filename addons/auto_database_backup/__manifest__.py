# Part of Flectra. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    FlectraHQ Inc.
#    Copyright (C) 2017-TODAY FlectraHQ Inc(<https://www.flectrahq.com>).
#
##############################################################################
{
    'name': "Automatic Database Backup To Local Server",
    'summary': """Generate automatic backup of databases and store to local server""",
    'version': '3.0.1.0',
    'author': "FlectraHQ Inc, Cybrosys",
    'website': "https://flectrahq.com",
    'category': 'Tools',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/cron_data.xml',
        'data/mail_data.xml',
        'views/db_backup_configure_views.xml',
        'views/res_config_setting_view.xml',
        'wizard/module_upgrade_wizard_views.xml',
    ],
    'license': 'LGPL-3',
    'images': ['static/description/banner.gif'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
