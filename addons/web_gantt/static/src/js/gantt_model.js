flectra.define('web_gantt.GanttModel', function (require) {
"use strict";

var core = require('web.core');
const { DEFAULT_INTERVAL, rankInterval } = require('web.searchUtils');

var _t = core._t;

var AbstractModel = require('web.AbstractModel');
var Domain = require('web.Domain');

return AbstractModel.extend({
    /**
     * @override
     * @param {Widget} parent
     */
    init: function () {
        this._super.apply(this, arguments);
        this.chart = null;
        this.GanttData = [];
        this.lockedIDs = [];
    },

    __get: function () {
        return Object.assign({ isSample: this.isSampleModel }, this.chart);
    },
    __load: function (params) {
        var groupBys = params.context.graph_groupbys || params.groupBys;
        this.initialGroupBys = groupBys;
        this.fields = params.fields;
        this.modelName = params.modelName;
        this.chart = Object.assign({
            context: params.context,
            dataPoints: [],
            domain: params.domain,
            groupBy: params.groupedBy.length ? params.groupedBy : groupBys,
            measure: params.context.graph_measure || params.measure,
            mode: params.context.graph_mode || params.mode,
            lockDomain: Domain.prototype.normalizeArray(Domain.prototype.stringToArray(params.lockState)),
            origins: [],
            stacked: params.stacked,
            timeRanges: params.timeRanges,
            orderBy: params.orderBy,
            startDate: params.startDate,
            endDate: params.endDate,
            child: params.child,
            childExist: params.childExist,
            progress: params.progress,
            titleField: params.titleField,
        });

        this._computeDerivedParams();

        return this._loadGraph();
    },
    __reload: function (handle, params) {
        if ('context' in params) {
            this.chart.context = params.context;
            this.chart.groupBy = params.context.graph_groupbys || this.chart.groupBy;
            this.chart.measure = params.context.graph_measure || this.chart.measure;
            this.chart.mode = params.context.graph_mode || this.chart.mode;
        }
        if ('domain' in params) {
            this.chart.domain = params.domain;
        }
        if ('groupBy' in params) {
            this.chart.groupBy = params.groupBy.length ? params.groupBy : this.initialGroupBys;
        }
        if ('measure' in params) {
            this.chart.measure = params.measure;
        }
        if ('timeRanges' in params) {
            this.chart.timeRanges = params.timeRanges;
        }

        this._computeDerivedParams();

        if ('mode' in params) {
            this.chart.mode = params.mode;
            return Promise.resolve();
        }
        if ('stacked' in params) {
            this.chart.stacked = params.stacked;
            return Promise.resolve();
        }
        if ('orderBy' in params) {
            this.chart.orderBy = params.orderBy;
            return Promise.resolve();
        }
        return this._loadGraph();
    },
    _computeDerivedParams: function () {
        this.chart.processedGroupBy = this._processGroupBy(this.chart.groupBy);

        const { range, rangeDescription, comparisonRange, comparisonRangeDescription, fieldName } = this.chart.timeRanges;
        if (range) {
            this.chart.domains = [
                this.chart.domain.concat(range),
                this.chart.domain.concat(comparisonRange),
            ];
            this.chart.origins = [rangeDescription, comparisonRangeDescription];
            const groupBys = this.chart.processedGroupBy.map(function (gb) {
                return gb.split(":")[0];
            });
            this.chart.comparisonFieldIndex = groupBys.indexOf(fieldName);
        } else {
            this.chart.domains = [this.chart.domain];
            this.chart.origins = [""];
            this.chart.comparisonFieldIndex = -1;
        }
    },
    _loadGraph: function () {
        var self = this;
        this.chart.dataPoints = [];
        this.chart.GanttData = [];
        this.chart.lockedIDs = [];
        var groupBy = this.chart.processedGroupBy;
        var fields = _.map(groupBy, function (groupBy) {
            return groupBy.split(':')[0];
        });
        if (this.chart.measure !== '__count__') {
            if (this.fields[this.chart.measure].type === 'many2one') {
                fields = fields.concat(this.chart.measure + ":count_distinct");
            }
            else {
            }
        }
        fields = fields.concat(this.chart.startDate);
        fields = fields.concat(this.chart.endDate);
        fields = fields.concat(this.chart.titleField);
        fields = fields.concat(this.chart.progress);
        if(this.chart.childExist){
            fields = fields.concat(this.chart.child.name);
        }
        var context = _.extend({fill_temporal: true}, this.chart.context);

        var proms = [];
        proms.push(this._rpc({
            route: '/web/dataset/search_read',
            model: this.modelName,
            fields: fields,
            context: context,
            domain: this.chart.domain,
        }).then(self._processGanttData.bind(self)));
        if(this.chart.lockDomain.length !== 0){
            proms.push(this._rpc({
                route: '/web/dataset/search_read',
                model: this.modelName,
                fields: fields,
                context: context,
                domain: this.chart.lockDomain,
            }).then(self._processLockedState.bind(self)));
        }
        return Promise.all(proms);
    },
    _processGanttData: async function(rawData) {
        var self = this;
        var childFields = ['display_name'];
        var proms = [];
        if(this.chart.childExist){
            childFields = childFields.concat(this.chart.child.startDate);
            childFields = childFields.concat(this.chart.child.endDate);
        }
        rawData.records.forEach(function (dataPt){
            if(dataPt[self.chart.startDate] != false && dataPt[self.chart.endDate] != false){
                var start_date = self.formatDate(dataPt[self.chart.startDate]);
                var end_date = self.formatDate(dataPt[self.chart.endDate]);
                var type = '';
                if(self.chart.childExist){
                    type = dataPt[self.chart.child.name].length != 0 ? "project" : ''
                }
                self.chart.GanttData.push({
                    resId: dataPt.id,
                    startDate: start_date,
                    type: type,
                    endDate: end_date,
                    titleField: dataPt[self.chart.titleField],
                    progress: dataPt[self.chart.progress],
                });
            }
            if(self.chart.childExist && dataPt[self.chart.child.name].length != 0){
                proms.push(self._rpc({
                    route: '/web/dataset/search_read',
                    model: self.chart.child.model,
                    fields: childFields,
                    domain: [['id', 'in', dataPt[self.chart.child.name]]],
                }).then(self._processGanttChildData.bind(self,dataPt)));
            }
        });
        return Promise.all(proms);
    },
    _processLockedState: async function(data){
        var self = this;
        data.records.forEach(function (dataPt){
            self.chart.lockedIDs.push(dataPt.id);
        });
    },
    _processGanttChildData: async function(data,rawData){
        var self = this;
        rawData.records.forEach(function (dataPt){
            var start_date = self.formatDate(dataPt[self.chart.child.startDate]);
            var end_date = self.formatDate(dataPt[self.chart.child.endDate]);
            self.chart.GanttData.push({
                resId: 'child_' + dataPt.id,
                startDate: start_date,
                endDate: end_date,
                titleField: dataPt['display_name'],
                parent: data.id,
            });
        });
    },
    formatDate: function(date){
        var d = new Date(date),
            month = '' + (d.getMonth() + 1),
            day = '' + d.getDate(),
            year = d.getFullYear();

        if (month.length < 2)
            month = '0' + month;
        if (day.length < 2)
            day = '0' + day;

        return [day, month, year].join('-');
    },
    _processGroupBy: function(groupBy) {
        const groupBysMap = new Map();
        for (const gb of groupBy) {
            let [fieldName, interval] = gb.split(':');
            const field = this.fields[fieldName];
            if (['date', 'datetime'].includes(field.type)) {
                interval = interval || DEFAULT_INTERVAL;
            }
            if (groupBysMap.has(fieldName)) {
                const registeredInterval = groupBysMap.get(fieldName);
                if (rankInterval(registeredInterval) < rankInterval(interval)) {
                    groupBysMap.set(fieldName, interval);
                }
            } else {
                groupBysMap.set(fieldName, interval);
            }
        }
        return [...groupBysMap].map(([fieldName, interval]) => {
            if (interval) {
                return `${fieldName}:${interval}`;
            }
            return fieldName;
        });
    },
});

});
