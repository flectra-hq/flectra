flectra.define('web.GanttModel', function (require) {
"use strict";

/**
 * The gantt model is responsible for fetching and processing data from the
 * server.  It basically just do a search_read and format/normalize data.
 */

var core = require('web.core');
var AbstractModel = require('web.AbstractModel');

var _t = core._t;

return AbstractModel.extend({
    /**
     * @override
     */
    init: function () {
        this._super.apply(this, arguments);
    },
    /**
     * @override
     * @param {any} params
     * @returns {Deferred}
     */
    load: function(params) {
        var self = this;
        this.modelName = params.modelName;
        this.gantt = {
            data: [],
            domain: params.domain,
            groupBy: params.groupedBy,
            context: params.context,
            arch: params.arch.attrs,
        };
        return this._loadGantt();
    },
    /**
     * @override
     * @param {any} handle ignored!
     * @param {Object} params
     * @param {string[]} [params.domain]
     * @param {string[]} [params.groupBy]
     * @returns {Deferred}
     */
    reload: function(handle, params) {
        if (params.domain) {
            this.gantt.domain = params.domain;
        }
        if (params.groupBy) {
            this.gantt.groupBy = params.groupBy;
        }
        return this._loadGantt();
    },
    /**
     * Fetch and process gantt data. It is basically a read_group with correct
     * fields.
     *
     * @returns {Deferred}
     */
    _loadGantt: function() {
        var self = this;
        this.gantt.data = [];
        return this._rpc({
            model: this.modelName,
            method: 'search_read',
            context: this.gantt.context,
            domain: this.gantt.domain,
            groupBy: this.gantt.groupBy,
        }).then(function(raw_datas) {
            /**
             * GroupBy is only supported till 1st level !
             * @todo Flectra: Support Multi level GroupBy
             */
            if(self.gantt.groupBy.length) {
                _.each(raw_datas, function(raw_data) {
                    var grpByStr = raw_data[self.gantt.groupBy[0]] ? raw_data[self.gantt.groupBy[0]] : 'Undefined';
                    if(grpByStr && grpByStr instanceof Array) {
                        grpByStr = raw_data[self.gantt.groupBy[0]] ? raw_data[self.gantt.groupBy[0]][1] : 'Undefined';
                    }
                    var keyCheck = _.findKey(self.gantt.data, {name: grpByStr});
                    if(!keyCheck) {
                        self.gantt.data.push({
                            name: grpByStr,
                            series: [],
                        });
                    }
                    keyCheck = _.findKey(self.gantt.data, {name: grpByStr});
                    if(self.gantt.data[keyCheck]) {
                        if(raw_data[self.gantt.arch['date_stop']]) {
                            self.gantt.data[keyCheck].series.push({
                                id: raw_data['id'], name: raw_data['display_name'],
                                start: raw_data[self.gantt.arch['date_start']], end: raw_data[self.gantt.arch['date_stop']]
                            });
                        } else {
                            self.gantt.data[keyCheck].series.push({
                                id: raw_data['id'], name: raw_data['display_name'],
                                start: raw_data[self.gantt.arch['date_start']], end: raw_data[self.gantt.arch['date_start']]
                            });
                        }
                    }
                });
            } else {
                _.each(raw_datas, function(raw_data) {
                    if(raw_data[self.gantt.arch['date_stop']]) {
                        self.gantt.data.push({
                            series: [
                                {id: raw_data['id'], name: raw_data['display_name'],
                                start: raw_data[self.gantt.arch['date_start']], end: raw_data[self.gantt.arch['date_stop']]},
                            ],
                        });
                    } else {
                        self.gantt.data.push({
                            series: [
                                {id: raw_data['id'], name: raw_data['display_name'],
                                start: raw_data[self.gantt.arch['date_start']], end: raw_data[self.gantt.arch['date_start']]},
                            ],
                        });
                    }
                });
            }

            /**
             * Render the Gantt view.
             *
             * Note that This method is synchronous, but the actual rendering is done
             * asynchronously (in a setTimeout).
             *
             */
            setTimeout(function() {
                $(".o_gantt_view_container").empty();
                $(".o_gantt_view_container").ganttView({
                    data: self.gantt.data,
                    slideWidth: 'auto',
                    cellWidth: 20,
                    behavior: {
                        clickable: false,
                        draggable: false,
                        resizable: false,
                        /**
                         * @todo Flectra:
                         * Turn-On below events & related behavior/functions
                         */
//                         onClick: function(data) {},
//
//                         onResize: function(data) {
//                            self.updateRecord(data);
//                         },
//
//                         onDrag: function(data) {
//                            self.updateRecord(data);
//                         },
                    }
                });
            }, 0);
        });
    },

//    updateRecord: function(data) {
//        var self = this;
//        return this._rpc({
//            model: self.modelName,
//            method: 'write',
//            args: [[data.id], {
//                [self.gantt.arch['date_start']]: data.start,
//                [self.gantt.arch['date_stop']]: data.end,
//            }],
//            context: self.gantt.context,
//        });
//    },

});

});
