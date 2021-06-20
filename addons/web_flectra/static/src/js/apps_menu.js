flectra.define('web_flectra.AppsMenu', function (require) {
    "use strict";

    var core = require('web.core');
    var AppsMenu = require('web.AppsMenu');

    var Qweb = core.qweb;

    function findNames(memo, menu) {
        if (menu.action) {
            var key = menu.parent_id ? menu.parent_id[1] + "/" : "";
            memo[key + menu.name] = menu;
        }
        if (menu.children.length) {
            _.reduce(menu.children, findNames, memo);
        }
        return memo;
    }

    AppsMenu.include({
        events: _.extend({}, AppsMenu.prototype.events, {
            'input .o_search_box': '_onAppsSearch',
            'click .full': '_onToggleClicked',
            "click .o-menu-search-result": "_searchResultChosen",
            "keydown .search-input input": "_searchResultsNavigate",
        }),
        /**
         * @override
         * @param {web.Widget} parent
         * @param {Object} menuData
         * @param {Object[]} menuData.children
         */
        init: function (parent, menuData) {
            this._super.apply(this, arguments);
            this._activeApp = undefined;
            this._searchApps = [];
            for (const n in this._apps) {
                this._apps[n].web_icon_data = menuData.children[n].web_icon_data;
            }
            this._searchableMenus = _.reduce(menuData.children, findNames, {});
            this._apps = _.map(menuData.children, function (appMenuData) {
                return {
                    actionID: parseInt(appMenuData.action.split(',')[1]),
                    menuID: appMenuData.id,
                    name: appMenuData.name,
                    xmlID: appMenuData.xmlid,
                    icon: appMenuData.web_icon_data
                };
            });
        },
        start: function(){
            this._super.apply(this, arguments);
            var self = this;
            this.$search_container = this.$(".search-container");
            this.$search_input = this.$(".search-input input");
            this.$search_results = this.$(".search-results");
            this.$theme_search = this.$('input#goolegoogle_font_val');
            this.$('.o_app_search').css('display', 'none');
            $(window).keypress( function(e){
                if($(document.activeElement).is('body', '.o_search_box')){
                    if(self.$el.find('.full > i').hasClass('fa-th') === false){
                        if((e.key == 'Delete') == false && (e.key == 'Enter') == false){
                            self.$search_input.val(self.$search_input.val() + e.key);
                            self._onAppsSearch(e);
                            self.$('.o_app_search').css('display', 'flex');
                        }
                        self.$search_input.focus();
                    }
                }
            });
            var state = $.bbq.getState();
            if((Object.keys(state).length === 1 && Object.keys(state)[0] === "cids")){
                var $navbar = this.$el.parents('.o_main_navbar');
                var $menu_tray = $navbar.find('.o_menu_brand, .o_menu_sections');
                var $toggle_btn = this.$el.find('.full > i');
                var $dashboard = this.$el.find('#apps_menu');
                if (!$dashboard || !$dashboard.length) {
                    $dashboard = $navbar.find('#apps_menu');
                }
                if (!$toggle_btn || !$toggle_btn.length) {
                    $toggle_btn = $navbar.find('.full > i');
                }

                $toggle_btn.removeClass('fa-th');
                $menu_tray.hide();
                $dashboard.removeClass('d-none');
            }
        },
        _onAppsMenuItemClicked: function(ev){
            this._super.apply(this, arguments);
            this._searchReset();
            var $navbar = this.$el.parents('.o_main_navbar');
            var $menu_tray = $navbar.find('.o_menu_brand, .o_menu_sections');
            $menu_tray.css('display','block');
        },
        _searchResultsNavigate: function (event) {
            // Find current results and active element (1st by default)
            const all = this.$search_results.find(".o-menu-search-result"),
                pre_focused = all.filter(".active") || $(all[0]);
            let offset = all.index(pre_focused),
                key = event.key;
            // Keyboard navigation only supports search results
            if (!all.length) {
                return;
            }
            // Transform tab presses in arrow presses
            if (key === "Tab") {
                event.preventDefault();
                key = event.shiftKey ? "ArrowUp" : "ArrowDown";
            }
            switch (key) {
                // Pressing enter is the same as clicking on the active element
                case "Enter":
                    pre_focused.click();
                    const $result = $(pre_focused),
                        text = $result.text().trim(),
                        data = $result.data(),
                        suffix = ~text.indexOf("/") ? "/" : "";
                    this.trigger_up("menu_clicked", {
                        action_id: data.actionId,
                        id: data.menuId,
                        previous_menu_id: data.parentId,
                    });
                    const app = _.find(this._apps, function (_app) {
                        return text.indexOf(_app.name + suffix) === 0;
                    });
                    //this._openApp(app);
                    core.bus.trigger("change_menu_section", app.menuID);
                    var $navbar = this.$el.parents('.o_main_navbar');
                    var $menu_tray = $navbar.find('.o_menu_brand, .o_menu_sections');
                    $menu_tray.css('display','block');
                    //this._onOpenCloseDashboard();
                    this._searchReset();
                    break;
                // Navigate up or down
                case "ArrowUp":
                    offset--;
                    break;
                case "ArrowDown":
                    offset++;
                    break;
                default:
                    // Other keys are useless in this event
                    return;
            }
            // Allow looping on results
            if (offset < 0) {
                offset = all.length + offset;
            } else if (offset >= all.length) {
                offset -= all.length;
            }
            // Switch active element
            const new_focused = $(all[offset]);
            pre_focused.removeClass("active");
            new_focused.addClass("active");
            this.$el.find('.o_app_search_results').scrollTo(new_focused, {
                offset: {
                    top: this.$el.find('.o_app_search_results').height() * -0.5,
                },
            });
        },
        _menuInfo: function (key) {
            const original = this._searchableMenus[key.original];
            return _.extend(
                {
                    action_id: parseInt(original.action.split(",")[1], 10),
                },
                original
            );
        },

        //--------------------------------------------------------------------------
        // Public
        //--------------------------------------------------------------------------

        /**
         * @returns {Object[]}
         */
        getApps: function () {
            return this._apps;
        },
        /**
         * Open the first app in the list of apps
         */
        openFirstApp: function () {
            var firstApp = this._apps[0];
            //this._openApp(firstApp);
        },
        _searchResultChosen: function(event){
            event.preventDefault();
            event.stopPropagation();
            const $result = $(event.currentTarget),
                text = $result.text().trim(),
                data = $result.data(),
                suffix = ~text.indexOf("/") ? "/" : "";
            this.trigger_up("menu_clicked", {
                action_id: data.actionId,
                id: data.menuId,
                previous_menu_id: data.parentId,
            });
            const app = _.find(this._apps, function (_app) {
                return text.indexOf(_app.name + suffix) === 0;
            });
            //this._openApp(app);
            core.bus.trigger("change_menu_section", app.menuID);
            var $navbar = this.$el.parents('.o_main_navbar');
            var $menu_tray = $navbar.find('.o_menu_brand, .o_menu_sections');
            $menu_tray.css('display','block');
            //this._onOpenCloseDashboard();
            this._searchReset();
        },
        _searchReset: function () {
            this.$search_container.removeClass("has-results");
            this.$search_results.empty();
            this.$search_input.val("");
            this.$('.o_app_search').css('display', 'none');
            this.$el.find('.full').css('pointer-events','all');
            this._searchApps = this._apps;
            var html = Qweb.render('AppsSearch', {apps: this._searchApps});
            this.$el.find('.o_apps_container').replaceWith(html);
        },
        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @private
         * @param {Object} app
         */
        _openApp: function (app) {
            this._setActiveApp(app);
            this.trigger_up('app_clicked', {
                action_id: app.actionID,
                menu_id: app.menuID,
            });
        },
        /**
         * @privates
         * @param {Object} app
         */
        _setActiveApp: function (app) {
            var $oldActiveApp = this.$('.o_app.active');
            $oldActiveApp.removeClass('active');
            var $newActiveApp = this.$('.o_app[data-action-id="' + app.actionID + '"]');
            $newActiveApp.addClass('active');
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        _onAppsSearch: function (ev) {
            ev.preventDefault();
            var search_txt = this.$search_input.val().trim().toLowerCase();
            if (search_txt.length) {
                this._searchApps = _.filter(this._apps, function (app) {
                    return app.name.toLowerCase().indexOf(search_txt) !== -1;
                });
            } else {
                this._searchApps = this._apps;
            }
            var html = Qweb.render('AppsSearch', {apps: this._searchApps});
            this.$el.find('.o_apps_container').replaceWith(html);
            this._search_def = new Promise((resolve) => {
                setTimeout(resolve, 50);
            });
            this._search_def.then(this._searchMenus.bind(this));
        },
        _searchMenus: function () {
            const query = this.$search_input.val();
            if (query === "") {
                this.$search_container.removeClass("has-results");
                this.$search_results.empty();
                return;
            }
            var results = fuzzy.filter(query, _.keys(this._searchableMenus), {
                pre: "<b>",
                post: "</b>",
            });
            this.$search_container.toggleClass("has-results", Boolean(results.length));
            this.$search_results.html(
                core.qweb.render("web_responsive.MenuSearchResults", {
                    results: results,
                    widget: this,
                })
            );
        },
        _onToggleClicked: function (ev) {
            ev.preventDefault();
            this.trigger_up('custom_clicked');
            this._searchReset();
            this._onOpenCloseDashboard();
        },
        _onOpenCloseDashboard: function (flag) {
            var $navbar = this.$el.parents('.o_main_navbar');
            var $menu_tray = $navbar.find('.o_menu_brand, .o_menu_sections');
            var $toggle_btn = this.$el.find('.full > i');
            var $dashboard = this.$el.find('#apps_menu');
            if (!$dashboard || !$dashboard.length) {
                $dashboard = $navbar.find('#apps_menu');
            }
            if (!$toggle_btn || !$toggle_btn.length) {
                $toggle_btn = $navbar.find('.full > i');
            }

            if (!$dashboard.hasClass('d-none')) {
                $toggle_btn.addClass('fa-th').removeClass('fa-chevron-left');
                $menu_tray.show();
                $dashboard.addClass('d-none');
            } else {
                if (!flag) {
                    $toggle_btn.addClass('fa-chevron-left').removeClass('fa-th');
                    $menu_tray.hide();
                    $dashboard.removeClass('d-none');
                    document.activeElement.blur();
                }
            }
        },
    });

    return AppsMenu;

});
