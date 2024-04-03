/** @flectra-module **/

import {UserMenu}  from "@web/webclient/user_menu/user_menu";
import { patch } from "@web/core/utils/patch";
const { hooks } = owl;
// const { useExternalListener, useRef, useState } = owl.hooks;
import { useExternalListener, useRef } from "@web/core/utils/hooks";
const { useState } = owl;
import { isMobileOS } from "@web/core/browser/feature_detection";

patch(UserMenu.prototype, {
    setup(...args) {
        super.setup(...args);
        this.state = useState({
            isMobile: isMobileOS(),
        });
        setTimeout(() =>{
      
            $('.o_mobile_user_menu_btn').on('click', function (){
                $('.o_mobile_user_menu').removeClass('d-none')
            })
            $('.o_mobile_user_menu_close').on('click', function (){
                $('.o_mobile_user_menu').addClass('d-none')
            })

        },300);
    },
});