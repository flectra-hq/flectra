{
    "name": "Flectra Core Backend",
    "category": "Hidden",
    "version": "3.0",
    "author": "FlectraHQ",
    "website": "https://flectrahq.com/",
    'company': 'FlectraHQ Inc.',
    "depends": ['base', 'web'],
    'auto_install': True,
    "data": [
        # 'views/style.xml',
        'data/theme_config.xml',
        'data/ir_config_param_data.xml',
        'views/sidebar.xml',
        'views/web.xml',
        'views/res_config_settings.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'web_flectra/static/src/scss/login.scss',
        ],
        'web.assets_backend': [
            'web_flectra/static/src/scss/theme_primary_variables.scss',
            'web_flectra/static/src/scss/theme/apps_menu.scss',
            'web_flectra/static/src/scss/theme/common_style.scss',
            'web_flectra/static/src/scss/theme/fields_extra.scss',
            'web_flectra/static/src/scss/theme/form_view_extra.scss',
            'web_flectra/static/src/scss/theme/list_view_extra.scss',
            'web_flectra/static/src/scss/theme/navbar.scss',
            'web_flectra/static/src/scss/theme/search_view_extra.scss',
            'web_flectra/static/src/scss/theme/webclient_extra.scss',
            'web_flectra/static/src/scss/kanban_view_mobile.scss',
            'web_flectra/static/src/scss/search_view_mobile.scss',
            'web_flectra/static/src/scss/search_view_extra.scss',
            'web_flectra/static/src/scss/backend_theme_customizer/dark_mode.scss',
            'web_flectra/static/src/scss/backend_theme_customizer/style.scss',
            'web_flectra/static/src/scss/sidebar.scss',
            # 'web_flectra/static/src/scss/web_responsive.scss',
            'web_flectra/static/src/js/theme/apps_menu.js',
            'web_flectra/static/src/js/theme/web_client.js',
            'web_flectra/static/src/js/theme/control_panel.js',
            'web_flectra/static/src/js/theme/control_legacy_panel.js',
            'web_flectra/static/src/js/theme/DropdownItem.js',
            'web_flectra/static/src/js/theme/home_menu_wrapper.js',
            'web_flectra/static/src/js/theme/home_menu.js',
            'web_flectra/static/src/js/theme/search_panel.js',
            'web_flectra/static/src/js/theme/user_menu.js',
            'web_flectra/static/src/js/sidebar.js',
            'web_flectra/static/src/js/blockui.js',
            'web_flectra/static/src/js/theme/theme_customizer.js',
            # 'web_flectra/static/src/js/theme/backend_theme_customizer.js',
            'web_flectra/static/lib/spectrum/js/spectrum.js',
            'web_flectra/static/lib/jquery.touchSwipe/jquery.touchSwipe.js',
            'web_flectra/static/src/xml/backend_theme_customizer.xml',
            'web_flectra/static/src/xml/navbar.xml',
            'web_flectra/static/src/xml/menu.xml',
            'web_flectra/static/lib/spectrum/css/spectrum.css',
            'web_flectra/static/src/scss/style.scss',
            'web_flectra/static/src/scss/theme/form_view_extra.scss',
            'web_flectra/static/src/scss/fonts.scss',
            'web_flectra/static/src/scss/preloader.scss',
        ],
        'web.assets_qweb': [
            'web_flectra/static/src/xml/menu.xml',
            'web_flectra/static/src/xml/backend_theme_customizer.xml',
        ],

        'web._assets_bootstrap': [
            'web_flectra/static/src/scss/theme_primary_variables.scss',
            'web_flectra/static/src/scss/variables.scss',
        ],

        'web._assets_helpers': [
            'web_flectra/static/src/scss/variables.scss',
         ],

        'web._assets_primary_variables': [
            '/web_flectra/static/src/scss/backend_theme_customizer/colors.scss',
            ('replace', '/web_editor/static/src/scss/web_editor.variables.scss', 'web_flectra/static/src/scss/color_palettes.scss',),
        ],

        'point_of_sale.assets': [
            'web_flectra/static/src/scss/theme/form_view_extra.scss',
        ]


    },
    "license": "LGPL-3",
    "uninstall_hook": "_uninstall_reset_changes",
}
