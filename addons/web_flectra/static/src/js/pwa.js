flectra.define("web_flectra.backend_pwa", function(require) {
    "use strict";
    $(document).ready(function (require) {
        if ("serviceWorker" in navigator) {
            navigator.serviceWorker.register("/service-worker.js").then(function () {
                console.log("Service Worker Registered");
            });
        }
    });
});
