flectra.define('web_gantt.GanttView', function (require) {
"use strict";


var AbstractView = require('web.AbstractView');
var core = require('web.core');
var GraphModel = require('web.GraphModel');
var Controller = require('web_gantt.GanttController');
var GanttRenderer = require('web_gantt.GanttRenderer');
var GanttModel = require('web_gantt.GanttModel');
var view_registry = require('web.view_registry');

var _t = core._t;
var _lt = core._lt;

var searchUtils = require('web.searchUtils');

var GanttView = AbstractView.extend({
    accesskey: 'o',
    display_name: _lt('Gantt'),
    icon: 'fa-tasks',
    config: _.extend({}, AbstractView.prototype.config, {
        Model: GanttModel,
        Controller: Controller,
        Renderer: GanttRenderer,
    }),
    viewType: 'gantt',
    searchMenuTypes: ['filter', 'groupBy', 'comparison', 'favorite'],

    /**
     * @override
     */
    init: function (viewInfo, params) {
        this._super.apply(this, arguments);
        const additionalMeasures = params.additionalMeasures || [];
        let title;
        let startDate;
        let endDate;
        let progress;
        let measure;
        let progress_scale;
        let childExist = false;
        let child = {};
        const measures = {};
        const measureStrings = {};
        let groupBys = [];
        const groupableFields = {};
        this.fields.__count__ = { string: _t("Count"), type: 'integer' };

        this.arch.children.forEach(field => {
            let fieldName = field.attrs.name;
            if (fieldName === "id") {
                return;
            }
            const interval = field.attrs.interval;
            if (interval) {
                fieldName = fieldName + ':' + interval;
            }
            if (field.attrs.type === 'start') {
                startDate = fieldName;
            }
            if(field.attrs.type === 'end'){
                endDate = fieldName;
            }
            if(field.attrs.type === 'title'){
                title = fieldName;
            }
            if(field.attrs.type === 'progress'){
                progress = fieldName;
                if(field.attrs.scale){
                    progress_scale = parseInt(field.attrs.scale);
                }
            }
            if(field.attrs.type === 'child'){
                if(this.fields[fieldName].type == 'many2many' || this.fields[fieldName].type == 'one2many'){
                    if(field.attrs.start && field.attrs.end){
                        child['name'] = fieldName;
                        child['startDate'] = field.attrs.start;
                        child['endDate'] = field.attrs.end;
                        child['model'] = this.fields[fieldName].relation;
                        childExist = true;
                    }
                }
            }
            if (field.attrs.string) {
                measureStrings[fieldName] = field.attrs.string;
            }
        });

        for (const name in measureStrings) {
            if (measures[name]) {
                measures[name].description = measureStrings[name];
            }
        }

        // Remove invisible fields from the measures
        this.arch.children.forEach(field => {
            let fieldName = field.attrs.name;
            if (field.attrs.invisible && py.eval(field.attrs.invisible)) {
                groupBys = groupBys.filter(groupBy => groupBy !== fieldName);
                if (fieldName in groupableFields) {
                    delete groupableFields[fieldName];
                }
                if (!additionalMeasures.includes(fieldName)) {
                    delete measures[fieldName];
                }
            }
        });

        const sortedMeasures = Object.values(measures).sort((a, b) => {
                const descA = a.description.toLowerCase();
                const descB = b.description.toLowerCase();
                return descA > descB ? 1 : descA < descB ? -1 : 0;
            });
        const countMeasure = {
            description: _t("Count"),
            fieldName: '__count__',
            groupNumber: 1,
            isActive: false,
            itemType: 'measure',
        };
        this.controllerParams.withButtons = params.withButtons !== false;
        this.controllerParams.measures = [...sortedMeasures, countMeasure];
        this.controllerParams.groupableFields = groupableFields;
        this.controllerParams.child = child;
        this.controllerParams.childExist = childExist;
        this.controllerParams.title = params.title || this.arch.attrs.string || _t("Untitled");
        // retrieve form and list view ids from the action to open those views
        // when the graph is clicked
        function _findView(views, viewType) {
            const view = views.find(view => {
                return view.type === viewType;
            });
            return [view ? view.viewID : false, viewType];
        }
        this.controllerParams.views = [
            _findView(params.actionViews, 'list'),
            _findView(params.actionViews, 'form'),
        ];

        this.rendererParams.fields = this.fields;
        this.rendererParams.modelName = params.modelName;
        this.rendererParams.startDate = startDate;
        this.rendererParams.endDate = endDate;
        this.rendererParams.progress = progress;
        this.rendererParams.child = child;
        this.rendererParams.childExist = childExist;
        this.rendererParams.progress_scale = progress_scale;
        this.rendererParams.titleField = 'display_name';
        this.rendererParams.title = this.arch.attrs.title; // TODO: use attrs.string instead
        this.rendererParams.disableLinking = !!JSON.parse(this.arch.attrs.disable_linking || '0');

        this.loadParams.startDate = startDate;
        this.loadParams.endDate = endDate;
        this.loadParams.progress = progress;
        this.loadParams.child = child;
        this.loadParams.childExist = childExist;
        this.loadParams.titleField = 'display_name';
        this.loadParams.mode = this.arch.attrs.type || 'day';
        this.loadParams.orderBy = this.arch.attrs.order;
        this.loadParams.lockState = this.arch.attrs.lock || '';
        this.loadParams.measure = measure || '__count__';
        this.loadParams.groupBys = groupBys;
        this.loadParams.fields = this.fields;
        this.loadParams.comparisonDomain = params.comparisonDomain;
        this.loadParams.stacked = this.arch.attrs.stacked !== "False";
    },
});
view_registry.add('gantt', GanttView);

return GanttView;

}); 