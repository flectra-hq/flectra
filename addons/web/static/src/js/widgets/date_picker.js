flectra.define('web.datepicker', function (require) {
"use strict";

var core = require('web.core');
var config = require("web.config");
var field_utils = require('web.field_utils');
var time = require('web.time');
var Widget = require('web.Widget');

var _t = core._t;

var DateWidget = Widget.extend({
    template: "web.datepicker",
    type_of_date: "date",
    events: {
        'dp.error': 'errorDatetime',
        'dp.change': 'changeDatetime',
        'dp.hide': '_onHide',
        'dp.show': '_onShow',
        'keydown': '_onKeydown',
        'click input': '_onInputClicked',
        'change .o_datepicker_input': 'changeDatetime',
    },
    /**
     * @override
     */
    init: function (parent, options) {
        this._super.apply(this, arguments);

        this.name = parent.name;
        this.options = _.defaults(options || {}, {
            format : this.type_of_date === 'datetime' ? time.getLangDatetimeFormat() : time.getLangDateFormat(),
            minDate: moment({ y: 1900 }),
            maxDate: moment().add(200, "y"),
            calendarWeeks: true,
            icons: {
                time: 'fa fa-clock-o',
                date: 'fa fa-calendar',
                next: 'fa fa-chevron-right',
                previous: 'fa fa-chevron-left',
                up: 'fa fa-chevron-up',
                down: 'fa fa-chevron-down',
                close: 'fa fa-times',
            },
            locale : moment.locale(),
            allowInputToggle: true,
            keyBinds: null,
            widgetParent: 'body',
            useCurrent: false,
            ignoreReadonly: true,
        });

        // datepicker doesn't offer any elegant way to check whether the
        // datepicker is open or not, so we have to listen to hide/show events
        // and manually keep track of the 'open' state
        this.__isOpen = false;
    },
    /**
     * @override
     */
    start: function () {
        this.$input = this.$('input.o_datepicker_input');
        this.$input.datetimepicker(this.options);
        this.picker = this.$input.data('DateTimePicker');
        this._setReadonly(config.device.isMobile);
    },
    /**
     * @override
     */
    destroy: function () {
        if (this._onScroll) {
            window.removeEventListener('wheel', this._onScroll, true);
        }
        this.picker.destroy();
        this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * set datetime value
     */
    changeDatetime: function () {
        var oldValue = this.getValue();
        if (this.isValid()) {
            this._setValueFromUi();
            var newValue = this.getValue();
            var hasChanged = !oldValue !== !newValue;
            if (oldValue && newValue) {
                var formattedOldValue = oldValue.format(time.getLangDatetimeFormat());
                var formattedNewValue = newValue.format(time.getLangDatetimeFormat())
                if (formattedNewValue !== formattedOldValue) {
                    hasChanged = true;
                }
            }
            if (hasChanged) {
                this.trigger("datetime_changed");
            }
        } else {
            var formattedValue = oldValue ? this._formatClient(oldValue) : null;
            this.$input.val(formattedValue);
        }
    },
    /**
     * Library clears the wrong date format so just ignore error
     */
    errorDatetime: function (e) {
        return false;
    },
    /**
     * Focuses the datepicker input. This function must be called in order to
     * prevent 'input' events triggered by the lib to bubble up, and to cause
     * unwanted effects (like triggering 'field_changed' events)
     */
    focus: function () {
        this.$input.focus();
    },
    /**
     * @returns {Moment|false}
     */
    getValue: function () {
        var value = this.get('value');
        return value && value.clone();
    },
    /**
     * @returns {boolean}
     */
    isValid: function () {
        var value = this.$input.val();
        if (value === "") {
            return true;
        } else {
            try {
                this._parseClient(value);
                return true;
            } catch (e) {
                return false;
            }
        }
    },
    /**
     * @param {Moment|false} value
     */
    setValue: function (value) {
        this.set({'value': value});
        var formatted_value = value ? this._formatClient(value) : null;
        this.$input.val(formatted_value);
        if (this.picker) {
            this.picker.date(value || null);
        }
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {Moment} v
     * @returns {string}
     */
    _formatClient: function (v) {
        return field_utils.format[this.type_of_date](v, null, {timezone: false});
    },
    /**
     * @private
     * @param {string|false} v
     * @returns {Moment}
     */
    _parseClient: function (v) {
        return field_utils.parse[this.type_of_date](v, null, {timezone: false});
    },
    /**
     * @private
     * @param {boolean} readonly
     */
    _setReadonly: function (readonly) {
        this.readonly = readonly;
        this.$input.prop('readonly', this.readonly);
    },
    /**
     * set the value from the input value
     *
     * @private
     */
    _setValueFromUi: function () {
        var value = this.$input.val() || false;
        this.setValue(this._parseClient(value));
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * Reacts to the datetimepicker being hidden
     * Used to unbind the scroll event from the datetimepicker
     *
     * @private
     */
    _onHide: function () {
        this.__isOpen = false;
        this.changeDatetime();
        if (this._onScroll) {
            window.removeEventListener('wheel', this._onScroll, true);
        }
        this.changeDatetime();
    },
    /**
     * Reacts to the datetimepicker being shown
     * Could set/verify our widget value
     * And subsequently update the datetimepicker
     *
     * @private
     */
    _onShow: function () {
        this.__isOpen = true;
        if(this.$input.val().length !== 0 && this.isValid()) {
            var value = this._parseClient(this.$input.val());
            this.picker.date(value);
            this.$input.select();
        }
        var self = this;
        this._onScroll = function (ev) {
            if (ev.target !== self.$input.get(0)) {
                self.picker.hide();
            }
        };
        window.addEventListener('wheel', this._onScroll, true);
    },
    /**
     * @private
     * @param {KeyEvent} ev
     */
    _onKeydown: function (ev) {
        if (ev.which === $.ui.keyCode.ESCAPE) {
            if (this.__isOpen) {
                // we don't want any other effects than closing the datepicker,
                // like leaving the edition of a row in editable list view
                ev.stopImmediatePropagation();
                this.picker.hide();
            }
        }
    },
    /**
     * @private
     */
    _onInputClicked: function () {
        this.picker.toggle();
        this.focus();
    },
});

var DateTimeWidget = DateWidget.extend({
    type_of_date: "datetime",
    init: function () {
        this._super.apply(this, arguments);
        this.options = _.defaults(this.options, {
            showClose: true,
        });
    },
});

return {
    DateWidget: DateWidget,
    DateTimeWidget: DateTimeWidget,
};

});
