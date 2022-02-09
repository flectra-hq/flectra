flectra.define('web_flectra.sidemenu', function (require) {
    "use strict";

    var core = require('web.core');
    var session = require('web.session');
    var Widget = require('web.Widget');
    var config = require('web.config');
    var rpc = require('web.rpc');

    var activeMenu;

    var SideMenu = Widget.extend({
        init: function (menu_data) {
            this._super.apply(this, arguments);
            this.is_bound = $.Deferred();
            this._isMainMenuClick = false;
            this.isLoadflag = true;
            this.menu_data = menu_data;
        },
        start: function () {
            this._super.apply(this, arguments);
            this.$el = $('.f_launcher').find('.oe_application_menu_placeholder');
            return this.bind_menu();
        },
        do_reload: function () {
            var self = this;
            self.bind_menu();
        },
        bind_menu: function () {
            var self = this;
            this.$secondary_menus = this.$el.parents().find('.f_launcher');
            this.$secondary_menus.on('click', 'a[data-menu]', this.on_menu_click);
            this.$el.on('click', 'a[data-menu]', function (event) {
                event.preventDefault();
                var menu_id = $(event.currentTarget).data('menu');
                core.bus.trigger('change_menu_section', menu_id);
            });

            function toggleIcon(e) {
                $(e.target).prev().find('.more-less i').toggleClass('fa-chevron-down fa-chevron-right');
            }

            function toggleCollapse(e) {
                $('.f_launcher .oe_secondary_menu.show').not(e.target).collapse('toggle')
                let $activeMenu = $('.oe_main_menu_container.active');
                if ($activeMenu.length && !$activeMenu.is(activeMenu)) {
                    activeMenu = $activeMenu;
                    setTimeout(() => {
                        // $('.f_launcher').scrollTop(0);
                        let $main = $('.f_launcher');
                        let scrollTop = $activeMenu.offset().top;
                        $('.f_launcher').animate({
                            scrollTop: scrollTop - ($main.offset().top - $main.scrollTop())
                        });
                    }, 400);

                }
            }

            function updateSlideButton(e) {
                var btn = $('.o-menu-slide');
                if (window.matchMedia('(max-device-width: 1024px)').matches) {
                    btn.hide();
                } else {
                    btn.show();
                }
            }

            function closeFullMenu(e) {
                var $fLauncherContent = $('.f_launcher_content');
                if ($fLauncherContent.hasClass('mobile_views_menu_force') || window.matchMedia('(max-device-width: 1024px)').matches) {
                    $('.f_launcher_content .app_name, .more-less, .oe_secondary_menu').addClass('hidden');
                    $fLauncherContent.addClass('mobile_views_menu');
                } else {
                    $fLauncherContent.removeClass('mobile_views_menu');
                }
            }

            function openFullMenu(e) {
                var $fLauncherContent = $('.f_launcher_content');
                if ($fLauncherContent.hasClass('mobile_views_menu_force') || window.matchMedia('(max-device-width: 1024px)').matches) {
                    $('.f_launcher_content .app_name, .more-less, .oe_secondary_menu').removeClass('hidden');
                    $fLauncherContent.removeClass('mobile_views_menu');
                } else {
                }
            }

            function resizeFullMenu(e) {
                var $fLauncherContent = $('.f_launcher_content');
                if ($fLauncherContent.hasClass('mobile_views_menu_force') || window.matchMedia('(max-device-width: 1024px)').matches) {
                    $('.f_launcher_content .app_name, .more-less, .oe_secondary_menu').addClass('hidden');
                    $fLauncherContent.addClass('mobile_views_menu');
                } else {
                    $('.f_launcher_content .app_name, .more-less, .oe_secondary_menu').removeClass('hidden');
                    $fLauncherContent.removeClass('mobile_views_menu');
                }
            }

            $(window).on('resize', resizeFullMenu);
            this.$secondary_menus.find('[data-toggle="tooltip"]').tooltip({
                trigger: "hover",
                delay: 500
            });

            this.$secondary_menus.find('#menu_launcher')
                .on('hidden.bs.collapse', toggleIcon)
                .on('shown.bs.collapse', toggleIcon)
                .on('shown.bs.collapse', toggleCollapse);

            // Hide menu on mouseleave and show menu on mouseover
            $('.f_launcher_content')
                .on('mouseleave', closeFullMenu)
                .on('mouseover', openFullMenu);

            // Enable touch gestures for mobile devices
            $(".f_launcher_content").swipe({
                swipeLeft: closeFullMenu,
                swipeRight: openFullMenu,
            });

            // Hide elements on init as default
            if ($('.f_launcher_content').hasClass('mobile_views_menu')) {
                closeFullMenu();
            }

            // Hide second level submenus
            this.$secondary_menus.find('.oe_menu_toggler').siblings('.oe_secondary_submenu').addClass('o_hidden');
            if (self.current_menu) {
                self.open_menu(self.current_menu);
            }
            updateSlideButton();
            this.is_bound.resolve();
        },

        /**
         * Highlights the active menu record
         * collapse the menus and set the arrows in right direction.
         *
         * @param {Number} action id of the menu entry to select
         */
        set_menu: function (app) {
            if (!app.actionID || !app.menuID) {
                return;
            }
            var $main_menu = $('.f_launcher_content');
            var $clicked_menu = $main_menu.find('a[data-menu=' + app.menuID + ']');
            var $main_menu_container = $clicked_menu.closest('li.panel');
            var $main_menu_chevron = $main_menu_container.find('i');
            var $secondary_menu = $main_menu_container.find('.oe_secondary_menu');

            $secondary_menu.collapse('toggle');
            $clicked_menu.closest('li:not(".panel")').addClass('active');

            /** If triggered a menu change from APP DASHBOARD use actionID instead. **/
            if ($clicked_menu.length > 1) {
                var $active_menu = $main_menu.find('a.oe_menu_leaf[data-action-id=' + app.actionID + ']').closest('li:not(".panel")');
                $active_menu.addClass('active');
            } else {
                var $active_menu = $main_menu.find('a.oe_menu_leaf[data-action-id=' + app.actionID + ']').closest('.oe_secondary_menu_section');
                $active_menu.addClass('active');
            }
            $clicked_menu.closest('.panel').addClass('active')

            /** Open secondary submenus. **/
            var $secondary_menu_parents = $clicked_menu.parents('.oe_secondary_submenu');
            var $secondary_menu_toggler = $clicked_menu.closest('li:not(".active")').children('.oe_menu_toggler')
            if ($secondary_menu_parents.length > 1) {
                setTimeout(function () {
                    $secondary_menu_toggler.addClass('oe_menu_opened');
                    $clicked_menu.closest('ul').removeClass('o_hidden');
                }, 2000);
            }
        },

        /**
         * Resets all highlighted menu entries and
         * collapse all opened menu items.
         */
        reset_menu: function () {
            var $main_menu = $('.f_launcher_content');
            var $main_menu_container = $main_menu.find('.collapse.show');
            var $active_entry = $main_menu.find('li.active');
            var $chevron_down = $main_menu.find('.fa-chevron-down');
            var $secondary_menu_link = $main_menu.find('.oe_menu_opened');
            var $secondary_menu_container = $main_menu.find('.oe_secondary_menu > .oe_secondary_submenu > li > .oe_secondary_submenu')

            $main_menu_container.removeClass('show');
            $active_entry.removeClass('active');
            $chevron_down.removeClass('fa-chevron-down').addClass('fa-chevron-right');
            $secondary_menu_link.removeClass('oe_menu_opened');
            $secondary_menu_container.addClass('o_hidden');
        },

        /**
         * Opens a given menu by id, as if a user had browsed to that menu by hand
         * except does not trigger any event on the way
         *
         * @param {Number} id database id of the terminal menu to select
         */
        open_menu: function (id) {
            var self = this;
            this.current_menu = id;
            session.active_id = id;
            var $clicked_menu, $sub_menu, $main_menu;
            $clicked_menu = this.$el.add(this.$secondary_menus).find('a[data-menu=' + id + ']');
            this.trigger('open_menu', id, $clicked_menu);

            if (this.$secondary_menus.has($clicked_menu).length) {
                $sub_menu = $clicked_menu.parents('.oe_secondary_menu');
                $main_menu = this.$el.find('a[data-menu=' + $sub_menu.data('menu-parent') + ']');
            } else {
                $sub_menu = this.$secondary_menus.find('.oe_secondary_menu[data-menu-parent=' + $clicked_menu.attr('data-menu') + ']');
                $main_menu = $clicked_menu;
            }

            // Activate current main menu
            this.$el.find('.active').removeClass('active');
            $main_menu.parent().addClass('active');

            var isNotMainMenu = $clicked_menu.hasClass('oe_main_menu');
            if (this._isMainMenuClick || this.isLoadflag && isNotMainMenu) {
                var href_id = $sub_menu.attr('id');
                if (href_id && $sub_menu.attr('class').indexOf('in') === -1) {
                    this.$secondary_menus.find("a[href='#" + href_id + "']").trigger('click');
                    this.$secondary_menus.find("a[href='#" + href_id + " i']")
                        .addClass('fa-chevron-right')
                        .removeClass('fa-chevron-down');
                } else {
                    $clicked_menu.parents('li.panel').find('.oe_main_menu_container .more-less a').trigger('click');
                    this.$secondary_menus.find("a[href='#" + href_id + " i']")
                        .addClass('fa-chevron-down')
                        .removeClass('fa-chevron-right');
                }
            }

            // Hide/Show the leftbar menu depending of the presence of sub-items
            this.$secondary_menus.toggleClass('o_hidden', !$sub_menu.children().length);

            // Activate current menu item and show parents
            this.$secondary_menus.find('.active').removeClass('active');
            if ($main_menu !== $clicked_menu) {
                $clicked_menu.parents().removeClass('o_hidden');
                if ($clicked_menu.is('.oe_menu_toggler')) {
                    $clicked_menu.toggleClass('oe_menu_opened').siblings('.oe_secondary_submenu:first').toggleClass('o_hidden');
                } else {
                    $clicked_menu.parent().addClass('active');
                }
                this.$secondary_menus.find('.oe_main_menu_container').removeClass('active');
                $clicked_menu.parents('li.panel').find('.oe_main_menu_container').addClass('active');
            }
            $clicked_menu.closest('.panel').addClass('active')
            // add a tooltip to cropped menu items
            this.$secondary_menus.find('.oe_secondary_submenu li a span').each(function () {
                $(this).tooltip(this.scrollWidth > this.clientWidth ? {title: $(this).text().trim(), placement: 'right'} : 'dispose');
            });
            this.isLoadflag = false;
        },
        /**
         * Call open_menu on a menu_item that matches the action_id
         *
         * If `menuID` is a match on this action, open this menu_item.
         * Otherwise open the first menu_item that matches the action_id.
         *
         * @param {Number} id the action_id to match
         * @param {Number} [menuID] a menu ID that may match with provided action
         */
        open_action: function (id, menuID) {
            var $menu = this.$el.add(this.$secondary_menus).find('a[data-action-id="' + id + '"]');
            if (!(menuID && $menu.filter("[data-menu='" + menuID + "']").length)) {
                // menuID doesn't match action, so pick first menu_item
                menuID = $menu.data('menu');
            }
            if (menuID) {
                this.open_menu(menuID);
            }
        },
        /**
         * Process a click on a menu item
         *
         * @param {Number} id the menu_id
         */
        menu_click: function (id) {
            if (!id) {
                return;
            }

            // find back the menuitem in dom to get the action
            var $item = this.$el.find('a[data-menu=' + id + ']');
            if (!$item.length) {
                $item = this.$secondary_menus.find('a[data-menu=' + id + ']');
            }
            var action_id = $item.data('action-id');
            // If first level menu doesnt have action trigger first leaf
            if (!action_id) {
                if (this.$el.has($item).length) {
                    var $sub_menu = this.$secondary_menus.find('.oe_secondary_menu[data-menu-parent=' + id + ']');
                    var $items = $sub_menu.find('a[data-action-id]').filter('[data-action-id!=""]');
                    if ($items.length) {
                        action_id = $items.data('action-id');
                        id = $items.data('menu');
                    }
                }
            }
            if (action_id) {
                this.trigger_up('app_clicked', {
                    action_id: action_id,
                    menu_id: id,
                });
            } else {
                console.log('Menu no action found web test 04 will fail');
            }
            this._isActionId = action_id === undefined ? false : true;
            this.open_menu(id);
        },

        /**
         * Change the current top menu
         *
         * @param {int} [menu_id] the top menu id
         */
        on_change_top_menu: function (menu_id) {
            var self = this;
            this.menu_click(menu_id);
        },
        on_menu_click: function (ev) {
            ev.preventDefault();
            if (!parseInt($(ev.currentTarget).data('menu'))) return;
            this._isMainMenuClick = $(ev.currentTarget).attr('class').indexOf('oe_main_menu') !== -1 ? true : false;
            this.menu_click($(ev.currentTarget).data('menu'));
        },
    });

    return SideMenu;
});

