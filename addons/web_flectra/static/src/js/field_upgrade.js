flectra.define('flectra_backend_theme.FormRenderer', function (require) {
"use strict";
    var FormRenderer = require('base.settings');
    const symbol = Symbol('form');

    FormRenderer.Renderer.include({
        _updateView: function ($newContent) {
            var self = this;

            // Set the new content of the form view, and toggle classnames
            this.$el.html($newContent);
            this.$el.toggleClass('o_form_nosheet', !this.has_sheet);
            if (this.has_sheet) {
                this.$el.children().not('.o_FormRenderer_chatterContainer')
                    .wrapAll($('<div/>', {class: 'o_form_sheet_bg'}));
            }
            this.$el.toggleClass('o_form_editable', this.mode === 'edit');
            this.$el.toggleClass('o_form_readonly', this.mode === 'readonly');

            // Attach the tooltips on the fields' label
            _.each(this.allFieldWidgets[this.state.id], function (widget) {
                const idForLabel = self.idsForLabels[widget[symbol]];
                var $label = idForLabel ? self.$('.o_form_label[for=' + idForLabel + ']') : $();
                self._addFieldTooltip(widget, $label);
                if (widget.attrs.widget === 'upgrade_boolean') {
                    // this widget needs a reference to its $label to be correctly
                    // rendered
                    $newContent.find('.o_enterprise_label').parent().parent().parent().hide();
                    widget.renderWithLabel($label);
                }
            });
        },
    });
}); 