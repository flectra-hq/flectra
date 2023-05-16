flectra.define('web_flectra/static/src/components/composer_suggested_recipient.js', function (require) {
'use strict';

    const ComposerSuggestedRecipient = require('mail/static/src/components/composer_suggested_recipient/composer_suggested_recipient.js');
    const ComposerSuggestedRecipientList = require('mail/static/src/components/composer_suggested_recipient_list/composer_suggested_recipient_list.js');
    const session = require('web.session');

    class WebComposerSuggestedRecipient extends ComposerSuggestedRecipient{
        get suggestedRecipientInfo() {
            if(session.allow_suggested_recipient){
                return super.suggestedRecipientInfo;
            } else {
                return false;
            }
        }
    }

    ComposerSuggestedRecipientList.components = {
        ...ComposerSuggestedRecipientList.components,
        ComposerSuggestedRecipient: WebComposerSuggestedRecipient
    }
});