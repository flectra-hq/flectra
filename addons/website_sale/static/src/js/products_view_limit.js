/*
    Part of Odoo Module Developed by 73lines
    See LICENSE file for full copyright and licensing details.
*/
flectra.define('website_product_misc_options_73lines.products_view_limit', function (require) {
    "use strict";

    var website = require('website.website');
    var ajax = require('web.ajax');

    $(function(){
        var previous_limit = localStorage['active_limit'];
        if (previous_limit) {
            for (var i = 0; i < $('.product_limit_link').length; i++) {
                if (previous_limit == $('.product_limit_link')[i].getAttribute('value')) {
                     $('.product_limit_link')[i].classList.add('active');
                }
            }
            $('.product_limit_link.active').parent().addClass('active')
        }
        $('.product_limit_link').click(function(type){
            if(type['type'] !== "click") return;
            ajax.jsonRpc('/shop/product_limit', 'call', {'value': $(this)[0].getAttribute('value')});
            location.reload();
            $(this).parent().siblings().removeClass('active');
            $(this).parent().addClass('active');
            localStorage['active_limit'] = $(this)[0].getAttribute('value');
        });
    });

});