flectra.define('web_flectra.sidemenu.AppsMenu', function (require) {
    "use strict";
    var AppsMenu = require('web.AppsMenu');
    var SideMenu = require('web_flectra.sidemenu');
    AppsMenu.include({
        _openApp: function (app) {
            this.sidemenu = new SideMenu(this);
            this.sidemenu.reset_menu();
            this.sidemenu.set_menu(app);
            return this._super.apply(this, arguments);
        },
    });
});

flectra.define('web_flectra.sidemenu.webclient', function (require) {
    "use strict";
    var Menu = require('web.Menu');
    var WebClient = require('web.WebClient');
    var SideMenu = require('web_flectra.sidemenu');

    var config = require('web.config');
    var data_manager = require('web.data_manager');
    var rpc = require('web.rpc');
    var session = require('web.session');

    WebClient.include({
        start: function () {
            var self = this;
            this._super();
            return rpc.query({
                model: 'res.company', method: 'read',
                args: [[session.company_id], ['theme_menu_style']]
            }).then(function (res) {
                if (res[0].theme_menu_style == 'sidemenu') {
                    $('.o-menu-toggle, .o_menu_sections').remove();
                }
            });
        },

        show_application: function () {
            var state = $.bbq.getState(true);
            var app = {
                'menuID': state.menu_id,
                'actionID': state.action
            }
            this.sidemenu = new SideMenu(this);
            this.sidemenu.appendTo(this.$el.parents().find('.oe_application_menu_placeholder'));
            this.sidemenu.on('menu_click', this, this.on_menu_action);
            this.sidemenu.set_menu(app);

            //this.bind_hashchange();
            return this._super.apply(this, arguments);
        },

        bind_hashchange: function () {
            var self = this;
            $(window).bind('hashchange', function (e) {
                self.on_hashchange(e);
            });
            var didHashChanged = false;
            $(window).one('hashchange', function () {
                didHashChanged = true;
            });

            var state = $.bbq.getState(true);
            if (_.isEmpty(state) || state.action === "login") {
                self.sidemenu.is_bound.done(function () {
                    self._rpc({
                        model: 'res.users',
                        method: 'read',
                        args: [[session.uid], ['action_id']],
                    })
                        .done(function (result) {
                            if (didHashChanged) {
                                return;
                            }
                            var data = result[0];
                            if (data.action_id) {
                                self.action_manager.doAction(data.action_id[0]);
                                self.sidemenu.open_action(data.action_id[0]);
                            } else {
                                var first_menu_id = self.sidemenu.$el.find("a:first").data("menu");
                                if (first_menu_id) {
                                    self.sidemenu.menu_click(first_menu_id);
                                }
                            }
                        });
                });
            } else {
                $(window).trigger('hashchange');
            }
        },

        on_hashchange: function (event) {
            this._super.apply(this, event);
            if (this._ignore_hashchange) {
                this._ignore_hashchange = false;
                return;
            }
            var self = this;
            this.clear_uncommitted_changes().then(function () {
                var stringstate = $.bbq.getState(false);
                var state = $.bbq.getState(true);
                if (!_.isEqual(self._current_state, stringstate)) {
                    if (!state.action && state.menu_id) {
                        self.sidemenu.is_bound.done(function () {
                            self.sidemenu.menu_click(state.menu_id);
                        });
                    } else if (state.menu_id) {
                        var action = self.action_manager.getCurrentAction();
                        if (action) {
                            self.sidemenu.open_action(action.id, state.menu_id);
                        }
                    }
                }
                self._current_state = stringstate;
            }, function () {
                if (event) {
                    self._ignore_hashchange = true;
                    window.location = event.originalEvent.oldURL;
                }
            });
        },

        on_menu_action: function (options) {
            var self = this;
            return this.menu_dp.add(data_manager.load_action(options.action_id))
                .then(function (result) {
                    return self.action_mutex.exec(function () {
                        var completed = $.Deferred();
                        $.when(self.action_manager.do_action(result, {
                            clear_breadcrumbs: true,
                            action_menu_id: options.id,
                        })).fail(function () {
                            self.sidemenu.open_menu(options.previous_menu_id);
                        }).always(function () {
                            completed.resolve();
                        });
                        setTimeout(function () {
                            completed.resolve();
                        }, 2000);
                        // We block the menu when clicking on an element until the action has correctly finished
                        // loading. If something crash, there is a 2 seconds timeout before it's unblocked.
                        return completed;
                    });
                });
        },
    });
});
