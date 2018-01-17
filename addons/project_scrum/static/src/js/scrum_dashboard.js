flectra.define('project_scrum.dashboard', function(require) {
    "use strict";

    var core = require('web.core');
    var field_utils = require('web.field_utils');
    var KanbanView = require('web.KanbanView');
    var KanbanModel = require('web.KanbanModel');
    var KanbanRenderer = require('web.KanbanRenderer');
    var KanbanController = require('web.KanbanController');
    var data = require('web.data');
    var view_registry = require('web.view_registry');
    var QWeb = core.qweb;

    var _t = core._t;
    var _lt = core._lt;

    var ScrumDashboardRenderer = KanbanRenderer.extend({
        events: _.extend({}, KanbanRenderer.prototype.events, {
            'click .total-sprints': 'on_sprints_click',
            'click .total-tasks': 'on_tasks_click',
            'click .total-stories': 'on_stories_click',
            'click .total-projects': 'on_projects_click',
        }),


        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * Notifies the controller that the target has changed.
         *
         * @private
         * @param {string} target_name the name of the changed target
         * @param {string} value the new value
         */
        _notifyTargetChange: function (target_name, value) {
            this.trigger_up('dashboard_edit_target', {
                target_name: target_name,
                target_value: value,
            });
        },

        fetch_data: function() {
            // Overwrite this function with useful data
            return $.when();
        },
        /**
         * @override
         * @private
         * @returns {Deferred}
         */
        _render: function() {
            var super_render = this._super;
            var self = this;
            self._rpc({
                route: '/project_scrum/get_sprints_data',
                params: {},}).done(function
            (result) {
                if (result) {
                    $('#total_projects').html("<h2>" + result.total_projects + "</h2>");
                    $('#total_sprints').html("<h2>" + result.total_sprints + "</h2>");
                    $('#total_stories').html("<h2>" + result.total_stories + "</h2>");
                    $('#total_tasks').html("<h2>" + result.total_tasks + "</h2>");
                }
            });
            self.render_line_chart();
            return this.fetch_data().then(function(result) {
                var scrum_dashboard_view = QWeb.render('ScrumDashboard');
                super_render.call(self);
                $(scrum_dashboard_view).prependTo(self.$el);
            });
        },

        load_sprint_burndown_chart: function(result) {
            var sprint_labels = [],
                sprint_velocities = [],
                sprint_rates = [];
            for (var key in result) {
                if (result[key]) {
                    sprint_labels.push(result[key].sprint_seq);
                    sprint_velocities.push(result[key].velocity);
                    sprint_rates.push(result[key].per);
                }
            }
            try {
                var sprint_burndown_chart = $("#scrum_chart")[0].getContext("2d");
                sprint_burndown_chart.canvas.height = 55;

                // This will get the first returned node in the jQuery collection.
                var sprint_chart = new Chart(sprint_burndown_chart);

                var sprint_chart_data = {
                    labels: sprint_labels,
                    datasets: [{
                            label: "Success (%)",
                            fillColor: "rgb(243, 156, 18)",
                            strokeColor: "rgb(243, 156, 18)",
                            pointColor: "rgb(243, 156, 18)",
                            pointStrokeColor: "#c1c7d1",
                            pointHighlightFill: "#fff",
                            pointHighlightStroke: "rgb(243, 156, 18)",
                            data: sprint_velocities
                        },
                        {
                            label: "Estimated Velocity",
                            fillColor: "rgba(60,141,188,0.9)",
                            strokeColor: "rgba(60,141,188,0.8)",
                            pointColor: "#3b8bba",
                            pointStrokeColor: "rgba(60,141,188,1)",
                            pointHighlightFill: "#fff",
                            pointHighlightStroke: "rgba(60,141,188,1)",
                            data: sprint_rates
                        },
                    ]
                };

                var sprint_chart_options = {
                    //Boolean - If we should show the scale at all
                    showScale: true,
                    //Boolean - Whether grid lines are shown across the chart
                    scaleShowGridLines: false,
                    //String - Colour of the grid lines
                    scaleGridLineColor: "rgba(0,0,0,.05)",
                    //Number - Width of the grid lines
                    scaleGridLineWidth: 1,
                    //Boolean - Whether to show horizontal lines (except X axis)
                    scaleShowHorizontalLines: true,
                    //Boolean - Whether to show vertical lines (except Y axis)
                    scaleShowVerticalLines: true,
                    //Boolean - Whether the line is curved between points
                    bezierCurve: true,
                    //Number - Tension of the bezier curve between points
                    bezierCurveTension: 0.3,
                    //Boolean - Whether to show a dot for each point
                    pointDot: false,
                    //Number - Radius of each point dot in pixels
                    pointDotRadius: 4,
                    //Number - Pixel width of point dot stroke
                    pointDotStrokeWidth: 1,
                    //Number - amount extra to add to the radius to cater for hit detection outside the drawn point
                    pointHitDetectionRadius: 20,
                    //Boolean - Whether to show a stroke for datasets
                    datasetStroke: true,
                    //Number - Pixel width of dataset stroke
                    datasetStrokeWidth: 2,
                    //Boolean - Whether to fill the dataset with a color
                    datasetFill: true,
                    //String - A legend template
                    legendTemplate: "<ul class=\"<%=name.toLowerCase()%>-legend\"><% for (var i=0; i<datasets.length; i++){%><li><span style=\"background-color:<%=datasets[i].lineColor%>\"></span><%=datasets[i].label%></li><%}%></ul>",
                    //Boolean - whether to maintain the starting aspect ratio or not when responsive, if set to false, will take up entire container
                    maintainAspectRatio: true,
                    //Boolean - whether to make the chart responsive to window resizing
                    responsive: true
                };

                //Create the line chart
                sprint_chart.Line(sprint_chart_data, sprint_chart_options);
            } catch (e) {
                console.log("Something went wrong...", e);
            }
        },

        render_line_chart: function() {
            var self = this;
            self._rpc({
            route: '/project_scrum/get_line_chart_data',
            params: {},}).done(function(result) {
                if (result) {
                    self.load_sprint_burndown_chart(result); //  load sprint burndown chart
                }
            });
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        on_sprints_click: function(event) {
            var self = this,
                context = {};
            context.search_default_group_by_project = 1;
            return self._rpc({
            route: "/web/action/load",
            params: {
                action_id: "project_scrum.action_project_sprint"
            },}).done(function(result) {
                if (result) {
                    result.views = [
                        [false, 'list'],
                        [false, 'form']
                    ];
                    result.context = context;
                    return self.do_action(result);
                };
            })
        },

        on_tasks_click: function(event) {
            var self = this,
                context = {};
            context.search_default_group_by_sprint = 1;
            return self._rpc({
            route:"/web/action/load",
            params: {
                action_id: "project.action_view_task"
            },}).done(function(result) {
                if (result) {
                    result.views = [
                        [false, 'list'],
                        [false, 'form']
                    ];
                    result.context = context;
                    return self.do_action(result);
                };
            })
        },

        on_stories_click: function() {
            var self = this,
                context = {};
            context.search_default_group_by_sprint = 1;
            return self._rpc({route:"/web/action/load",
            params: {
                action_id: "project_scrum.action_project_story_sprint"
            },}).done(function(result) {
                if (result) {
                    result.views = [
                        [false, 'list'],
                        [false, 'form']
                    ];
                    result.context = context;
                    return self.do_action(result);
                };
            })
        },

        on_projects_click: function() {
            var self = this,
                context = {};
            context.search_default_Manager = 1;
            return self._rpc({
                route: "/web/action/load",
                params:{
                    action_id: "project.open_view_project_all_config"
                },
            }).done(function(result) {
                if (result) {
                    result.views = [
                        [false, 'list'],
                        [false, 'form']
                    ];
                    result.context = context;
                    return self.do_action(result);
                };
            })
        },
    });

    var ScrumDashboardModel = KanbanModel.extend({
        //--------------------------------------------------------------------------
        // Public
        //--------------------------------------------------------------------------

        /**
         * @override
         */
        init: function () {
            this.dashboardValues = {};
            this._super.apply(this, arguments);
        },

        /**
         * @override
         */
        get: function (localID) {
            var result = this._super.apply(this, arguments);
            return result;
        },


        /**
         * @œverride
         * @returns {Deferred}
         */
        load: function () {
            return this._super.apply(this, arguments);
        },
        /**
         * @œverride
         * @returns {Deferred}
         */
        reload: function () {
            return this._super.apply(this, arguments);
        },
    });

    var ScrumDashboardController = KanbanController.extend({
        
    });

    var MyMainDashboard = KanbanView.extend({
        config: _.extend({}, KanbanView.prototype.config, {
            Model: ScrumDashboardModel,
            Renderer: ScrumDashboardRenderer,
            Controller: ScrumDashboardController,
        }),
        display_name: _lt('Dashboard'),
        icon: 'fa-dashboard',
        searchview_hidden: true,
    });

    view_registry.add('scrum_dashboard', MyMainDashboard);

    return {
        Model: ScrumDashboardModel,
        Renderer: ScrumDashboardRenderer,
        Controller: ScrumDashboardController,
    };
});
    