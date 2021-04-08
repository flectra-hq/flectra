flectra.define("web_flectra.backend_pwa", function(require) {
    "use strict";
    var utils = require('web.utils');
    var session = require('web.session');

    $(document).ready(function (require) {
        //Setting User ID In cookie For One Signal
        utils.set_cookie('user_id', session.uid)

        if ("serviceWorker" in navigator) {
            navigator.serviceWorker.register("/service-worker.js").then(function () {
                console.log("Service Worker Registered");
            });
        }
    });
});
