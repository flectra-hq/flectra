flectra.define('web_flectra.systray.ActivityMenu', function (require) {
    "use strict";

    var ActivityMenu = require('mail.systray.ActivityMenu');

    return ActivityMenu.include({
        init: function (parent) {
            this._super(parent);
            this._closeDashboard = parent.getParent()._appsMenu._onOpenCloseDashboard;
        },
        _onActivityFilterClick: function (ev) {
            this._super.apply(this, arguments);
            this._closeDashboard(true);
        }
    });
});


flectra.define('web_flectra.systray.MessagingMenu', function (require) {
    "use strict";

    var MessagingMenu = require('mail.systray.MessagingMenu');

    return MessagingMenu.include({
        init: function (parent) {
            this._super(parent);
            this._closeDashboard = parent.getParent()._appsMenu._onOpenCloseDashboard;
        },
        _onClickPreview: function (ev) {
            this._super.apply(this, arguments);
            this._closeDashboard(true);
        },
    });
});
