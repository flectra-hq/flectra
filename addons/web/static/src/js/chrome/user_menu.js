flectra.define('web.UserMenu', function (require) {
"use strict";

/**
 * This widget is appended by the webclient to the right of the navbar.
 * It displays the avatar and the name of the logged user (and optionally the
 * db name, in debug mode).
 * If clicked, it opens a dropdown allowing the user to perform actions like
 * editing its preferences, accessing the documentation, logging out...
 */

var framework = require('web.framework');
var Widget = require('web.Widget');


var UserMenu = Widget.extend({
    template: 'UserMenu',

    /**
     * @override
     * @returns {Deferred}
     */
    start: function () {
        var self = this;
        var session = this.getSession();
        this.$el.on('click', 'li a[data-menu]', function (ev) {
            ev.preventDefault();
            var menu = $(this).data('menu');
            self['_onMenu' + menu.charAt(0).toUpperCase() + menu.slice(1)]();
        });
        return this._super.apply(this, arguments).then(function () {
            var $avatar = self.$('.oe_topbar_avatar');
            if (!session.uid) {
                $avatar.attr('src', $avatar.data('default-src'));
                return $.when();
            }
            var topbar_name = session.name;
            if (session.debug) {
                topbar_name = _.str.sprintf("%s (%s)", topbar_name, session.db);
            }
            self.$('.oe_topbar_name').text(topbar_name);
            var avatar_src = session.url('/web/image', {
                model:'res.users',
                field: 'image_small',
                id: session.uid,
            });
            $avatar.attr('src', avatar_src);
        });
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onMenuAccount: function () {
        var self = this;
        this.trigger_up('clear_uncommitted_changes', {
            callback: function () {
                self._rpc({route: '/web/session/account'})
                    .then(function (url) {
                        framework.redirect(url);
                    })
                    .fail(function (result, ev){
                        ev.preventDefault();
                        framework.redirect('https://flectrahq.com/accounting');
                    });
            },
        });
    },
    /**
     * @private
     */
    _onMenuDocumentation: function () {
        window.open('https://userdoc.flectrahq.com/index.html', '_blank');
    },
    /**
     * @private
     */
    _onMenuLogout: function () {
        this.trigger_up('clear_uncommitted_changes', {
            callback: this.do_action.bind(this, 'logout'),
        });
    },
    /**
     * @private
     */
    _onMenuSettings: function () {
        var self = this;
        var session = this.getSession();
        this.trigger_up('clear_uncommitted_changes', {
            callback: function () {
                self._rpc({
                        route: "/web/action/load",
                        params: {
                            action_id: "base.action_res_users_my",
                        },
                    })
                    .done(function (result) {
                        result.res_id = session.uid;
                        self.do_action(result);
                    });
            },
        });
    },
    /**
     * @private
     */
    _onMenuSupport: function () {
        window.open('https://www.flectrahq.com/buy', '_blank');
    },
});

return UserMenu;

});

flectra.define('web.UserProfile', function (require) {
"use strict";

var framework = require('web.framework');
var Widget = require('web.Widget');

var UserProfile = Widget.extend({
    template: 'UserProfile',

    /**
     * @override
     * @returns {Deferred}
     */
    start: function () {
        var self = this;
        var session = this.getSession();
        this.$el.on('click', 'li a[data-menu]', function (ev) {
            ev.preventDefault();
            var menu = $(this).data('menu');
            self['_onMenu' + menu.charAt(0).toUpperCase() + menu.slice(1)]();
        });
        return this._super.apply(this, arguments).then(function () {
            var $avatar = self.$('.profile_pic img');
            var $lang_logo = self.$('img.profile_lang');
            if (!session.uid) {
                $avatar.attr('src', $avatar.data('default-src'));
                $lang_logo.attr('src', $lang_logo.data('default-src'));
                return $.when();
            }
            self.$('.profile_name').text(session.name);
            if (session.debug) {
                self.$el.addClass('debug')
                self.$('.db_name').text('(' + session.db + ')');
            }
            var avatar_src = session.url('/web/image', {
                model:'res.users',
                field: 'image_small',
                id: session.uid,
            });
            self._rpc({
                model: 'res.lang',
                method: 'search_read',
                args: [[["code", "=", session.user_context.lang]], ['name', 'direction']],
            }).then(function(lang_data){
                if (lang_data.length) {
                    var img_src = session.url('/web/image', {
                        model: 'res.lang',
                        field: 'image',
                        id: lang_data[0].id,
                    });
                    $lang_logo.attr('title', lang_data[0].name).attr('src', img_src).attr('data-lang-dir', lang_data[0].direction);

                    // Web RTL(Right to Left) Snippet
                    if (lang_data[0].direction == 'rtl') {
                        var head = document.getElementsByTagName('head')[0];

                        // BootStrap RTL CSS
                        var link = document.createElement('link');
                        link.rel = 'stylesheet';
                        link.type = 'text/css';
                        link.href = '/web/static/lib/rtl/bootstrap-rtl.min.css';
                        head.appendChild(link);

                        // Flectra RTL Custom CSS
                        var link1 = document.createElement('link');
                        link1.rel = 'stylesheet';
                        link1.type = 'text/css';
                        link1.href = '/web/static/lib/rtl/flectra-rtl-custom.css';
                        head.appendChild(link1);
                    }
                }
            });
            $avatar.attr('src', avatar_src);
        });
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onMenuAccount: function () {
        var self = this;
        this.trigger_up('clear_uncommitted_changes', {
            callback: function () {
                self._rpc({route: '/web/session/account'})
                    .then(function (url) {
                        framework.redirect(url);
                    })
                    .fail(function (result, ev){
                        ev.preventDefault();
                        framework.redirect('https://accounts.flectrahq.com/account');
                    });
            },
        });
    },
    /**
     * @private
     */
    _onMenuDocumentation: function () {
        window.open('https://www.flectrahq.com/documentation/user', '_blank');
    },
    /**
     * @private
     */
    _onMenuLogout: function () {
        this.trigger_up('clear_uncommitted_changes', {
            callback: this.do_action.bind(this, 'logout'),
        });
    },
    /**
     * @private
     */
    _onMenuSettings: function () {
        var self = this;
        var session = this.getSession();
        this.trigger_up('clear_uncommitted_changes', {
            callback: function () {
                self._rpc({
                        route: "/web/action/load",
                        params: {
                            action_id: "base.action_res_users_my",
                        },
                    })
                    .done(function (result) {
                        result.res_id = session.uid;
                        self.do_action(result);
                    });
            },
        });
    },
    /**
     * @private
     */
    _onMenuSupport: function () {
        window.open('https://www.flectrahq.com/buy', '_blank');
    },
});

return UserProfile;

});
