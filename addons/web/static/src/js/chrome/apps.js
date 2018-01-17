flectra.define('web.AppsLauncher', function (require) {
    "use strict";

var core = require('web.core');
var session = require('web.session');
var Widget = require('web.Widget');
var rpc = require('web.rpc');

var QWeb = core.qweb;

var Apps = Widget.extend({
    template: 'AppsLauncher',
    events: {
        'click #f_clear_apps_search': '_clearSearch',
        'input .f_apps_search_input': '_appsSearch',
        'click a[data-menu]': '_o_app_click',
    },
    init: function (parent) {
        this._super.apply(this, arguments);
        this.parent = parent;
    },
    start: function () {
        var self = this;
        this._super.apply(this, arguments);
        var company = session.company_id;
        var img = session.url('/web/binary/company_logo' + '?db=' + session.db + (company ? '&company=' + company : ''));
        $(document).keyup(function (e) {
            if (e.keyCode == 27) {
                $('.o_web_client').removeClass('launcher_opened');
                self.$el.parents().find('#f_apps_search').find('i').toggleClass('fa-search fa-times');
            }
        });
        this._createAppDashboardWidget().then(function (apps) {
            self.$el.find('.f_apps_content').html(QWeb.render('AppsLauncher.Menus', {
                dashboard_apps: apps.children
            }));
            self.apps = apps.children;
        });
        this.$('.f_app_footer img').attr('src',img);

    },
    _getAction: function (menu) {
        if (!menu.action && menu.children.length) {
            if (menu.children[0].action) {
                return menu.children[0].action;
            } else {
                return this._getAction(menu.children[0]);
            }
        }
    },
    _createAppDashboardWidget: function () {
        var self = this;
        return rpc.query({
            model: 'ir.ui.menu',
            method: 'load_menus',
            args: [core.debug],
            kwargs: {context: session.user_context},
        }).then(function (menus) {
            menus.children = _.each(menus.children, function (menu) {
                if (!menu.action && menu.children.length) {
                    menu.action = self._getAction(menu);
                }
                return menu;
            });
            return menus;
        });
    },
    _clearSearch: function (ev) {
        this.$el.find('.f_apps_search_input').val('');
        this.$el.find('.f_apps_content').html(QWeb.render('AppsLauncher.Menus', {
            dashboard_apps: this.apps
        }));
    },
    _appsSearch: function (ev) {
        var search_str = $(ev.currentTarget).val().trim().toLowerCase();
        var apps = [];
        _.each(this.apps, function (app) {
            if (app.name.trim().toLowerCase().indexOf(search_str) !== -1) {
                apps.push(app);
            }
        });
        this.$el.find('.f_apps_content').html(QWeb.render('AppsLauncher.Menus', {
            dashboard_apps: apps
        }));
    },
    _o_app_click: function (ev) {
        ev.preventDefault();
        this.parent._isMainMenuClick = true;
        this.parent.menu_click($(ev.currentTarget).data('menu'));
    }
});

return Apps;

});
