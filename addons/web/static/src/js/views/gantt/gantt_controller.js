flectra.define('web.GanttController', function (require) {
"use strict";
/*---------------------------------------------------------
 * Flectra Gantt view
 *---------------------------------------------------------*/

var AbstractController = require('web.AbstractController');

return AbstractController.extend({
    custom_events: _.extend({}, AbstractController.prototype.custom_events, {
        updateRecord: '_onUpdateRecord',
    }),
    _onUpdateRecord: function (record) {
        this._rpc({
            model: this.model.modelName,
            method: 'write',
            args: [record.data.id, {
                [this.model.data.arch['date_start']]: record.data.start.toString('yyyy-M-d'),
                [this.model.data.arch['date_stop']]: record.data.end.toString('yyyy-M-d'),
            }],
        }).then(this.reload.bind(this));
    },
});

});
