# Part of Flectra. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    FlectraHQ Inc.
#    Copyright (C) 2017-TODAY FlectraHQ Inc(<https://www.flectrahq.com>).
#
##############################################################################
{
    'name': "Automatic Database Backup To Onedrive",
    'summary': """This module allows will generate automatic backup of databases and store to onedrive""",
    'version': '3.0.1.0',
    'author': "FlectraHQ Inc, Cybrosys",
    'website': "https://flectrahq.com",
    'category': 'Tools',
    'depends': ['auto_database_backup'],
    'data': [
        'views/db_backup_configure_views.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
