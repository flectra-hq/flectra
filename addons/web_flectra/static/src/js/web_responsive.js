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
    var dragCount = 0;
    FormRenderer.include({
        start: function (){
            var superMethod = this._super.apply(this, arguments);
            this.dropTemplateAvailable = false;
            document.addEventListener('dragenter', this._onDragEnterForm.bind(this), true);
            document.addEventListener('dragover', this._onDragOver.bind(this), true);
            document.addEventListener('dragleave', this._onDragLeaveForm.bind(this), true);
            document.addEventListener('drop', this._onDropFile.bind(this), true);
            return superMethod;
        },
        _onDragEnterForm: function (e) {
            e.preventDefault();
            e.stopPropagation();
            if(this._checkFileType(e)){
                if(dragCount == 0){
                    if(!this.dropTemplateAvailable){
                        $('.o_content').append($(core.qweb.render('drop_template',{mode: this.mode})));
                        this.dropTemplateAvailable = true;
                    }
                }
                dragCount++;
            }
        },
        _onDragOver: function(e){
            e.preventDefault();
            e.stopPropagation();
        },
        _checkFileType: function(e){
            if(e.dataTransfer.types.length == 1 && e.dataTransfer.types[0] == 'Files'){
                return true;
            }else{
                return false;
            }
        },
        async _onDropFile(e){
            e.preventDefault();
            var self = this;
            if(this.mode == 'readonly'){
                if(e.dataTransfer.files.length != 0){
                    for(var file=0; file <  e.dataTransfer.files.length; file++){
                        var attachment = e.dataTransfer.files[file];
                        await this._createAttachment(e.dataTransfer.files[file]);
                    }
                    this.trigger('o-attachments-changed');
                    this._onDragLeaveForm(e);
                }else{
                    return;
                }
            }else{
                return;
            }
        },
        _createAttachment: function(attachment){
            var self = this;
            var fileReader = new FileReader();
            fileReader.onload = function(){
                return self._rpc({
                    model: "ir.attachment",
                    method: "create",
                    args: [{
                        name: attachment.name,
                        datas: base64js.fromByteArray(new Uint8Array(fileReader.result)),
                        res_model: self.state.model,
                        res_id: self.state.res_id,
                    }],
                });
            };
            fileReader.readAsArrayBuffer(attachment);
            this.trigger('o-attachments-changed');
        },
        _onDragLeaveForm: function(e){
            e.preventDefault();
            e.stopPropagation();
            if(this._checkFileType(e)){
                dragCount--;
                if(dragCount == 0 ){
                    if(this.dropTemplateAvailable){
                        this.dropTemplateAvailable = false;
                        $('.drag_zone').remove();
                    }
                }
            }
        },
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
