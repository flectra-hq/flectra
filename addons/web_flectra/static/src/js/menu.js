flectra.define('web_flectra.Menu', function (require) {
    "use strict";

    var Menu = require('web.Menu');
    var SlideMenu = require('web_flectra.sidemenu');
    var config = require('web.config');

    return Menu.include({
        updateSidebar: function () {
            var btn = $('.o-menu-slide');
            var $fLauncherContent = $('.f_launcher_content');
            if (!$fLauncherContent.length || window.matchMedia('(max-device-width: 1024px)').matches) {
                btn.hide();
                $fLauncherContent.removeClass('mobile_views_menu_force');
            } else {
                btn.show();
            }
            if ($fLauncherContent.hasClass('mobile_views_menu_force') || window.matchMedia('(max-device-width: 1024px)').matches) {
                $('.f_launcher_content .app_name, .more-less, .oe_secondary_menu').addClass('hidden');
                $fLauncherContent.addClass('mobile_views_menu');
                $('.o_action_manager').addClass('force_mobile');
            } else {
                $('.f_launcher_content .app_name, .more-less, .oe_secondary_menu').removeClass('hidden');
                $fLauncherContent.removeClass('mobile_views_menu');
                $('.o_action_manager').removeClass('force_mobile');
            }
        }, start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                if (config.device.isMobile == true) {
                    self.$section_placeholder.addClass('mobile-view');
                    self.$menu_brand_placeholder.addClass('mobile-view');
                }

                self.$('.o_menu_systray').find('.dropdown-menu').on('click', function (ev) {
                    self._appsMenu._onOpenCloseDashboard(true);
                });

                $('.o-menu-slide').on('click', function (ev) {
                    ev.preventDefault();
                    $('.o-menu-slide > i').toggleClass('fa-compress fa-expand');
                    $('.f_launcher_content').toggleClass('mobile_views_menu_force');
                    self.updateSidebar();
                });
                $(window).on('resize', function (ev) {
                    self.updateSidebar();
                });
            });
        },
    });
});
