flectra.define('website_sale_advance_pricelist.discount', function (require) {
    "use strict";

    require('web.dom_ready');
    var core = require('web.core');
    var _t = core._t;
    var discount_counter;
    
    function popover_discount($discount) {
        $discount.popover({
            trigger: 'manual',
            html: true,
            animation: true,
            title: function () {
                return _t("Discount Calculation Details");
            },
            container: 'body',
            placement: 'auto',
        }).on("mouseenter",function () {
            var self = this;
            clearTimeout(discount_counter);
            $discount.not(self).popover('hide');
            discount_counter = setTimeout(function(){
                if($(self).is(':hover')){
                    $.get("/website/discount", {'type': 'popover'})
                        .then(function (data) {
                            $(self).data("bs.popover").options.content =  data;
                            $(self).popover("show");
                            $(".popover").on("mouseleave", function () {
                                $(self).trigger('mouseleave');
                            });
                        });
                }
            }, 100);
        }).on("mouseleave", function () {
            var self = this;
            setTimeout(function () {
                if (!$(".popover:hover").length) {
                    if(!$(self).is(':hover')) {
                       $(self).popover('hide');
                    }
                }
            }, 100);
        });
    }

    $(function(e){
        popover_discount($('a[href$="/website/discount"]'));
        $(document).on("change", ".oe_cart input.js_quantity[data-product-id]", function () {
            setTimeout(function() {
                var $discount = $(document).find('a[href="/website/discount"]');
                popover_discount($discount);
            },2000);
      });

    });
});