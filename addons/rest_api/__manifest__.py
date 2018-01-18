# Part of Flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'REST API For Flectra',
    'version': '1.0.0',
    'category': 'API',
    'author': 'FlectraHQ',
    'website': 'https://www.flectrahq.com',
    'summary': 'REST API For Flectra',
    'description': """
REST API For Flectra
====================
With use of this module user can enable REST API in any Flectra applications/modules

For detailed example of REST API refer *readme.md*
""",
    'depends': [
        'web',
    ],
    'data': [
        'data/ir_configparameter_data.xml',
        'views/ir_model_view.xml',
        'views/res_user_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
}
