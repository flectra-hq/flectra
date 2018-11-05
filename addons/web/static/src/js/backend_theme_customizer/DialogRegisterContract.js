flectra.define('FlectraLicensing.DialogRegisterContract', function (require) {
    "use strict";
    var Dialog = require('web.Dialog');
    var rpc = require('web.rpc');

    return Dialog.extend({
        template: 'FlectraLicense.dialog_contract_registration',
        init: function (parent) {
            var options = {
                title: 'Register Contract',
                size: 'small',
                buttons: [
                    {
                        text: "save",
                        classes: 'btn-success',
                        click: _.bind(this.save, this)
                    },
                    {text: "Cancel", classes: 'btn-danger', close: true}
                ]
            };
            this._super(parent, options);
        },

        save: function () {
            var contract_id = this.$el.find('#contract_id').val();
            var self = this;
            var type = this.$el.find("input[name='activate']:checked").val();
            if (!contract_id || !type) {
                return;
            }
            rpc.query({
                model: 'ir.http',
                method: 'contract_validate_file',
                args: [contract_id,type]
            }).done(function (bin) {
                self.trigger('get_key', {'key': contract_id, 'binary': bin, 'type': type});
                self.close();
            });
        }
    })

});