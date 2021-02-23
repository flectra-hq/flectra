flectra.define('web_gantt.GanttRenderer', function (require) {
"use strict";

var AbstractRenderer = require('web.AbstractRenderer');
var config = require('web.config');
var core = require('web.core');
var dataComparisonUtils = require('web.dataComparisonUtils');
var fieldUtils = require('web.field_utils');

var _t = core._t;
var DateClasses = dataComparisonUtils.DateClasses;
var qweb = core.qweb;

return AbstractRenderer.extend({
    className: "o_gantt_renderer",
    id: "o_gantt_renderer",
    sampleDataTargets: ['.o_graph_canvas_container'],
    /**
     * @override
     * @param {Widget} parent
     * @param {Object} state
     * @param {Object} params
     * @param {boolean} [params.isEmbedded]
     * @param {Object} [params.fields]
     * @param {string} [params.title]
     */
    init: function (parent, state, params) {
        this._super.apply(this, arguments);
        this.isEmbedded = params.isEmbedded || false;
        this.title = params.title || '';
        this.fields = params.fields || {};
        this.modelName = params.modelName;
        this.startDate = params.startDate;
        this.endDate = params.endDate;
        this.titleField = params.titleField;
        this.progress_scale = params.progress_scale;
        this.child = params.child;
        this.childExist = params.childExist;
        this.disableLinking = params.disableLinking;
        this.chart = null;
        this.ganttId = _.uniqueId('gantt');
        this.$legendTooltip = null;
        this.$tooltip = null;
        this.rtlEnable = _t.database.parameters.direction == "rtl" ? true : false;
    },
    on_attach_callback: function () {
        this._super.apply(this, arguments);
        this.isInDOM = true;
        this._render();
    },
    /**
     * @override
     */
    on_detach_callback: function () {
        this._super.apply(this, arguments);
        this.isInDOM = false;
    },
    _prepareGanttData: function(){
        var self = this;
        this.GanttChartData = {"data": [],"links": []};
        this.state.GanttData.forEach(function (data){
            var progress_bar = data.progress;
            if(self.progress_scale){
                progress_bar = (data.progress) / self.progress_scale;
            }
            self.GanttChartData.data.push({
                id: data.resId,
                start_date: data.startDate,
                end_date: data.endDate,
                text: data.titleField,
                type: data.type || '',
                progress: progress_bar ? progress_bar : 0,
                parent: data.parent ? data.parent : false,
                readonly: self.state.lockedIDs.includes(data.resId),
            });
        });
    },
    async _renderView() {
        var self = this;
        this._prepareGanttData();
        if (this.chart) {

            this.chart.clearAll();
            this.chart.parse(this.GanttChartData);
            this._changeState();
        }else{
            if (this.isInDOM) {
                this._renderTitle();
                gantt.plugins({
                    tooltip: true
                });
                gantt.config.show_links = false;
                if(this.rtlEnable){
                    gantt.config.rtl = true;
                }
                gantt.config.date_grid = _t.database.parameters.date_format;
                gantt.config.auto_scheduling = true;
                gantt.config.auto_scheduling_strict = true;
                gantt.i18n.setLocale(moment.locale());
                gantt.init('o_gantt_renderer');
                gantt.parse(this.GanttChartData);
                this.chart = gantt;
                this.chart.attachEvent("onBeforeLightbox", function(){
                    return false;
                });
                this.chart.attachEvent("onBeforeTaskDrag", function(id, mode, e){
                    if(self.state.lockedIDs.includes(parseInt(id))){
                        return false;
                    }
                    return true;
                });
                this.chart.attachEvent("onAfterTaskDrag", function(id, mode, e){
                    var currentTask = this.getTask(id);
                    self._updateData(currentTask);
                });
                this._changeState();
            }
        }
    },
    _renderTitle: function () {
        if (this.title) {
            this.$el.prepend($('<label/>', {
                text: this.title,
            }));
        }
    },
    _changeState: function(){
        if(this.state.mode == 'month'){
            this.chart.config.scale_unit = "month";
            this.chart.config.date_scale = "%F, %Y";
        }else if(this.state.mode == 'week'){
            this.chart.config.scale_unit = "week";
            this.chart.config.date_scale = "Week #%W";
        }else{
            this.chart.config.scale_unit = "day";
            this.chart.config.date_scale = "%d %M";
        }
        this.chart.render();
    },
    _updateData: function(data){
        var updatedData = {};
        if(data.id.toString().startsWith('child_')){
            updatedData[this.child.startDate] = this.formatDate(data.start_date);
            updatedData[this.child.endDate] = this.formatDate(data.end_date);
            return this._rpc({
                model: this.child.model,
                method: 'write',
                args: [parseInt(data.id.substring("child_".length)), updatedData],
            });
        }else{
            updatedData[this.startDate] = this.formatDate(data.start_date);
            updatedData[this.endDate] = this.formatDate(data.end_date);
            return this._rpc({
                model: this.modelName,
                method: 'write',
                args: [data.id, updatedData],
            });
        }
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

        return [year, month, day].join('-');
    },
});
});
