flectra.define('web.GanttController', function (require) {
"use strict";
/*---------------------------------------------------------
 * Flectra Gantt view
 *---------------------------------------------------------*/

var AbstractController = require('web.AbstractController');
var core = require('web.core');

var qweb = core.qweb;

var GanttController = AbstractController.extend({
    template: "GanttView",
    /**
     * @override
     * @param {Widget} parent
     * @param {GanttModel} model
     * @param {AbstractRenderer} renderer
     * @param {Object} params
     */
    init: function(parent, model, renderer, params) {
        this._super.apply(this, arguments);
    },
});

return GanttController;

});
