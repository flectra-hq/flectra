/** @flectra-module alias=web.home.menu **/

const { Component, onMounted, useState, useExternalListener, useRef } = owl;
import { ErrorHandler, NotUpdatable } from "@web/core/utils/components";
import { NavBar, MenuDropdown, MenuItem } from "@web/webclient/navbar/navbar";
import { useService } from "@web/core/utils/hooks";
import { isMobileOS } from "@web/core/browser/feature_detection";

export default class HomeMenu extends Component{

    setup() {
        super.setup(...arguments);
        this.command = useService('command');
        this.ui = useService('ui');
        this.company = useService("company");
        this.env.bus.trigger('home_menu_change', true);
        this.searchBox = useRef('searchBox');
        this.rootMenus = this.props.rootMenus;
        // DO Not Remove -> Will Be Used For No Code Editor
        this.state = useState({
            isEditor: false,
        });
        onMounted(() => {
            if(!isMobileOS()){
                this.focusOnSearch();
            }
        });
        useExternalListener(document, 'keydown', this.onKeyDown);
    }

    onKeyDown(){
        if(document.activeElement !== this.searchBox.el && this.ui.activeElement === document){
            this.focusOnSearch()
        }
    }

    focusOnSearch(){
        this.searchBox.el.focus();
    }


    onMenuClick(currentId) {
        this.env.bus.trigger('home_menu_change', false);
        this.env.bus.trigger('home_menu_selected', this.props.allMenus[currentId]);
    }

    async onInput(e) {
        this.command.openMainPalette({
            searchValue: `/${this.searchBox.el.value.trim()}`
        }, () => {
            this.env.bus.trigger('home_menu_change', false);
            this.searchBox.el.value = "";
            this.focusOnSearch()
        });
    }


}
HomeMenu.template = 'HomeMenu.Template';
HomeMenu.props = {
    rootMenus: Object,
    allMenus: Object,
};

HomeMenu.components = { NavBar, MenuDropdown, MenuItem, NotUpdatable, ErrorHandler };