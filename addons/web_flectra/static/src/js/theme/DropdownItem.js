/** @flectra-module **/
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { patch } from "@web/core/utils/patch";
import { isMobileOS } from "@web/core/browser/feature_detection";

const { useState } = owl;
// import {useState} from "@web/core/utils/hooks";

patch(DropdownItem.prototype, {
    setup(...args) {
        super.setup(...args);
        this.state = useState({
            showViewSwitcherButtons: false,
            mobileSearchMode: "",
        });
        this.isMobile =isMobileOS();
        if (isMobileOS()) {
            $('.o_dropdown').on('click', function () {
                setTimeout(() => {
                    $('.o-dropdown--menu').addClass('o_dropdown_menu')
                    $('.o-dropdown--menu').addClass('dropdown-menu')
                    $('.o-dropdown--menu').addClass('show')
                }, 5)
            })
        }


    },
    get mobileConfig() {
        return {
            'isMobile': isMobileOS(),
            'viewType': this.__owl__.parent.props.viewType
        }
    },
});