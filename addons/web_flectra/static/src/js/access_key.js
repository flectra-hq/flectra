flectra.define('web_flectra.access_key', function(require){
'use strict';

    var CalendarView = require('web.CalendarView');
    var GraphView = require('web.GraphView');
    var PivotView = require('web.PivotView');

    // Added Hot Key For Rest Of Views
    CalendarView.include({
        accesskey: 'b'
    });
    GraphView.include({
        accesskey: 'm'
    });
    PivotView.include({
        accesskey: 'g'
    });

});