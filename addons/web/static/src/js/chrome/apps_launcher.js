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
        'click .f_remove_bookmark i': '_removeBookmark',
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
            if ($('.launcher_opened').length && e.keyCode == 27) {
                $('.f_search_launcher').removeClass('launcher_opened');
                self.$el.parents().find('#f_apps_search').find('i').toggleClass('fa-search fa-times');
            }
        });
        this.render();
        this.$('.f_app_footer img').attr('src',img);

    },
    render: function () {
        var self = this;
        this._loadAllMenuData().then(function () {
            var app_contents = self.$el.find('.f_apps_contents');
            if(!app_contents.length){
                app_contents = $('.f_search_launcher .f_apps_contents');
                $('.f_search_launcher .f_apps_search_input').val('');
            }
            app_contents.html(QWeb.render('FlectraMenuContent', {
                bookmark_menus: self.bookmarkMenus,
                dashboard_apps: self.allApps.main_menu,
            }));
        });
    },
    _removeBookmark: function (e) {
        e.stopPropagation();
        var self = this;
        var id = parseInt($(e.currentTarget).data('id'));
        if(id !== NaN){
            rpc.query({
                model: 'menu.bookmark',
                method: 'remove_bookmark',
                args: ['', id]
            }).then(function (res) {
                if(res.id){
                    self.render();
                    if($.bbq.getState(true).action == res.action_id){
                        self.$el.parents().find('.o_user_bookmark_menu > a').removeClass('active');
                    }
                }
            });
        }
        return false;
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
    _loadAllMenuData: function () {
        var self = this;
        var _allApps = rpc.query({
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
            self.allApps = self._simplifyMenuData(menus);
        });
        var _bookmarkMenus = rpc.query({
            model: 'menu.bookmark',
            method: 'get_bookmark_data',
            args: ['', ['name', 'action', 'display_name', 'bookmark_label', 'bookmark_icon']],
            kwargs: {context: session.user_context},
        }).then(function (menus) {
            menus = _.each(menus, function (menu) {
                menu.short_name = self._createShortName(menu.name);
                return menu;
            });

            self.bookmarkMenus = menus;
        });
        return $.when(_allApps, _bookmarkMenus);
    },
    _createShortName: function (menu_name) {
        var s_name = menu_name.split(' ');
        if(s_name.length > 1){
            return (s_name[0].substr(0, 1) + s_name[1].substr(0, 1)).toUpperCase();
        }else{
            return menu_name.substr(0, 2).toUpperCase();
        }
    },
    _clearSearch: function (ev) {
        this.$el.find('.f_apps_search_input').val('');
        this.render();
    },
    _appsSearch: function (ev) {
        var search_str = $(ev.currentTarget).val().trim().toLowerCase();
        var bookmarks = [];
        var main_menus = [];
        var sub_menus = [];

        _.each(this.bookmarkMenus, function (bookmark) {
            if (bookmark.name.trim().toLowerCase().indexOf(search_str) !== -1) {
                bookmarks.push(bookmark);
            }
        });

        _.each(this.allApps.main_menu, function (main_menu) {
            if (main_menu.label.trim().toLowerCase().indexOf(search_str) !== -1) {
                main_menus.push(main_menu);
            }
        });

        _.each(this.allApps.sub_menu, function (sub_menu) {
            if (sub_menu.label.trim().toLowerCase().indexOf(search_str) !== -1) {
                sub_menus.push(sub_menu);
            }
        });

        this.$el.find('.f_apps_contents').html(QWeb.render('FlectraMenuContent', {
            bookmark_menus: bookmarks,
            dashboard_apps: main_menus,
            sub_menus : search_str == ''? undefined : sub_menus
        }));
    },
    _o_app_click: function (ev) {
        ev.preventDefault();
        this.parent._isMainMenuClick = false;
        this.$el.removeClass('launcher_opened');
        this.$el.parents().find('#f_apps_search').find('i').addClass('fa-search').removeClass('fa-times');
        this.parent.menu_click($(ev.currentTarget).data('menu'));
    },
    _simplifyMenuData: function (app, result, menu_id) {
        result = result || {
            main_menu:[],
            sub_menu:[]
        };
        menu_id = menu_id || false;
        var item = {
            label: (app.parent_id && app.parent_id.length) ? [app.parent_id[1], app.name].join('/').replace(/\//g, ' / ') : app.name,
            id: app.id,
            xmlid: app.xmlid,
            action: app.action ? app.action.split(',')[1] : '',
            is_app: !app.parent_id,
            web_icon: app.web_icon
        };

        if (!app.parent_id) {
            if (app.web_icon_data) {
                item.web_icon_data = 'data:image/png;base64,' + app.web_icon_data;
            } else {
                item.web_icon_data = '/base/static/description/icon.png';
            }
        } else {
            item.menu_id = menu_id;
        }

        if (item.action !== "") {
            if(item.is_app){
                result.main_menu.push(item);
            }else if(!item.is_app){
                result.sub_menu.push(item);
            }
        }

        if (app.children && app.children.length) {
            for (var i in app.children) {
                if (app.children[i].parent_id === false) {
                    menu_id = app.children[i].id;
                }
                this._simplifyMenuData(app.children[i], result, menu_id);
            }
        }
        return result;
    }
});

return Apps;

});
