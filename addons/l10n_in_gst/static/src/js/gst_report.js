flectra.define('l10n_in_gst.gstr1', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
//    var Model = require('web.Model');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var ControlPanelMixin = require('web.ControlPanelMixin');
    var crash_manager = require('web.crash_manager');
    var framework = require('web.framework');

    var QWeb = core.qweb;

    var GSTRport = Widget.extend(ControlPanelMixin, {
        template: 'GSTReportDashboard',
        events: {
            "click [data-action]": "open_summary_data",
            "click [action]": "trigger_action",
            "click .show_subline": "show_subline"
        },
        init: function (parent, action) {
            this.actionManager = parent;
            this.model = action.context.model; // get default model from context
            this.summary_type = action.context.summary_type
            this.pager_context = {
                rec_limit: 10,
                rec_start: 1,
                rec_end: 10,
                rec_length: null,
                rec_range: null,
                total_page: null,
            };

            this.months = {
                1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
                7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
            };
            this.gst_report_context = {
                'from_date': null,
                'to_date': null,
                'company_id': session.company_id,
                'year': null,
                'month': null,
                'template': 'ViewSummary',
                'data_action_method': 'get_gstr_summary',
                'summary_type': this.summary_type
            };
            this.update_date();
            return this._super.apply(this, arguments);
        },

        start: function () {
            var self = this;
            var temp = self._rpc({
                model: this.model,
                method: this.gst_report_context.data_action_method,
                args: [[], this.gst_report_context, 1],
            }).then(function (data) {
                return data;
            });
            return $.when(temp, this._super.apply(this, arguments)).then(function (data) {
                self.$el.html(QWeb.render(self.gst_report_context.template, {data: data['summary']}));
                self.$button_html = $(QWeb.render('GSTButton', {}));
                self.$pager_html = $(QWeb.render('GSTPager', {}));
                self.$search_view_html = $(QWeb.render('GSTFilter', {
                    companies: data['companies'],
                    months: self.months,
                    curr_com_id: session.company_id,
                    curr_month: new Date().getMonth() + 1,
                    curr_year: new Date().getFullYear()
                }));
                self.update_cp();
                self.render_control_panel();
            });
        },
        // Update from_date and to_date when change made in month filter
        update_date: function () {
            var dt;
            if (this.gst_report_context.from_date) {
                dt = new Date(this.gst_report_context.year + " " + this.gst_report_context.month + " 01");
            } else {
                dt = new Date();
            }
            var month = dt.getMonth() + 1,
                year = dt.getFullYear();
            new Date(year, month, 0).getDate();

            this.gst_report_context.year = year;
            this.gst_report_context.month = month;
            this.gst_report_context.from_date = year + '-' + month + '-01';
            this.gst_report_context.to_date = year + '-' + month + '-' + new Date(year, month, 0).getDate();
        },
        // Update control panel Mixin when go back in GST report
        do_show: function () {
            this._super.apply(this, arguments);
            this.update_cp();
        },
        // override method for change control panel mixin
        update_cp: function () {
            var status = {
                breadcrumbs: this.actionManager.get_breadcrumbs(),
                cp_content: {
                    $buttons: this.$button_html,
                    $searchview_buttons: this.$search_view_html,
                    $pager: this.$pager_html,
                    $searchview: this.$searchview
                }
            };
            return this.update_control_panel(status, {clear: true});
        },
        // update el according user select report type
        update_report_data: function () {
            var self = this;
            if (this.gst_report_context.template == 'ViewSummary') {
            self._rpc({
                model: this.model,
                method: this.gst_report_context.data_action_method,
                args: [[], this.gst_report_context],
            }).then(function (data) {
                    self.$el.html(QWeb.render(self.gst_report_context.template, {data: data}));
                });
            } else {
                self._rpc({
                    model: this.model,
                    method: this.gst_report_context.data_action_method,
                    args: [[], this.gst_report_context, this.pager_context.rec_start, this.pager_context.rec_end],
                }).then(function (data) {
                    self.$el.html(QWeb.render(self.gst_report_context.template, {data: data['data'], 'summary_type':
                    self.gst_report_context.summary_type
                    }));
                    $("#pager").removeClass('hidden');
                    self.pager_context.rec_length = data['length'];
                    if (self.pager_context.rec_limit > self.pager_context.rec_length) {
                        self.pager_context.rec_limit = self.pager_context.rec_length;
                    }
                    if (data['length'] > 0) {
                        self.pager_context.total_page = Math.ceil(data['length'] / self.pager_context.rec_limit);
                        self.pager_context.rec_end = Math.min(self.pager_context.rec_end, self.pager_context.rec_length);
                        self.pager_context.offset = (self.pager_context.total_page * self.pager_context.rec_limit) - self.pager_context.rec_length;
                        if (self.pager_context.rec_start === self.pager_context.rec_end && self.pager_context.rec_limit === 1) {
                            self.pager_context.rec_range = self.pager_context.rec_start.toString();
                        } else if (self.pager_context.rec_start === self.pager_context.rec_end && self.pager_context.rec_limit > 1) {
                            self.pager_context.rec_range = self.pager_context.rec_start.toString() + '-' + self.pager_context.rec_end.toString();
                        } else {
                            self.pager_context.rec_range = self.pager_context.rec_start.toString() + '-' + self.pager_context.rec_end.toString();
                        }
                        $("#pager .o_pager_value").html(self.pager_context.rec_range);
                        $("#pager .o_pager_limit").html(self.pager_context.rec_length);
                        if (self.pager_context.total_page > 1) {
                            self.$pager_html.find(".o_pager_next").prop('disabled', false);
                            self.$pager_html.find(".o_pager_previous").prop('disabled', false);
                        } else {
                            self.$pager_html.find(".o_pager_next").prop('disabled', true);
                            self.$pager_html.find(".o_pager_previous").prop('disabled', true);
                        }
                    } else {
                        $("#pager").addClass('hidden');
                    }
                });
            }
        },
        // function of control panel mixin
        render_control_panel: function () {
            var self = this;
            // view summary function
            this.$button_html.find('#view_summary_back').click(function (e) {
                var view_summary_back_btn = $(this);
                self._rpc({
                    model: 'gst.report',
                    method: 'get_gstr_summary',
                    args: [[], self.gst_report_context],
                }).then(function (data) {
                    self.$el.html(QWeb.render('ViewSummary', {data: data}));
                    self.gst_report_context.template = 'ViewSummary';
                    self.gst_report_context.data_action_method = 'get_gstr_summary';
                    view_summary_back_btn.addClass('hidden');
                    $("#pager").addClass('hidden');
                    $("#export_excel").removeClass('hidden');
                });
            });
            // month filter
            this.$search_view_html.find('#filter_month li a').click(function (e) {
                if (self.gst_report_context.month != $(this).attr('data-value')) {
                    $('#filter_month li').removeClass('active');
                    $('#filter_month li a span i').removeClass('fa fa-check pull-right');
                    $(this).find('i').addClass('fa fa-check pull-right');
                    $(this).parent().addClass('active');
                    $(this).parent().parent().prev().html($(this).attr('data-string') + ' <span class="caret"></span>');

                    self.gst_report_context.month = $(this).attr('data-value');
                    self.update_date();
                    self._clear_context();
                    self.update_report_data();
                }
            });
            // res_company filter
            this.$search_view_html.find('#res_company li a').click(function (e) {
                if (self.gst_report_context.company_id != parseInt($(this).attr('data-id'))) {
                    $('#res_company li').removeClass('active');
                    $('#res_company li a span i').removeClass('fa fa-check pull-right');
                    $(this).find('i').addClass('fa fa-check pull-right');
                    $(this).parent().addClass('active');
                    $(this).parent().parent().prev().html($(this).attr('data-string') + ' <span class="caret"></span>');

                    self.gst_report_context.company_id = parseInt($(this).attr('data-id'));
                    self.update_date();
                    self._clear_context();
                    self.update_report_data();
                }
            });
            // year filter
            this.$search_view_html.find('#filter_year').change(function (e) {
                if (self.gst_report_context.year != $(this).val()) {
                    self.gst_report_context.year = $(this).val();
                    self.update_date();
                    self._clear_context();
                    self.update_report_data();
                }
            });
            // export excel report
            this.$button_html.find('#export_excel').click(function (e) {
                var c = crash_manager;
                session.get_file({
                    url: '/l10n_in_gst/export_excel',
                    data: self.gst_report_context,
                    complete: framework.unblockUI,
                    error: c.rpc_error.bind(c)
                });
            });

            this.$pager_html.find('.o_pager_value').click(function (e) {
                var inner_self = this;
                var o_pager_value = $(this).html();
                var $input = $('<input>', {type: 'text', value: o_pager_value});

                $(this).html($input);
                $input.focus();

                // Event handlers
                $input.click(function (ev) {
                    ev.stopPropagation(); // ignore clicks on the input
                });
                $input.blur(function (ev) {
                    //$(inner_self).html($(this).val());
                    self._save($(ev.target), $(inner_self)); // save the state when leaving the input
                });
                $input.on('keydown', function (ev) {
                    ev.stopPropagation();
                    if (ev.which === $.ui.keyCode.ENTER) {
                        self._save($(ev.target), $(inner_self)); // save on enter
                    } else if (ev.which === $.ui.keyCode.ESCAPE) {
                        $(inner_self).html(o_pager_value); // leave on escape
                    }
                });
            });

            this.$pager_html.find('[accesskey]').click(function (e) {
                var access_key = $(this).attr('accesskey');
                if (access_key == "n") {
                    self.pager_context.rec_start = self.pager_context.rec_end + 1;
                    self.pager_context.rec_end = Math.min((self.pager_context.rec_end + self.pager_context.rec_limit), self.pager_context.rec_length);
                    if (self.pager_context.rec_end < self.pager_context.rec_start) {
                        self.pager_context.rec_start = 1;
                        self.pager_context.rec_end = self.pager_context.rec_limit;
                    }
                } else if (access_key == "p") {
                    self.pager_context.rec_start -= self.pager_context.rec_limit;
                    self.pager_context.rec_end = Math.max((self.pager_context.rec_start + self.pager_context.rec_limit - 1), 1);
                    if ((self.pager_context.rec_end == self.pager_context.rec_length) && (self.pager_context.rec_length < (self.pager_context.total_page * self.pager_context.rec_limit))) {
                        self.pager_context.rec_start = ((self.pager_context.total_page - 2) * self.pager_context.rec_limit) + 1;
                        self.pager_context.rec_end = self.pager_context.rec_start + self.pager_context.rec_limit;
                    } else if (self.pager_context.rec_start <= 0) {
                        self.pager_context.rec_start = ((self.pager_context.total_page - 1) * self.pager_context.rec_limit) + 1;
                        self.pager_context.rec_end = self.pager_context.rec_length;
                    }
                }
                if (self.pager_context.rec_start === self.pager_context.rec_end) {
                    self.pager_context.rec_range = self.pager_context.rec_start.toString();
                } else {
                    self.pager_context.rec_range = self.pager_context.rec_start.toString() + '-' + self.pager_context.rec_end.toString();
                }
                self.update_report_data();
            });
        },
        // render more details about report
        open_summary_data: function (e) {
            var data_action = $(e.target).attr('data-action');
            this._clear_context();
            this.gst_report_context.template = data_action.split('_data_')[1].toUpperCase() + 'ViewSummary';
            this.gst_report_context.data_action_method = data_action;
            $("#view_summary_back").removeClass('hidden');
            $("#export_excel").addClass('hidden');
            this.update_report_data();

        },
        // open invoice form
        trigger_action: function (e) {
            var self = this;
            var action = $(e.target).attr('action');
            var data_id = $(e.target).attr('data-id');
            var data_object = $(e.target).attr('data-object');
            if (action) {
                return self._rpc({
                            model: this.model,
                            method: action,
                            args: ['', {
                                id: data_id,
                                object: data_object
                            }],
                        }).then(function (result) {
                    return self.do_action(result);
                });
            }
        },
        // display sub line
        show_subline: function (e) {
            var tr = $(e.target).parent().parent().next('tr.data_subline');
            if (tr.attr('class').indexOf('hidden') === -1) {
                tr.addClass('hidden');
            } else {
                tr.removeClass('hidden');
            }
        },
        // clear page context
        _clear_context: function () {
            this.pager_context = {
                rec_limit: 10,
                rec_start: 1,
                rec_end: 10,
                rec_length: null,
                rec_range: null,
                total_page: null,
                offset: null
            };
        },
        // re-render after made change in pagination filter
        _save: function ($input, $o_pager_value) {
            var value = $input.val().split("-");
            var start = parseInt(value[0]);
            var end = parseInt(value[1]);
            var pager_context = _.clone(this.pager_context);
            if (!isNaN(start)) {
                if ((start <= this.pager_context.rec_length) && (start > 0)) {
                    if (value.length === 1) {
                        this.pager_context.rec_end = this.pager_context.rec_start = start;
                        this.pager_context.rec_limit = 1;
                    } else {
                        this.pager_context.rec_start = start;
                    }
                } else {
                    $o_pager_value.html(this.pager_context.rec_range);
                    return false;
                }

                if (!isNaN(end)) {
                    if ((end <= this.pager_context.rec_length) && (end > 0) && (end >= this.pager_context.rec_start)) {
                        this.pager_context.rec_end = end;
                        this.pager_context.rec_limit = (this.pager_context.rec_end - this.pager_context.rec_start) + 1;
                    } else {
                        $o_pager_value.html(this.pager_context.rec_range);
                        return false;
                    }
                }

                if (this.pager_context.rec_start > this.pager_context.rec_end) {
                    this.pager_context = pager_context;
                } else {
                    if (this.pager_context.rec_start === this.pager_context.rec_end) {
                        this.pager_context.rec_range = this.pager_context.rec_start.toString();
                    } else {
                        this.pager_context.rec_range = this.pager_context.rec_start.toString() + '-' + this.pager_context.rec_end.toString();
                    }
                    this.update_report_data();
                }
            } else {
                $o_pager_value.html(this.pager_context.rec_range);
                return false;
            }
        }
    });

    core.action_registry.add('l10n_in_gst.gstr1', GSTRport);

    return {
        GSTRport: GSTRport
    };

});
