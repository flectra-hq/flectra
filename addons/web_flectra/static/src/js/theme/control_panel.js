/** @flectra-module **/
import { ControlPanel } from "@web/search/control_panel/control_panel";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { patch } from "@web/core/utils/patch";
import { isMobileOS } from "@web/core/browser/feature_detection";

// const { useState } = owl.hooks;
const { useState } = owl;
// import {useState} from "@web/core/utils/hooks";
patch(ControlPanel.prototype, {
    setup(...args) {
        super.setup(...args);
        this.state = useState({
            showViewSwitcherButtons: false,
            mobileSearchMode: "",
        });
        this.isMobile = isMobileOS();
    },
//    get mobileConfig() {
//        return {
//            'isMobile': isMobileOS(),
//            'viewType': this.__owl__.parent.props.viewType
//        }
//    },
    _onWindowClick(event) {
        if (this.state.showViewSwitcherButtons && !event.target.closest('.o_cp_switch_buttons')) {
            this.state.showViewSwitcherButtons = false;
        }
    },
    _getCurrentViewIcon() {
        const currentView = this.props.views.find((view) => {
            return view.type === this.env.view.type
        })
        return currentView.icon;
    }
});
patch(DropdownItem.prototype, {
    setup(...args) {
        super.setup(...args);
        this.state = useState({
            showViewSwitcherButtons: false,
            mobileSearchMode: "",
        });
        this.isMobile = isMobileOS();
    },
    get mobileConfig() {
        return {
            'isMobile': isMobileOS(),
            'viewType': this.__owl__.parent.props.viewType
        }
    },
    _onWindowClick(event) {
        if (this.state.showViewSwitcherButtons && !event.target.closest('.o_cp_switch_buttons')) {
            this.state.showViewSwitcherButtons = false;
        }
    },
    _getCurrentViewIcon() {
        const currentView = this.props.views.find((view) => {
            return view.type === this.env.view.type
        })
        return currentView.icon;
    }
});
