flectra.define('web.GanttModel', function (require) {
"use strict";

/**
 * The gantt model is responsible for fetching and processing data from the
 * server.  It basically just do a search_read and format/normalize data.
 */

var AbstractModel = require('web.AbstractModel');

return AbstractModel.extend({
    /**
     * @override
     * @param {Object} params
     */
    init: function () {
        this._super.apply(this, arguments);
        this.data = null;
    },
    /**
     * @override
     * @param {Object} params
     * @param {string[]} params.groupedBy a list of valid field names
     * @param {Object} params.context
     * @param {string[]} params.domain
     * @returns {Deferred}
     */
    load: function (params) {
        this.modelName = params.modelName;
        this.data = {
            records: [],
            domain: params.domain,
            context: params.context,
            groupedBy: params.groupedBy || [],
            arch: params.arch.attrs,
        };
        return this._loadData();
    },
    /**
     * @override
     * @param {Object} params
     * @param {string[]} params.groupedBy a list of valid field names
     * @param {Object} params.context
     * @param {string[]} params.domain
     * @returns {Deferred}
     */
    reload: function (handle, params) {
        if (params.domain) {
            this.data.domain = params.domain;
        }
        if (params.context) {
            this.data.context = params.context;
        }
        if (params.groupBy) {
            this.data.groupedBy = params.groupBy;
        }
        return this._loadData();
    },
    /**
     * @returns {Deferred}
     */
    _loadData: function () {
        var self = this;
        return this._rpc({
            model: this.modelName,
            method: 'search_read',
            context: this.data.context,
            domain: this.data.domain,
        })
            .then(function (records) {
                self.data.records = self._processData(records);
            });
    },
    _processData: function (raw_datas) {
        /**
         * GroupBy is only supported till 1st level !
         * @todo Flectra: Support Multi level GroupBy
         */
        var self = this;
        var ganttData = [];
        if (self.data.groupedBy.length) {
            _.each(raw_datas, function (raw_data) {
                var grpByStr = raw_data[self.data.groupedBy[0]] ? raw_data[self.data.groupedBy[0]] : 'Undefined';
                if (grpByStr && grpByStr instanceof Array) {
                    grpByStr = raw_data[self.data.groupedBy[0]] ? raw_data[self.data.groupedBy[0]][1] : 'Undefined';
                }
                var keyCheck = _.findKey(ganttData, {name: grpByStr});
                if (!keyCheck) {
                    ganttData.push({
                        name: grpByStr,
                        series: [],
                    });
                }
                keyCheck = _.findKey(ganttData, {name: grpByStr});
                if (ganttData[keyCheck]) {
                    if (raw_data[self.data.arch['date_stop']]) {
                        ganttData[keyCheck].series.push({
                            id: raw_data['id'],
                            name: raw_data['display_name'],
                            start: raw_data[self.data.arch['date_start']].split(' ')[0],
                            end: raw_data[self.data.arch['date_stop']].split(' ')[0]
                        });
                    } else {
                        ganttData[keyCheck].series.push({
                            id: raw_data['id'],
                            name: raw_data['display_name'],
                            start: raw_data[self.data.arch['date_start']].split(' ')[0],
                            end: raw_data[self.data.arch['date_start']].split(' ')[0]
                        });
                    }
                }
            });
        } else {
            _.each(raw_datas, function (raw_data) {
                if (raw_data[self.data.arch['date_stop']]) {
                    ganttData.push({
                        series: [
                            {
                                id: raw_data['id'],
                                name: raw_data['display_name'],
                                start: raw_data[self.data.arch['date_start']].split(' ')[0],
                                end: raw_data[self.data.arch['date_stop']].split(' ')[0]
                            },
                        ],
                    });
                } else {
                    ganttData.push({
                        series: [
                            {
                                id: raw_data['id'],
                                name: raw_data['display_name'],
                                start: raw_data[self.data.arch['date_start']].split(' ')[0],
                                end: raw_data[self.data.arch['date_start']].split(' ')[0]
                            },
                        ],
                    });
                }
            });
        }
        return ganttData;
    },
});

});
