flectra.define('web_flectra.Menu', function (require) {
    "use strict";

    var Menu = require('web.Menu');
    var config = require('web.config');

    return Menu.include({
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                if(config.device.isMobile == true){
                    self.$section_placeholder.addClass('mobile-view');
                    self.$menu_brand_placeholder.addClass('mobile-view');
                }

                self.$('.o_menu_systray').find('.dropdown-menu').on('click', function (ev) {
                    self._appsMenu._onOpenCloseDashboard(true);
                });
            });
        },
    });
});
