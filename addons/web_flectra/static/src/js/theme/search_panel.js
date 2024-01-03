/** @flectra-module **/

import { SearchPanel } from "@web/search/search_panel/search_panel";
import { patch } from "@web/core/utils/patch";
const { hooks } = owl;
// const { useExternalListener, useRef, useState } = owl.hooks;
import { useExternalListener, useRef, useState } from "@web/core/utils/hooks";

import { isMobileOS } from "@web/core/browser/feature_detection";

patch(SearchPanel.prototype, {
    setup(...args) {
        super.setup(...args);
        this.state.isMobile = isMobileOS()
        setTimeout(() =>{
            $('.o_mobile_searchPanel_category').on('click', function (){
                $('.o_mobile_searchPanel_toggle').removeClass('d-none')
            })
            $('.o_mobile_searchPanel_toggle_close').on('click', function (){
                $('.o_mobile_searchPanel_toggle').addClass('d-none')
            })
            $('.o_mobile_searchPanel_toggle_show_result').on('click', function (){
                $('.o_mobile_searchPanel_toggle').addClass('d-none')
            })

        },300);
    },
});