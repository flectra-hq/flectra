flectra.define('web.Bookmark', function (require) {
    "use strict";

    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');
    var rpc = require('web.rpc');
    var AppsLauncher = require('web.AppsLauncher');

    var Bookmark = Widget.extend({
        template: "Bookmark.Menu",
        events: {
            "click": "on_click",
        },
        init: function () {
            this._super.apply(this, arguments);
        },
        start: function () {
            this.AppsLauncher = new AppsLauncher(this);
            return this._super();
        },
        getMenuRecord: function () {
            var action_id = $.bbq.getState().action;
            return rpc.query({
                model: 'menu.bookmark',
                method: 'bookmark',
                args: ['', action_id]
            });
        },
        on_click: function (ev) {
            ev.preventDefault();
            var self = this;
            this.getMenuRecord().then(function (rec) {
                if (rec.bookmark) {
                    self.$el.find('> a').addClass('active');
                } else {
                    self.$el.find('> a').removeClass('active');
                }
                self.AppsLauncher.render();
            });
        }
    });

    SystrayMenu.Items.push(Bookmark);

    return {
        Bookmark: Bookmark,
    };
});
