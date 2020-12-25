flectra.define('web_flectra.BackendThemeCustomizer', function (require) {
"use strict";

var SystrayMenu = require('web.SystrayMenu');
var Widget = require('web.Widget');
var ajax = require('web.ajax');
var core = require('web.core');
var session = require('web.session');

var CustomizeMenu = Widget.extend({
    template: 'web.customize_menu',
    events:{
     'click .theme-changer': '_onThemeChange',
    },
    start: function () {
        this._super.apply(this, arguments);
        this.$inputs = this.$("a[data-xmlid]");
        $('body').attr('data-theme', 'dark');
        this.loader = core.qweb.render('web.color_palette_loading');
        return this.load_theme_changer();
    },
    load_theme_changer: function () {
        var self = this;
        return ajax.jsonRpc('/web/theme_customize_backend_get', 'call',
        ).then(function (data) {
                if(data){
                    self.$inputs.append('<i class="fa fa-sun-o">');
                    $('body').attr('data-theme', 'dark');
                }else{
                    self.$inputs.append('<i class="fa fa-moon-o">');
                    $('body').removeAttr('data-theme');
                }
        });
    },
    _onThemeChange: function(e){
        //var enable = this.get_xml_ids(this.$inputs.filter('[data-xmlid]:checked'));
        //var disable = this.get_xml_ids(this.$inputs.filter('[data-xmlid]:not(:checked)'));
        $('body').append(this.loader);
        return ajax.jsonRpc('/web/theme_customize_backend',
            'call').then(function (bundleHTML) {
            window.location.reload();
        });
    },
});

SystrayMenu.Items.push(CustomizeMenu);

});
