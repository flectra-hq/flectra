flectra.define('sale.pricelist', function (require) {
"use strict";
var AbstractField = require('web.AbstractField');
var core = require('web.core');
var field_registry = require('web.field_registry');
var QWeb = core.qweb;
var ShowDiscountDetailsWidget = AbstractField.extend({
    supportedFieldTypes: ['char'],
    isSet: function() {
        return true;
    },
    _render: function() {
        var self = this;
        var info = JSON.parse(this.value);
        if (!info) {
            this.$el.html('');
            return;
        }
        this.$el.html(QWeb.render('ShowDiscountInfo', {
            lines: info.content,
            outstanding: info.outstanding,
            title: info.title
        }));
        _.each(this.$('.js_discount_info'), function (k, v){
            var content = info.content[v];
            var options = {
                content: function () {
                    var $content = $(QWeb.render('AllDiscountDetails', {
                        gross_amount: content.gross_amount,
                        price_list_discount: content.price_list_discount,
                        price_rule_discount: content.price_rule_discount,
                        cart_rule_discount: content.cart_rule_discount,
                        coupon_code_discount: content.coupon_code_discount,
                        currency: content.currency,
                        untaxed_amount: content.untaxed_amount,
                        position: content.position,
                        amount_words: content.amount_words,
                        discount: content.discount,
                    }));
                    return $content;
                },
                html: true,
                placement: 'left',
                title: 'Discount Calculation Details:',
                trigger: 'focus',
                delay: { "show": 0, "hide": 100 },
            };
            $(k).popover(options);
        });
    },
});

field_registry.add('discount_widget', ShowDiscountDetailsWidget);

});
