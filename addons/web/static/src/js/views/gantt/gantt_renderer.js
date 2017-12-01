flectra.define('web.GanttRenderer', function (require) {
"use strict";

/**
 * The graph renderer turns the data from the graph model into a nice looking
 * svg chart.  This code uses the nvd3 library.
 *
 * Note that we use a custom build for the nvd3, with only the model we actually
 * use.
 */

var core = require('web.core');
var AbstractRenderer = require('web.AbstractRenderer');
var Dialog = require('web.Dialog');

var _t = core._t;
var QWeb = core.qweb;

return AbstractRenderer.extend({
    template: "GanttView",
    /**
     * @override
     * @param {Widget} parent
     * @param {Object} state
     * @param {Object} params
     * @param {boolean} params.stacked
     */
    init: function (parent, state, params) {
        this.parent = parent;
        this._super.apply(this, arguments);
    },

    /**
     * Render the chart.
     *
     * Note that This method is synchronous, but the actual rendering is done
     * asynchronously (in a setTimeout).  The reason for that is that nvd3/d3
     * needs to be in the DOM to correctly render itself.  So, we trick Flectra by
     * returning immediately, then wait a tiny interval before actually
     * displaying the data.
     *
     * @returns {Deferred} The _super deferred is actually resolved immediately
     */
    _render: function () {
        this.data = this.parent.active_view.controller.model.data;
        this._loadGanttView();
        return $.when();
    },
    _loadGanttView: function () {
        var self = this;
        this.$el.empty().ganttView({
            data: self.data.records,
            slideWidth: 'auto',
            cellWidth: 20,
            behavior: {
                onClick: function (data) {
                    var dialog = new Dialog(self, {
                        title: _t(data.name),
                        $content: $(QWeb.render('GanttViewWizard')),
                        size: 'small',
                        buttons: [
                            {text: _t("Save"), classes: 'btn-success', click: _.bind(_callSave, self)},
                            {text: _t("Cancel"), classes: 'btn-danger', close: true}
                        ]
                    }).open();

                    dialog.opened().then(function () {
                        var datepickers_options = {
                            keepOpen: true,
                            minDate: moment({y: 1900}),
                            maxDate: moment().add(200, "y"),
                            calendarWeeks: true,
                            icons: {
                                time: 'fa fa-clock-o',
                                date: 'fa fa-calendar',
                                next: 'fa fa-chevron-right',
                                previous: 'fa fa-chevron-left',
                                up: 'fa fa-chevron-up',
                                down: 'fa fa-chevron-down',
                            },
                            locale: moment.locale(),
                            format: "YYYY-MM-DD",
                            ignoreReadonly: true
                        };
                        dialog.$el.find('input#start_date').val(data.start);
                        dialog.$el.find('input#end_date').val(data.end);
                        dialog.$el.find('input#start_date, input#end_date').datetimepicker(datepickers_options);
                    });

                    function _callSave(event) {
                        var newData = {
                            start: dialog.$el.find('input#start_date').val().toString(),
                            end: dialog.$el.find('input#end_date').val().toString(),
                            id: data.id
                        };
                        if (data.start !== newData.start || data.end !== newData.end) {
                            var start_data = new Date(dialog.$el.find('input#start_date').val().toString()).getTime();
                            var end_data = new Date(dialog.$el.find('input#end_date').val().toString()).getTime();
                            if(start_data <= end_data){
                                self.trigger_up('updateRecord', newData);
                                dialog.close();
                            }else {
                                self.do_warn(_t("Warning"), _t("Start date should be less than or equal to End date"));
                            }
                        }
                    }
                },

                onResize: function (data) {
                    self.trigger_up('updateRecord', data);
                },

                onDrag: function (data) {
                    self.trigger_up('updateRecord', data);
                },
            }
        });
        this.$el.removeAttr('style');
    },
});

});
