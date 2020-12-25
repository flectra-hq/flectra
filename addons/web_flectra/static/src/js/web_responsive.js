/* Copyright 2018 Tecnativa - Jairo Llopis
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

flectra.define("web_responsive", function (require) {
    "use strict";

    const ActionManager = require("web.ActionManager");
    const AbstractWebClient = require("web.AbstractWebClient");
    const AppsMenu = require("web.AppsMenu");
    const BasicController = require("web.BasicController");
    const config = require("web.config");
    const core = require("web.core");
    const FormRenderer = require("web.FormRenderer");
    const Menu = require("web.Menu");
    const RelationalFields = require("web.relational_fields");
    const ListRenderer = require("web.ListRenderer");
    const DocumentViewer = require("mail.DocumentViewer");

    function closeAppDrawer() {
        _.defer(function () {
            // Need close AppDrawer?
            var menu_apps_dropdown = document.querySelector(".o_menu_apps .dropdown");
            $(menu_apps_dropdown)
                .has(".dropdown-menu.show")
                .find("> a")
                .dropdown("toggle");
            // Need close Sections Menu?
            // TODO: Change to 'hide' in modern Bootstrap >4.1
            var menu_sections = document.querySelector(
                ".o_menu_sections li.show .dropdown-toggle"
            );
            $(menu_sections).dropdown("toggle");
            // Need close Mobile?
            var menu_sections_mobile = document.querySelector(".o_menu_sections.show");
            $(menu_sections_mobile).collapse("hide");
        });
    }

    function findNames(memo, menu) {
        if (menu.action) {
            var key = menu.parent_id ? menu.parent_id[1] + "/" : "";
            memo[key + menu.name] = menu;
        }
        if (menu.children.length) {
            _.reduce(menu.children, findNames, memo);
        }
        return memo;
    }


    BasicController.include({
        canBeDiscarded: function (recordID) {
            if (this.model.isDirty(recordID || this.handle)) {
                closeAppDrawer();
            }
            return this._super.apply(this, arguments);
        },
    });

    Menu.include({
        events: _.extend(
            {
                // Clicking a hamburger menu item should close the hamburger
                "click .o_menu_sections [role=menuitem]": "_onClickMenuItem",
                // Opening any dropdown in the navbar should hide the hamburger
                "show.bs.dropdown .o_menu_systray, .o_menu_apps": "_hideMobileSubmenus",
            },
            Menu.prototype.events
        ),

        start: function () {
            this.$menu_toggle = this.$(".o-menu-toggle");
            return this._super.apply(this, arguments);
        },

        _hideMobileSubmenus: function () {
            if (
                config.device.isMobile &&
                this.$menu_toggle.is(":visible") &&
                this.$section_placeholder.is(":visible")
            ) {
                this.$section_placeholder.collapse("hide");
            }
        },

        _onClickMenuItem: function (ev) {
            ev.stopPropagation();
        },

        _updateMenuBrand: function () {
            if (!config.device.isMobile) {
                return this._super.apply(this, arguments);
            }
        },
    });

    RelationalFields.FieldStatus.include({
        _setState: function () {
            this._super.apply(this, arguments);
            if (config.device.isMobile) {
                _.map(this.status_information, (value) => {
                    value.fold = true;
                });
            }
        },
    });

    // Sticky Column Selector
    ListRenderer.include({
        _renderView: function () {
            const self = this;
            return this._super.apply(this, arguments).then(() => {
                const $col_selector = self.$el.find(
                    ".o_optional_columns_dropdown_toggle"
                );
                if ($col_selector.length !== 0) {
                    const $th = self.$el.find("thead>tr:first>th:last");
                    $col_selector.appendTo($th);
                }
            });
        },

        _onToggleOptionalColumnDropdown: function (ev) {
            // FIXME: For some strange reason the 'stopPropagation' call
            // in the main method don't work. Invoking here the same method
            // does the expected behavior... O_O!
            // This prevents the action of sorting the column from being
            // launched.
            ev.stopPropagation();
            this._super.apply(this, arguments);
        },
    });

    FormRenderer.include({
        _renderHeaderButtons: function () {
            const $buttons = this._super.apply(this, arguments);
            if (
                !config.device.isMobile ||
                !$buttons.is(":has(>:not(.o_invisible_modifier))")
            ) {
                return $buttons;
            }

            $buttons.addClass("dropdown-menu");
            const $dropdown = $(
                core.qweb.render("web_responsive.MenuStatusbarButtons")
            );
            $buttons.addClass("dropdown-menu").appendTo($dropdown);
            return $dropdown;
        },
    });

    ActionManager.include({
        _appendController: function () {
            this._super.apply(this, arguments);
            closeAppDrawer();
        },
    });

    var KeyboardNavigationShiftAltMixin = {
        _shiftPressed: function (keyEvent) {
            const alt = keyEvent.altKey || keyEvent.key === "Alt",
                newEvent = _.extend({}, keyEvent),
                shift = keyEvent.shiftKey || keyEvent.key === "Shift";
            // Mock event to make it seem like Alt is not pressed
            if (alt && !shift) {
                newEvent.altKey = false;
                if (newEvent.key === "Alt") {
                    newEvent.key = "Shift";
                }
            }
            return newEvent;
        },

        _onKeyDown: function (keyDownEvent) {
            return this._super(this._shiftPressed(keyDownEvent));
        },

        _onKeyUp: function (keyUpEvent) {
            return this._super(this._shiftPressed(keyUpEvent));
        },
    };

    AbstractWebClient.include(KeyboardNavigationShiftAltMixin);

    DocumentViewer.include({
        events: _.extend(
            _.omit(DocumentViewer.prototype.events, ["keydown", "keyup"]),
            {
                "click .o_maximize_btn": "_onClickMaximize",
                "click .o_minimize_btn": "_onClickMinimize",
                "shown.bs.modal": "_onShownModal",
            }
        ),

        start: function () {
            core.bus.on("keydown", this, this._onKeydown);
            core.bus.on("keyup", this, this._onKeyUp);
            return this._super.apply(this, arguments);
        },

        destroy: function () {
            core.bus.off("keydown", this, this._onKeydown);
            core.bus.off("keyup", this, this._onKeyUp);
            this._super.apply(this, arguments);
        },

        _onShownModal: function () {
            $(document).off("focusin.modal");
        },
        _onClickMaximize: function () {
            this.$el.removeClass("o_responsive_document_viewer");
        },
        _onClickMinimize: function () {
            this.$el.addClass("o_responsive_document_viewer");
        },
    });
});
