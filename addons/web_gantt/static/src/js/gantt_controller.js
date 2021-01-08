flectra.define('web_gantt.GanttController', function (require) {
"use strict";


const AbstractController = require('web.AbstractController');
const { ComponentWrapper } = require('web.OwlCompatibility');
const DropdownMenu = require('web.DropdownMenu');
const { DEFAULT_INTERVAL, INTERVAL_OPTIONS } = require('web.searchUtils');
const { qweb } = require('web.core');
var view_dialogs = require('web.view_dialogs');

class CarretDropdownMenu extends DropdownMenu {
    /**
     * @override
     */
    get displayCaret() {
        return true;
    }
}

var GanttChartController = AbstractController.extend({
    events: _.extend({}, AbstractController.prototype.events, {
        'click .gantt_bar_task': '_onTaskClicked',
    }),
    custom_events: _.extend({}, AbstractController.prototype.custom_events, {
        item_selected: '_onItemSelected',
        open_view: '_onOpenView',
    }),

    /**
     * @override
     * @param {Widget} parent
     * @param {GraphModel} model
     * @param {GraphRenderer} renderer
     * @param {Object} params
     * @param {string[]} params.measures
     * @param {boolean} params.isEmbedded
     * @param {string[]} params.groupableFields,
     */
    init: function (parent, model, renderer, params) {
        this._super.apply(this, arguments);
        this.measures = params.measures;
        this.child = params.child;
        this.childExist = params.childExist;
        // this parameter condition the appearance of a 'Group By'
        // button in the control panel owned by the graph view.
        this.isEmbedded = params.isEmbedded;
        this.withButtons = params.withButtons;
        // views to use in the action triggered when the graph is clicked
        this.views = params.views;
        this.title = params.title;

        // this parameter determines what is the list of fields
        // that may be used within the groupby menu available when
        // the view is embedded
        this.groupableFields = params.groupableFields;
        this.buttonDropdownPromises = [];
    },
    /**
     * @override
     */
    start: function () {
        this.$el.addClass('o_gantt_controller');
        return this._super.apply(this, arguments);
    },
    getOwnedQueryParams: function () {
        var state = this.model.get();
        return {
            context: {
                gantt_mode: state.mode,
            }
        };
    },
    destroy: function () {
        this._super.apply(this, arguments);
    },
    _onTaskClicked:function(ev){
        var $target = $(ev.currentTarget);
        if($target.attr('task_id').startsWith('child_')){
            let id = $target.attr('task_id').substring("child_".length);

            return new view_dialogs.FormViewDialog(this, {
                title: $target.find('.gantt_task_content').text(),
                res_model: this.child.model,
                view_id: false,
                res_id: parseInt(id),
                on_saved: this.reload.bind(this, {}),
            }).open();

        }else{
            return new view_dialogs.FormViewDialog(this, {
                title: $target.find('.gantt_task_content').text(),
                res_model: this.modelName,
                view_id: false,
                res_id: parseInt($target.attr('task_id')),
                on_saved: this.reload.bind(this, {}),
            }).open();
        }
    },
    _onButtonClick:function(ev){
        var $target = $(ev.target);
        if($target.hasClass('o_gantt_button')){
            this.update({ mode: $target.data('mode') });
        }else{
            return new view_dialogs.FormViewDialog(this, {
                res_model: this.modelName,
                view_id: false,
                res_id: false,
                on_saved: this.reload.bind(this, {}),
            }).open();
        }
    },
    updateButtons: function () {
        if (!this.$buttons) {
            return;
        }
        var state = this.model.get();
        this.$buttons.find('.o_gantt_button').removeClass('active');
        this.$buttons
            .find('.o_gantt_button[data-mode="' + state.mode + '"]')
            .addClass('active');
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
    reload: async function () {
        const promises = [this._super(...arguments)];
        return Promise.all(promises);
    },
    renderButtons: function ($node) {
        this.$buttons = $(qweb.render('GanttView.buttons'));
        this.$buttons.click(ev => this._onButtonClick(ev));
    },

});
    return GanttChartController;
}); 