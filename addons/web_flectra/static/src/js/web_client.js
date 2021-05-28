flectra.define('web_flectra.WebClient', function (require) {
    "use strict";

    var WebClient = require('web.WebClient');
    var AbstractWebClient = require('web.AbstractWebClient');
    var core = require('web.core');
    var Menu = require('web.Menu');
    var dom = require('web.dom');
    var AppsMenu = require('web_flectra.AppsMenu');
    var session = require('web.session');

return  WebClient.include({
        events: _.extend({}, AbstractWebClient.prototype.events, {
            'custom_clicked': 'on_custom_clicked',
        }),
        custom_events: _.extend({}, AbstractWebClient.prototype.custom_events, {
            app_clicked: 'on_app_clicked',
            menu_clicked: 'on_menu_clicked',
            custom_clicked: 'on_custom_clicked',
        }),
        start: function(){
            return this._super.apply(this, arguments).then(function () {
                $('#menu_launcher').removeClass('d-none');
                core.bus.trigger('web_client_ready');
            });
        },
        _on_app_clicked_done: function (ev) {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self.menu._appsMenu._onOpenCloseDashboard(true);
            });
        },
        on_hashchange: function(event){
            this._super.apply(this, event);
            var state = $.bbq.getState();
            var $navbar = this.$el.parents('.o_main_navbar');
            var $menu_tray = $navbar.find('.o_menu_brand, .o_menu_sections');
            var $toggle_btn = this.$el.find('.full > i');
            var $dashboard = this.$el.find('#apps_menu');
            if (!$dashboard || !$dashboard.length) {
                $dashboard = $navbar.find('#apps_menu');
            }
            if (!$toggle_btn || !$toggle_btn.length) {
                $toggle_btn = $navbar.find('.full > i');
            }
            if((state.hasOwnProperty('home') && state.home == 'apps') || (Object.keys(state).length === 1 && Object.keys(state)[0] === "cids")){
                $toggle_btn.removeClass('fa-th');
                if(this.$el.find('.full > i').hasClass('fa-chevron-left') || this.$el.find('.full > i').hasClass('fa-th')){
                    this.$el.find('.full').css('pointer-events','all');
                }else{
                    this.$el.find('.full').css('pointer-events','none');
                }
                $menu_tray.hide();
                $dashboard.removeClass('d-none');
            }else{
                $toggle_btn.removeClass('fa-chevron-left').addClass('fa-th');
                $dashboard.addClass('d-none');
                this.$el.find('.o_menu_brand, .o_menu_sections').css('display','block');
            }
        },
        on_custom_clicked: function(){
            var current_action = JSON.parse(JSON.parse(window.sessionStorage.current_action));
            var state = $.bbq.getState();
            if((state.hasOwnProperty('home') && state.home == 'apps') || (Object.keys(state).length === 1 && Object.keys(state)[0] === "cids")){
                //this.do_action(current_action.id, {clear_breadcrumbs: false});
                $.bbq.pushState(this.prev_url, 2);
            }else{
                this.prev_url = state;
                $.bbq.pushState('#home=apps', 2);
            }
        },
    });
});  