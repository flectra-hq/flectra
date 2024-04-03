/** @flectra-module */

    const { Component, onWillStart, useState , useExternalListener, useRef } = owl;
    import { useService } from "@web/core/utils/hooks";
    import { registry } from "@web/core/registry";
    const actionRegistry = registry.category("actions");
    const { HomeMenu } = require('@web_flectra/js/theme/home_menu');

    export class HomeMenuWrapper extends Component{
        setup() {
            console.log('inside')
            this.menuService = useService("menu");
            this.rpc = useService("rpc");
            onWillStart(async() => {
                const data = await this.loadMenus()
                console.log(data,'.data')
            });
        }

        loadMenus() {
            var self = this;

            return flectra.loadMenusPromise.then( function(allMenus){
                self.allMenus = allMenus;

                return self.rpc('/web/dataset/call_kw/ir.ui.menu/load_menus_root', {
                    model: 'ir.ui.menu',
                    method: 'load_menus_root',
                    args: [],
                    kwargs: {}
                }).then( function(menus){
                    for (var i = 0; i < menus.children.length; i++) {
                        var child = menus.children[i];
                        if (child.action === false) {
                            while (child.children && child.children.length) {
                                child = child.children[0];
                                if (child.action) {
                                    menus.children[i].action = child.action;
                                    break;
                                }
                            }
                        }
                    }
                    self.rootMenus = menus;

                    return menus;
                });
            });
        }
    }
    HomeMenuWrapper.components = {HomeMenu};
    HomeMenuWrapper.template = 'web_flectra.HomeMenuWrapper';
    actionRegistry.add('apps_menu',HomeMenuWrapper)
