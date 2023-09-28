flectra.define('web_flectra.CalendarRenderer', function(require){
    'use strict';

    const config = require('web.config');
    const core = require('web.core');


    const Calendar = require('web.CalendarRenderer');

    Calendar.include({
        events: _.extend({}, Calendar.events, {
            'click .o_other_calendar_panel': '_onFilterClick'
        }),

        init: function (parent, state, params) {
            var self = this
            this._super.apply(this, arguments);
            this.filterPanelToggle = false;
        },

        _renderFilters() {
            return this._super(...arguments).then(() => {
                this.$('.o_calendar_mini').addClass('d-none');
                this._renderFilterBar();
            });
        },

        _onFilterClick() {
            this.filterPanelToggle = !this.filterPanelToggle;
            this.$('.o_calendar_view').toggleClass('d-none', this.filterPanelToggle);
            this.$('.o_calendar_sidebar_container').toggleClass('d-none', !this.filterPanelToggle);
            this._renderFilterBar();
        },

        _renderFilterBar(){
            if(this.$('.o_other_calendar_panel').length) { this.$('.o_other_calendar_panel').remove(); }
            var filters = [];
            for(const filter in this.state.filters){
                filters.push(this.state.filters[filter])
            }
            console.log(this.state.filters,'.THIS',filters)
            const filterBar = $(core.qweb.render('calendar.filterBar', {
                filterSections: filters,
                widget: this,
            }));
            this.$el.prepend(filterBar);
        }
    });
});