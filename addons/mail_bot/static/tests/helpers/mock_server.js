flectra.define('mail_bot/static/tests/helpers/mock_server.js', function (require) {
"use strict";

const MockServer = require('web.MockServer');

MockServer.include({
    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    async _performRpc(route, args) {
        if (args.model === 'mail.channel' && args.method === 'init_flectrabot') {
            return this._mockMailChannelInitFlectraBot();
        }
        return this._super(...arguments);
    },

    //--------------------------------------------------------------------------
    // Private Mocked Methods
    //--------------------------------------------------------------------------

    /**
     * Simulates `init_flectrabot` on `mail.channel`.
     *
     * @private
     */
    _mockMailChannelInitFlectraBot() {
        // TODO implement this mock task-2300480
        // and improve test "FlectraBot initialized after 2 minutes"
    },
});

});
