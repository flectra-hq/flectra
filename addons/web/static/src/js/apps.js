flectra.define('web.Apps', function (require) {
"use strict";

var core = require('web.core');
var Widget = require('web.Widget');
var Dialog = require('web.Dialog');
var framework = require('web.framework');

var _t = core._t;
var QWeb = core.qweb;

var Apps = Widget.extend({
    template: 'AppStore',
    events: {
        'click [app-action="download"]': '_onDownload',
        'click [app-action="install"]': '_onInstall',
        'click [app-action="uninstall"]': '_onUninstall',
        'click [app-action="view-info"]': '_onClickViewDetails',
        'click .load-more': '_onLoadMore',
        'click #try-again': '_onTryAgain',
        'keypress #input-module-search': '_onEnterSearch',
        'click #btn-module-search': '_onClickSearch',
        'click .top': '_onClickTop',
    },
    init: function (parent, action) {
        this._super(parent, action);
        var options = action.params || {};
        this.context = {};
        this.params = options;
    },
    willStart: function () {
        var self = this;
        var def = this._rpc({
            route: '/web/get_app_store_mode',
        });
        return $.when(def, this._super.apply(this, arguments)).then(function (mode) {
            self.mode = mode;
            framework.blockUI();
            if (self.mode != 'disable') {
                self._rpc({
                    route: '/web/get_modules',
                }).done(function (data) {
                    if (data) {
                        self.all_app = [];
                        _.each(data.modules, function (categ) {
                            self.all_app = self.all_app.concat(categ);
                        });
                        self.active_categ = data.categ[0][0];
                        self.store_url = data.store_url;
                        self.search_categ = '';
                        self.$el.html(QWeb.render('AppStore.Content', {
                            modules: data.modules,
                            categ: data.categ,
                            installed_modules: data.installed_modules,
                            mode: self.mode,
                            store_url: data.store_url
                        }));
                        if (data.banner) {
                            self.$el.find('.banner').html(data.banner);
                        } else {
                            self.$el.find('.banner').html('<h2 class="text-center">FlectraHQ Store</h2>');
                        }
                        self.$el.find('ul.nav.category a:first').tab('show');
                        self.$el.find('a[data-toggle="tab"]').on('shown.bs.tab', self._onChangeTab.bind(self));
                        self.context.categ = self.prepareContext(data.categ);
                        self.context.limit = data.limit;
                    } else {
                        self.$el.html(QWeb.render('AppStore.TryError', {}));
                    }
                    framework.unblockUI();
                });
            }
        });
    },
    destroy: function () {
        $(window).off("message." + this.uniq);
        if (this.$ifr) {
            this.$ifr.remove();
            this.$ifr = null;
        }
        return this._super();
    },
    start: function () {
        if (this.mode == 'disable') {
            this.$el.html(QWeb.render('AppStore.Disable', {}));
            framework.unblockUI();
        }
        return this._super.apply(this, arguments);
    },
    prepareContext: function (data) {
        var context = {};
        _.each(data, function (value) {
            context[value[0]] = {
                offset: 0,
                search: ''
            }
        });
        return context
    },
    _openDialogAfterAction: function (data) {
        if (!_.isEmpty(data)) {
            if (data.success) {
                window.location.reload();
                return;
            }
            var buttons = [{
                text: _t("OK"),
                classes: 'btn-success',
                close: true,
            }];
            var dialog = new Dialog(this, {
                size: 'medium',
                buttons: buttons,
                $content: $("<h4>" + data.error + "</h4>"),
                title: _t("Error"),
            });
            dialog.open();
        }
    },
    _onUninstall: function (e) {
        e.preventDefault();
        var self = this;
        var id = $(e.target).data("module-id");
        var data = _.findWhere(this.all_app, {id: id});
        if (!_.isEmpty(data)) {
            this._rpc({
                route: '/web/app_action',
                params: {
                    action: "uninstall",
                    module_name: data['technical_name'],
                },
            }).then(function (data) {
                self._openDialogAfterAction(data);
            })
        }
    },
    _onDownload: function (e) {
        e.preventDefault();
        var href = $(e.currentTarget).attr('href').trim();
        if (href) {
            window.location = href;
        }
    },
    _onInstall: function (e) {
        e.preventDefault();
        var self = this;
        var id = $(e.target).data("module-id");
        var data = _.findWhere(this.all_app, {id: id});
        self._rpc({
            route: '/web/app_download_install',
            params: {
                id: data['md5_val'],
                checksum: data['checksum'],
                module_name: data['technical_name']
            }
        }).then(function (data) {
            self._openDialogAfterAction(data);
        });
    },
    _onChangeTab: function (e) {
        this.active_categ = $(e.target).data("category-id");
        this.$el.find('#input-module-search').val(this.context.categ[this.active_categ]['search']);
    },
    _onLoadMore: function (e) {
        e.preventDefault();
        var self = this;
        framework.blockUI();
        this.context.categ[this.active_categ]['offset'] += this.context.limit;
        this._rpc({
            route: '/web/get_modules',
            params: {
                offset: this.context.categ[this.active_categ]['offset'],
                categ: this.active_categ,
                search: this.context.categ[this.active_categ]['search']
            }
        }).done(function (data) {
            if (data) {
                self.all_app = self.all_app.concat(data.modules[self.active_categ]);
                self.$el.find('#' + self.active_categ + " .module-kanban:last")
                    .after(QWeb.render('AppStore.ModuleBoxContainer', {
                        modules: data.modules[self.active_categ],
                        installed_modules: data.installed_modules,
                        mode: self.mode,
                        store_url: data.store_url
                    }));
                if (!_.isEmpty(data.modules[self.active_categ]) && data.modules[self.active_categ].length == data.limit) {
                    self.$el.find('#' + self.active_categ + " .load-more").show();
                } else {
                    var $rec = self.$el.find('#' + self.active_categ + " .module-kanban ");
                    var $load_more = self.$el.find('#' + self.active_categ + " .load-more");
                    $load_more.hide().next('h3').remove();
                    if (!$rec.length) {
                        $load_more.after('<h3>No such module(s) found.</h3>');
                    }
                }
            } else {
                self.$el.html(QWeb.render('AppStore.TryError', {}));
            }
            framework.unblockUI();
        });
    },
    _onTryAgain: function (e) {
        e.preventDefault();
        var self = this;
        this._rpc({
            route: '/web/action/load',
            params: {action_id: "base.modules_act_cl"},
        }).then(function (action) {
            self.do_action(action);
        });
    },
    _onEnterSearch: function (e) {
        if (e.keyCode == 13) {
            e.preventDefault();
            this._onModuleSearch(e);
        }
    },
    _onClickSearch: function (e) {
        e.preventDefault();
        this._onModuleSearch(e);
    },
    _onModuleSearch: function (e) {
        var search = this.$el.find('#input-module-search').val().trim();
        var self = this;
        framework.blockUI();
        this._rpc({
            route: '/web/get_modules',
            params: {
                offset: 0,
                categ: this.active_categ,
                search: search
            }
        }).done(function (data) {
            if (data) {
                self.all_app = self.all_app.concat(data.modules[self.active_categ]);
                self.$el.find('#' + self.active_categ).find('.module-kanban').remove();
                self.context.categ[self.active_categ]['search'] = search;
                self.context.categ[self.active_categ]['offset'] = 0;
                $(QWeb.render('AppStore.ModuleBoxContainer', {
                    modules: data.modules[self.active_categ],
                    installed_modules: data.installed_modules,
                    mode: self.mode,
                    store_url: data.store_url
                })).prependTo(self.$el.find('#' + self.active_categ + " .o_kanban_view"));
                if (!_.isEmpty(data.modules[self.active_categ]) && data.modules[self.active_categ].length == data.limit) {
                    self.$el.find('#' + self.active_categ + " .load-more").show().next('h3').remove();
                } else {
                    var $rec = self.$el.find('#' + self.active_categ + " .module-kanban ");
                    var $load_more = self.$el.find('#' + self.active_categ + " .load-more");
                    $load_more.hide().next('h3').remove();
                    if (!$rec.length) {
                        $load_more.after('<h3>No such module(s) found.</h3>');
                    }
                }
            } else {
                self.$el.html(QWeb.render('AppStore.TryError', {}));
            }
            framework.unblockUI();
        });
    },
    _onClickViewDetails: function (e) {
        e.preventDefault();
        var id = $(e.currentTarget).data('module-id');
        var data = _.findWhere(this.all_app, {id: id});
        if (!_.isEmpty(data)) {
            var dialog = new Dialog(this, {
                size: 'medium',
                $content: $(QWeb.render('AppStore.ViewDetails', {app: data, store_url: this.store_url})),
                title: _t('Module'),
            });
            dialog.open();
        }
    },
    _onClickTop: function (e) {
        e.preventDefault();
        this.$el.parents('.o_content').animate({scrollTop:0}, 500, 'swing');
    }
});

var AppsUpdates = Apps.extend({
    remote_action_tag: 'loempia.embed.updates',
});

core.action_registry.add("apps", Apps);
core.action_registry.add("apps.updates", AppsUpdates);

return Apps;

});
