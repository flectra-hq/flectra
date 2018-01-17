flectra.define('web.CustomizeSwitcher', function (require) {
"use strict";

var core = require('web.core');
var Widget = require('web.Widget');
var ajax = require('web.ajax');

var QWeb = core.qweb;

var Theme = Widget.extend({
    template: 'web.theme_customize_backend',
    events: {
        'change input[data-xmlid]': 'change_selection',
        'click .theme_customizer_close': 'close',
    },
    start: function () {
        this.$inputs = this.$("input[data-xmlid]");
        this.loader = QWeb.render('web.color_palette_loading');
        return this.load_xml_data();
    },
    load_xml_data: function () {
        var self = this;
        return ajax.jsonRpc('/web/theme_customize_backend_get', 'call', {
            'xml_ids': this.get_xml_ids(this.$inputs)
        }).done(function (data) {
            _.each(data[0], function (active_less_id) {
                self.$inputs.filter('[data-xmlid="' + active_less_id + '"]').prop("checked", true);
            });
        }).fail(function (d, error) {
            $('body').prepend($('<div id="theme_error"/>').text(error.data.message));
            console.log(error.data.message);
        });
    },
    get_xml_ids: function ($inputs) {
        var xml_ids = [];
        $inputs.each(function () {
            if ($(this).data('xmlid') && $(this).data('xmlid').length) {
                xml_ids.push($(this).data('xmlid').trim());
            }
        });
        return xml_ids;
    },
    change_selection: function (event) {
        var enable = this.get_xml_ids(this.$inputs.filter('[data-xmlid]:checked'));
        var disable = this.get_xml_ids(this.$inputs.filter('[data-xmlid]:not(:checked)'));

        $('body').append(this.loader);
        return ajax.jsonRpc('/web/theme_customize_backend', 'call', {
            enable: enable,
            disable: disable,
            get_bundle: true,
        }).then(function (bundleHTML) {
            var $links = $('link[href*=".assets_backend"]');
            var $newLinks = $(bundleHTML).filter('link');

            var linksLoaded = $.Deferred();
            var nbLoaded = 0;
            $newLinks.on('load', function (e) {
                if (++nbLoaded >= $newLinks.length) {
                    linksLoaded.resolve();
                }
            });

            $newLinks.on('error', function (e) {
                linksLoaded.reject();
                window.location.hash = "theme=true";
                window.location.reload();
            });

            $links.last().after($newLinks);
            return linksLoaded.then(function () {
                $links.remove();
                $('body').find('.f_color_palette_loading').remove();
            });
        });
    }
});

return Theme;

});
