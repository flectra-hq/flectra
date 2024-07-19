/** @flectra-module **/

import { NavBar } from "@web/webclient/navbar/navbar";
import { patch } from "@web/core/utils/patch";
const { hooks,useState } = owl;
import {useService, useRef, useBus} from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { isMobileOS } from "@web/core/browser/feature_detection";
const websiteSystrayRegistry = registry.category('website_systray');

patch(NavBar.prototype, {
    setup(...args) {
        this.state = useState({
            is_home_menu: false,
            isMobile: isMobileOS(),
            prev_url: null,
        });
        if(websiteSystrayRegistry){
            useBus(websiteSystrayRegistry, 'EDIT-WEBSITE', () => {
                if(this.shouldDisplayWebsiteSystray){
                    $('body').removeClass('f_dark_mode');
                } else {
                    if(session.dark_mode){
                        $('body').addClass('f_dark_mode');
                    }
                }
            });
        }
        this.router = useService('router')
        super.setup(...args);
        useBus(this.env.bus ,'app_clicked', (res) => {
            this.onNavBarDropdownItemSelection(res.detail.menu_id)
        });
        useBus(this.env.bus ,"home_menu_change", (res) => {
            this.state.is_home_menu = res.detail;
            this.onHomeMenuUpdate();
            this.isMobile = isMobileOS();
        });
        useBus(this.env.bus ,"set_prev_url", (res) => {
            this.state.prev_url = res.detail;
        });

        this.onHomeMenuUpdate();
    },

    async onClickMainMenu(e) {
        //await $.bbq.pushState('#home=apps', 2);
        this.env.bus.trigger('home_menu_toggled', true);
    },

    async onClickSideBarMenu(ev){
         ev.preventDefault();
         $('.o-menu-slide > i').toggleClass('fa-compress fa-expand');
         $('.f_launcher_content').toggleClass('mobile_views_menu_force');
         this.updateSidebar();
    },

    async onClickBackButton(e) {
        await this.actionService.doAction(this.state.prev_url.action, {
            stackPosition: "replacePreviousAction"
        });
        this.state.is_home_menu = false;
        this.onHomeMenuUpdate();
        this.isMobile = isMobileOS();
    },

    onHomeMenuUpdate() {
        if(this.state.is_home_menu){
            document.querySelector('body').classList.add('home_menu_page')
        } else {
            document.querySelector('body').classList.remove('home_menu_page')
        }
    },

    updateSidebar: function () {
        var btn = $('.o-menu-slide');
        var $fLauncherContent = $('.f_launcher_content');
        if (!$fLauncherContent.length || window.matchMedia('(max-device-width: 1024px)').matches) {
            btn.hide();
            $fLauncherContent.removeClass('mobile_views_menu_force');
        } else {
            btn.show();
        }
        if ($fLauncherContent.hasClass('mobile_views_menu_force') || window.matchMedia('(max-device-width: 1024px)').matches) {
            $('.f_launcher_content .app_name, .more-less, .oe_secondary_menu').addClass('hidden');
            $fLauncherContent.addClass('mobile_views_menu');
            $('.o_action_manager').addClass('force_mobile');
        } else {
            $('.f_launcher_content .app_name, .more-less, .oe_secondary_menu').removeClass('hidden');
            $fLauncherContent.removeClass('mobile_views_menu');
            $('.o_action_manager').removeClass('force_mobile');
        }
    }

});
