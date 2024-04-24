/** @flectra-module alias=web.home.sidebar **/

import { onMounted, Component, xml } from "@flectra/owl";
var activeMenu;

export class SideBar extends Component{
    static template = xml`<div></div>`
    setup(){
        this.is_bound = $.Deferred();
        this._isMainMenuClick = false;
        this.isLoadflag = true;
        this.$el = $('.f_launcher').find('.oe_application_menu_placeholder');
        this.bind_menus();

        onMounted(() => {
            this.reset_menu();
            this.set_menu(this.props.menu)
        })
    }

    bind_menus() {
        var self = this;
        this.$secondary_menus = this.$el.parents().find('.f_launcher');
        const on_menu_click = this.on_menu_click.bind(this);
        this.$secondary_menus.on('click', 'a[data-menu]', on_menu_click);
        this.$el.on('click', 'a[data-menu]', (event) => {
            event.preventDefault();
            var menu_id = $(event.currentTarget).data('menu');
            this.env.bus.trigger('change_menu_section', menu_id);
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
    }

    set_menu(app) {
        if (!app.actionID || !app.menuID) {
            return;
        }
        var $main_menu = $('.f_launcher_content');
        var $clicked_menu = $main_menu.find('a[data-action-id=' + app.actionID + ']');
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
    }

    reset_menu() {
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
    }

    open_menu(id) {
        var self = this;
        this.current_menu = id;
        var $clicked_menu, $sub_menu, $main_menu;
        $clicked_menu = this.$el.add(this.$secondary_menus).find('a[data-menu=' + id + ']');
        //this.trigger('open_menu', id, $clicked_menu);

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
    }

    open_action (id, menuID) {
        var $menu = this.$el.add(this.$secondary_menus).find('a[data-action-id="' + id + '"]');
        if (!(menuID && $menu.filter("[data-menu='" + menuID + "']").length)) {
            // menuID doesn't match action, so pick first menu_item
            menuID = $menu.data('menu');
        }
        if (menuID) {
            this.open_menu(menuID);
        }
    }

    menu_click(id, force=false) {
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
        if(!force){
            if (action_id) {
                this.env.bus.trigger('app_clicked', {
                    action_id: action_id,
                    menu_id: id,
                });
            } else {
                console.log('Menu no action found web test 04 will fail');
            }
        }
        this._isActionId = action_id === undefined ? false : true;
        this.open_menu(id);
    }

    on_change_top_menu (menu_id) {
        var self = this;
        this.menu_click(menu_id);
    }

    on_menu_click(ev) {
        ev.preventDefault();
        if (!parseInt($(ev.currentTarget).data('menu'))) return;
        this._isMainMenuClick = $(ev.currentTarget).attr('class').indexOf('oe_main_menu') !== -1 ? true : false;
        this.menu_click($(ev.currentTarget).data('menu'));
    }
}
