flectra.define('FlectraLicensing.DialogRegisterContract', function (require) {
    "use strict";
    var Dialog = require('web.Dialog');
    var core = require('web.core');
    var rpc = require('web.rpc');

    return Dialog.extend({
        template: 'FlectraLicense.dialog_contract_registration',
        events: {
            'change #activate_online': '_onChangeOption',
            'click #download-key': '_onClickDownloadKey'
        },
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
        start: function() {
            this.contract_id = this.$el.find('#contract_id');
            this.type = this.$el.find("select#activate_online");
            this.activator_key = this.$el.find("#activator_key");
            this.form_offline = this.$el.find("#form-offline");
            return this._super.apply(this, arguments);
        },
        _getFile: function () {
            if (!this.contract_id.val() || !this.type.val()) {
                return false;
            }
            return rpc.query({
                model: 'ir.http',
                method: 'contract_validate_file',
                args: [this.contract_id.val(), this.type.val()]
            })
        },
        _validateFields: function () {
            this.contract_id.parent().toggleClass('has-error', !this.contract_id.val())
            this.activator_key.parent().toggleClass('has-error', !this.activator_key.prop('files').length)
        },
        _set_values: function(id) {
            var self = this;
            rpc.query({
                model: 'res.config.settings',
                method: 'set_values',
                args: [id]
            }).then(function () {
                self.close();
                var btn = [{
                    text: core._t('Refresh'),
                    classes: "btn-primary",
                    click: function () {
                        window.location.reload();
                    },
                    close: true
                }, {
                    text: core._t("Cancel"),
                    close: true,
                }];
                Dialog.alert(null, '', {
                    $content: $('<div/>').html('<h5>Your database successfully activated</h5>'),
                    buttons: btn
                });
            }).fail(function (error, event) {
                console.warn(error.data.message);
            });
        },
        _update_values: function (id, method, activator_key) {
            var self = this;
            var args = id ? [id] : [];
            args.push({ contract_id: this.contract_id.val(), activator_key: activator_key });
            rpc.query({
                model: 'res.config.settings',
                method: method,
                args: args,
            }).then(function (data) {
                if (data) {
                    var rec_id = data === true ? id : data;
                    self._set_values(rec_id);
                }
            });
        },
        _validateContract: function (file) {
            var self = this;
            var reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = function () {
                var b64 = reader.result.split('base64,')[1];
                rpc.query({
                    model: 'res.config.settings',
                    method: 'search_read',
                    kwargs: {
                        limit: 1,
                        fields: ['id'],
                        order: [{name: 'id', asc: false}],
                    }
                }).then(function (data) {
                    if (data.length && data[0]) {
                        self._update_values(data[0].id, 'write', b64);
                    } else {
                        self._update_values(false, 'create', b64);
                    }
                });
            };
            reader.onerror = function (error) {
                console.error(error);
            };
        },
        save: function () {
            this._validateFields();
            var self = this;
            var contract_id = this.contract_id.val();
            var type = this.type.val();
            if (type == 'offline') {
                var file = this.activator_key.prop('files');
                if (file.length && contract_id) {
                    this._validateContract(file[0]);
                }
            } else {
                var def = this._getFile();
                if (def) {
                    def.done(function (bin) {
                        self.trigger('get_key', {'key': contract_id, 'binary': bin, 'type': type});
                        self.close();
                    });
                }
            }
        },
        _onChangeOption: function (e) {
            this.form_offline.toggleClass('hidden', this.type.val() == 'online');
        },
        _onClickDownloadKey: function (e) {
            var self = this;
            var def = this._getFile();
            if (def) {
                def.done(function (bin) {
                    if (self.type.val() == 'offline') {
                        self.trigger('get_key', {'key': self.contract_id.val(), 'binary': bin, 'type': self.type.val()});
                    }
                });
            }
        }
    })

});
