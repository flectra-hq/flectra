flectra.define('web.BackendThemeCustomizer', function (require) {
"use strict";

var SystrayMenu = require('web.SystrayMenu');
var Widget = require('web.Widget');
var Theme = require('web.CustomizeSwitcher');
var session = require('web.session');

/**
 * Menu item appended in the systray part of the navbar, redirects to the Inbox in Discuss
 * Also displays the needaction counter (= Inbox counter)
 */

var CustomizeMenu = Widget.extend({
    template: 'web.customize_menu',
    start: function () {
        this._super.apply(this, arguments);
        this.theme = new Theme();
        this.theme.appendTo("#theme_customize_backend ul");
    },
});

if (session.is_superuser) {
    SystrayMenu.Items.push(CustomizeMenu);
}

});
