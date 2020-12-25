flectra.define('iap.redirect_flectra_credit_widget', function(require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var core = require('web.core');


var IapFlectraCreditRedirect = AbstractAction.extend({
    template: 'iap.redirect_to_flectra_credit',
    events : {
        "click .redirect_confirm" : "flectra_redirect",
    },
    init: function (parent, action) {
        this._super(parent, action);
        this.url = action.params.url;
    },

    flectra_redirect: function () {
        window.open(this.url, '_blank');
        this.do_action({type: 'ir.actions.act_window_close'});
        // framework.redirect(this.url);
    },

});
core.action_registry.add('iap_flectra_credit_redirect', IapFlectraCreditRedirect);
});
