flectra.define('web_flectra/static/src/components/thread.js', function (require) {
'use strict';

    const { registerInstancePatchModel } = require('mail/static/src/model/model_core.js');
    const session = require('web.session');

    registerInstancePatchModel('mail.composer', 'web_flectra/static/src/components/thread.js', {
        _computeRecipients()  {
            if(session.allow_suggested_recipient){
                return this._super(...arguments);
            } else {
                const recipients = [...this.mentionedPartners];
                return [['replace', recipients]];
            }
        }
    });
});