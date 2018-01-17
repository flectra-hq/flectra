flectra.define('web.UserLogout', function (require) {
"use strict";

var SystrayMenu = require('web.SystrayMenu');
var Widget = require('web.Widget');

var UserLogout = Widget.extend({
    template:"UserLogout.Action",
    events: {
        "click": "on_click",
    },
    init: function () {
        this._super.apply(this, arguments);
    },
    start: function () {
        return this._super();
    },
    on_click:function (e) {
        this.trigger_up('clear_uncommitted_changes', {
            callback: this.do_action.bind(this, 'logout'),
        });
    }
});

SystrayMenu.Items.push(UserLogout);

return {
    UserLogout: UserLogout,
};
});
