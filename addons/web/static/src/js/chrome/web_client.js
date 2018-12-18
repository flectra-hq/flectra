flectra.define('web.WebClient', function (require) {
"use strict";

var AbstractWebClient = require('web.AbstractWebClient');
var core = require('web.core');
var data_manager = require('web.data_manager');
var framework = require('web.framework');
var Menu = require('web.Menu');
var session = require('web.session');
var SystrayMenu = require('web.SystrayMenu');
var UserMenu = require('web.UserMenu');
var UserProfile = require('web.UserProfile');
var config = require('web.config');
var rpc = require('web.rpc');
var qweb = core.qweb;
var Dialog = require('FlectraLicensing.DialogRegisterContract');

return AbstractWebClient.extend({
    events: _.extend({}, AbstractWebClient.prototype.events, {
        'click .oe_logo_edit_admin': 'logo_edit',
        'click .oe_logo img': function(ev) {
            ev.preventDefault();
            return this.clear_uncommitted_changes().then(function() {
                framework.redirect("/web" + (core.debug ? "?debug" : ""));
            });
        },
    }),
    show_application: function() {
        var self = this;

        // Allow to call `on_attach_callback` and `on_detach_callback` when needed
        this.action_manager.is_in_DOM = true;

        this.toggle_bars(true);
        this.set_title();
        this.update_logo();

        // Menu is rendered server-side thus we don't want the widget to create any dom
        this.menu = new Menu(this);
        this.menu.setElement(this.$el.parents().find('.oe_application_menu_placeholder'));
        this.menu.on('menu_click', this, this.on_menu_action);
        if (config.device.size_class < config.device.SIZES.SM) {
            this.menu.is_menus_lite_mode = false;
        }else{
            this.menu.is_menus_lite_mode = 'menus_lite_mode' in window.sessionStorage ? true : false;
        }

        // Create the user menu (rendered client-side)
        this.user_menu = new UserMenu(this);
        this.user_profile = new UserProfile(this);
        var $user_menu_placeholder = $('body').find('.oe_user_menu_placeholder').show();
        var $oe_application_menu_placeholder = $('body').find('.f_launcher_content');
        var user_menu_loaded = this.user_menu.appendTo($user_menu_placeholder);
        this.user_profile.prependTo($oe_application_menu_placeholder);

        // Create the systray menu (rendered server-side)
        this.systray_menu = new SystrayMenu(this);
        this.systray_menu.setElement(this.$el.parents().find('.oe_systray'));
        var systray_menu_loaded = this.systray_menu.start();

        if ((session.expiration_date && session.expiration_reason === 'contract_expire') || !session['contract_validation']) {
            this.validate_days_of_contract();
        }
        // Start the menu once both systray and user menus are rendered
        // to prevent overflows while loading
        return $.when(systray_menu_loaded, user_menu_loaded).then(function() {
            self.menu.start();
            self.bind_hashchange();
        });

    },
    toggle_bars: function(value) {
        this.$('tr:has(td.navbar),.oe_leftbar').toggle(value);
    },
    update_logo: function(reload) {
        var company = session.company_id;
        var img = session.url('/web/binary/company_logo' + '?db=' + session.db + (company ? '&company=' + company : ''));
        this.$('.o_sub_menu_logo img').attr('src', '').attr('src', img + (reload ? "&t=" + Date.now() : ''));
        this.$('.oe_logo_edit').toggleClass('oe_logo_edit_admin', session.is_superuser);
    },
    logo_edit: function(ev) {
        var self = this;
        ev.preventDefault();
        this._rpc({
                model: 'res.users',
                method: 'read',
                args: [[session.uid], ['company_id']],
            })
            .then(function(data) {
                self._rpc({
                        route: '/web/action/load',
                        params: { action_id: 'base.action_res_company_form' },
                    })
                    .done(function(result) {
                        result.res_id = data[0].company_id[0];
                        result.target = "new";
                        result.views = [[false, 'form']];
                        result.flags = {
                            action_buttons: true,
                            headless: true,
                        };
                        self.action_manager.do_action(result, {
                            on_close: self.update_logo.bind(self, true),
                        });
                    });
            });
        return false;
    },
    bind_hashchange: function() {
        var self = this;
        $(window).bind('hashchange', this.on_hashchange);
        var didHashChanged = false;
        $(window).one('hashchange', function () {
            didHashChanged = true;
        });

        var state = $.bbq.getState(true);
        if (_.isEmpty(state) || state.action === "login") {
            self.menu.is_bound.done(function() {
                self._rpc({
                        model: 'res.users',
                        method: 'read',
                        args: [[session.uid], ['action_id']],
                    })
                    .done(function(result) {
                        if (didHashChanged) {
                            return;
                        }
                        var data = result[0];
                        if(data.action_id) {
                            self.action_manager.do_action(data.action_id[0]);
                            self.menu.open_action(data.action_id[0]);
                        } else {
                            var first_menu_id = self.menu.$el.find("a:first").data("menu");
                            if(first_menu_id) {
                                self.menu.menu_click(first_menu_id);
                            }
                        }
                    });
            });
        } else {
            $(window).trigger('hashchange');
        }
    },
    on_hashchange: function(event) {
        if (this._ignore_hashchange) {
            this._ignore_hashchange = false;
            return;
        }

        var self = this;
        this.clear_uncommitted_changes().then(function () {
            var stringstate = event.getState(false);
            if (!_.isEqual(self._current_state, stringstate)) {
                var state = event.getState(true);
                if(!state.action && state.menu_id) {
                    self.menu.is_bound.done(function() {
                        self.menu.menu_click(state.menu_id);
                    });
                } else {
                    state._push_me = false;  // no need to push state back...
                    self.action_manager.do_load_state(state, !!self._current_state).then(function () {
                        var action = self.action_manager.get_inner_action();
                        if (action) {
                            self.menu.open_action(action.action_descr.id, state.menu_id);
                        }
                    });
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
    on_menu_action: function(options) {
        var self = this;
        return this.menu_dm.add(data_manager.load_action(options.action_id))
            .then(function (result) {
                return self.action_mutex.exec(function() {
                    var completed = $.Deferred();
                    $.when(self.action_manager.do_action(result, {
                        clear_breadcrumbs: true,
                        action_menu_id: options.id,
                    })).fail(function() {
                        self.menu.open_menu(options.previous_menu_id);
                    }).always(function() {
                        completed.resolve();
                    });
                    setTimeout(function() {
                        completed.resolve();
                    }, 2000);
                    // We block the menu when clicking on an element until the action has correctly finished
                    // loading. If something crash, there is a 2 seconds timeout before it's unblocked.
                    return completed;
                });
            });
    },
    toggle_fullscreen: function(fullscreen) {
        this._super(fullscreen);
        if (!fullscreen) {
            this.menu.reflow();
        }
    },
    validate_days_of_contract: function () {
        var today = new moment();
        var dbexpiration_date = new moment(session.expiration_date);
        var duration = moment.duration(dbexpiration_date.diff(today));
        var params = {
            'difference': Math.round(duration.asDays()),
            'reason': session.expiration_reason,
        };
        this.show_contract_registration(params);
    },

    show_contract_registration: function (params) {
        var self = this;
        var bg_color = params.difference <= 10 ? '#e55e50' : '#f3be5d';
        var difference = params.difference || 0;
        if (difference <= 15 || !session['contract_validation']) {
            if (difference > 15){
                difference = 0;
                bg_color = '#e55e50';
            }
            var message = 'Register your contract, only ' + difference  + ' days left';
            var $panel = $(qweb.render('FlectraLicense.contract_expire_panel', {
                'difference': params.difference,
                'message': message,
                'background': bg_color
            }));
            $('nav').after($panel);
            if (difference <= 0) {
                return self.contract_expired()
            }
            $panel.find('#register_contract').bind('click', self.register_contract);
        }
    },
    register_contract: function () {
        var self = this;
        var dialog = new Dialog(self).open();
        dialog.on('get_key', self, function (key) {
            session.get_file({
                url: '/flectra/licensing',
                data: {
                    'binary': key['binary'],
                    'type': key['type'],
                    'contract_id': key['key']
                },
                error: function (res) {
                    var btn = [{
                        text: core._t("Cancel"),
                        close: true,
                    }];
                    if (res.success) {
                        btn.unshift({
                            text: core._t('Refresh'),
                            classes: "btn-primary",
                            click: function () { window.location.reload(); },
                            close: true
                        })
                    }
                    new require('web.Dialog').alert(null, '', {
                        $content: $('<div/>').html(res['message']),
                        buttons: btn
                    });
                }
            });
        });
    },
    contract_expired: function () {
        var self = this;
        var $message = $('#expiration-message').parent();
        var $clone = $message.clone();
        $clone.find('#contract-message').text('Contract Expired !!!').addClass('contract-block');
        $clone.find('button.close').remove();
        $message.hide();
        $clone.find('div#register_contract').after(
            $('<div id="apply_contract" class="noselect">').append(
                $('<span id="btn_apply_key">').text('Apply Key')));
        $clone.find('span#btn_register_contract').off('click').on('click', function () {
            $.unblockUI();
            self.register_contract();
        });
        $clone.find('#register_contract,#apply_contract').addClass('contract-mrg10');
        $clone.find('span#btn_apply_key').off('click').on('click', function () {
            $.unblockUI();
            rpc.query({
                model: 'ir.actions.act_window',
                method: 'search_read',
                domain: [['context', '=', "{'module' : 'general_settings'}"]]
            }).done(function (res) {
                if (!res)
                    window.location.reload();
                self.do_action(res[0]['id']).done(function () {
                    var $el = $('div[name=activator_key]');
                    if ($el && $el[0]){
                        $el[0].scrollIntoView({behavior: 'smooth', block: 'center'});
                        $el.parents('.o_setting_box').animate({backgroundColor: "rgb(239, 234, 208)"}, 2000, function () {
                            $el.parents('.o_setting_box').animate({backgroundColor: ''})
                        });
                    }
                });
            });
        });
        setTimeout(function () {
            $.blockUI({
                message: $clone,
                css: {cursor: 'auto'},
                overlayCSS: {cursor: 'auto'}
            });
            self.contract_expired();
        }, 150000);
    },
});

});
