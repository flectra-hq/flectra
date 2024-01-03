flectra.define('web_flectra.BackendThemeCustomizer', function (require) {
    "use strict";

    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');
    import core from "@web/legacy/js/services/core";
    var Dialog = require('web.Dialog')
    var session = require('web.session');
    var rpc = require('web.rpc');
    var ajax = require('web.ajax');

    var QWeb = core.qweb;
    var BackendThemeCustomizer = Widget.extend({
        template: 'web_flectra.theme_customizer.menu',

        events: _.extend({}, Widget.prototype.events, {
            "click .f-theme-customizer-toggler": "_on_customizer_toggler",
            "click .f-theme-customizer-close": "_on_customizer_close",
            "click .save-btn": "_on_save_btn",
            "change #select_font": "_onChangeFont",
            "input #google_font_val": "_onFontInput",
            "click #reset_to_default": "_resetDefault",
        }),

        willStart: function () {
            var self = this;
            var customizer_data = this._read_data();
            return Promise.all([
                this._super.apply(this, arguments),
                customizer_data,
            ]).then(function (results) {
                self.company_settings = results[1].company_settings;
                self.user_settings = results[1].user_settings;
            });
        },

        start: function () {
            this._super.apply(this, arguments);
            //this.loader = core.qweb.render('web.color_palette_loading');
            this._toggle_dark_mode();
            this._toggle_apps_menu();
            this._render();
        },

        ////////////////////////
        /// UI methods
        ////////////////////////
        _toggle_dark_mode: function () {
            if (this.user_settings.dark_mode) {
                $('body').attr('data-theme', 'dark');
            } else {
                $('body').removeAttr('data-theme');
            }
        },

        _toggle_apps_menu: function () {
            if (this.company_settings.theme_menu_style == 'sidemenu') {
                $('body').attr('data-menu', 'sidemenu');
            }
        },

        ////////////////////////
        /// Data methods
        ////////////////////////
        async _save_customizer_data() {
            /* Get company_settings from ui. */
            var company_settings = {}
            var company_settings_old = this.company_settings
            var company_container = $('.f-theme-customizer-content .company_settings');
            var colorPicker = company_container.find('.color_picker_component');
            company_settings['theme_menu_style'] = company_container.find('#select_menu option:selected').val()
//            company_settings['preloader_option'] = company_container.find('#preloader_option option:selected').val()
            company_settings['preloader_option'] = company_container.find('#preloader_ul_li').attr('value')
            company_settings['theme_font_name'] = company_container.find('#select_font option:selected').val()
            if(company_container.find('#google_font_val').val()){
                company_settings['google_font'] = company_container.find('#google_font_val').val().toString();
            }

            colorPicker.each(function () {
                var name = $(this).attr('data-identity')
                var color_value = $(this).find('input.color-inp-value').val()
                color_value = _.str.trim(color_value);
                company_settings[name] = color_value;
            })

            company_settings = this._diff(company_settings, company_settings_old);
            await this._write_data('company_settings', company_settings);

            /* Get user_settings from ui. */
            var user_settings = {}
            var user_settings_old = this.user_settings
            var user_container = $('.f-theme-customizer-content .user_settings');

            user_settings['dark_mode'] = user_container.find('#toggle_darkmode').prop('checked')
            user_settings['chatter_position'] = user_container.find('#select_chatter option:selected').val()

            user_settings = this._diff(user_settings, user_settings_old);
            const data = await this._write_data('user_settings', user_settings);
            return true;
        },

        _onChangeFont: function(e){
            var font = $('#select_font').val();
            if(font == 'google-font'){
                $('.google-font-input').show();
            }else{
                $('.google-font-input').hide();
            }
        },

        _resetDefault(){
            var self = this;
            Dialog.confirm(this, ("Are You Sure You Want Reset Default?"), {
                confirm_callback: function () {
                    self._onResetDefault();
                },
            });
        },

        _onResetDefault: async function(){
            if (session.is_admin) {
                await this._write_data('company_settings', {
                    theme_background_color: '#f2f7fb',
                    theme_color_brand: '#009efb',
                    theme_sidebar_color: '#212529',
                    theme_font_name: 'Rubik',
                    theme_menu_style: 'apps',
                });
            }
            await this._write_data('user_settings', {
                chatter_position: 'sided',
                dark_mode: false,
            });
            window.location.reload();
        },

        _onFontInput: function(e){
            e.stopPropagation();
            e.preventDefault();
        },

        _diff: function(dict1, dict2) {
            var result = {};
            $.each(dict1, function (key, value) {
                if (!dict2.hasOwnProperty(key) || dict2[key] !== dict1[key]) {
                    result[key] = value;
                }
            });
            return result;
        },

        _read_data: function() {
            return ajax.jsonRpc('/web/backend_theme_customizer/read', 'call',
            ).then(function (data) {
                return data;
            }) ;
        },

        async _write_data(setting_type, data) {
            var result = {}
            if (setting_type && data) {
                result[setting_type] = data;
            }
            return ajax.jsonRpc('/web/backend_theme_customizer/write', 'call', result);
        },

        ////////////////////////
        /// Init and rendering
        ////////////////////////
        _init_customizer_data: function () {
            /* Write user_settings to customizer ui. */
            this.$el.find('#toggle_darkmode').prop('checked', this.user_settings.dark_mode);
            this.$el.find('#select_chatter').val(this.user_settings.chatter_position);

            /* Write company_settings to customizer ui. */
            this.$el.find('#select_menu').val(this.company_settings.theme_menu_style);
            this.$el.find('#select_font').val(this.company_settings.theme_font_name);
            this.$el.find('#preloader_option').val(this.company_settings.preloader_option);
            this.$el.find('#google_font_val').val(this.company_settings.google_font);
            if(this.company_settings.theme_font_name == 'google-font'){
                this.$el.find(".google-font-input").show();
            }else{
                this.$el.find(".google-font-input").hide();
            }
        },

        _init_color_picker: function (item) {
            var self = this;
            var items = item.find('.color-picker-base-spectrum');
            items.each(function () {
                this.spectrum = $(this).spectrum({
                    color: $(this).val(),
                    showInput: true,
                    hideAfterPaletteSelect: true,
                    clickoutFiresChange: true,
                    showInitial: true,
                    preferredFormat: "rgb",
                });
                this.spectrum.on("move.spectrum", function(e, tinycolor){
                    self._OnColorChange(e, tinycolor);
                });
            });
        },

        _OnColorChange :function(e, tinycolor){
            if($(e.target).hasClass('color-picker-base-spectrum')){
                var value = tinycolor.toRgbString();
                $(e.target).val(value);
                $(e.target).parent().parent().find('.color-inp-value').val(value);
            }
        },

        _render: function() {
            this.$('.f-theme-customizer-toggler').parent().append(QWeb.render('web_flectra.theme_customizer.panel', this));
            var panelContent = this.$('.f-theme-customizer-content')
            var adminPanel = QWeb.render('web_flectra.theme_customizer.panel.admin', this);
            var userPanel = QWeb.render('web_flectra.theme_customizer.panel.user', this);
            if (session.is_admin) {
                panelContent.append(userPanel);
                panelContent.append(adminPanel);
            } else {
                panelContent.append(userPanel);
            }
            setTimeout(()=>{
                this.loaderImage()
            },100)
            this._init_customizer_data();
            this._init_color_picker(this.$el);
        },
        loaderImage: function(){
            var langArray = [];
            $('.preloader_option option').each(function(){
              var img = $(this).attr("data-thumbnail");
              var text = this.innerText;
              var value = $(this).val();
              var item = '<li class="preloader_li" value="'+$(this).attr('value')+'"><img src="'+ img +'" alt="" value="'+value+'"/><span>'+ text +'</span></li>';
              langArray.push(item);
            })

            $('#preloader_list').html(langArray);

            //Set the button value to the first el of the array
            $('.btn-select').html(langArray[0]);
            $('.btn-select').attr('value', 'en');

            //change button stuff on click
            $('#preloader_list li').click(function(){
           preloader_onchange(this)
            });


            //check local storage for the preloader
            var sessionLang = localStorage.getItem('lang');
            if (sessionLang){
              //find an item with value of sessionLang
              var langIndex = langArray.indexOf(sessionLang);
              $('.btn-select').html(langArray[langIndex]);
              $('.btn-select').attr('value', sessionLang);
            } else {
               var langIndex = langArray.indexOf('ch');
              $('.btn-select').html(langArray[langIndex]);
              //$('.btn-select').attr('value', 'en');
            }
                var selected_preloader = $('.preloader_li[value="'+this.company_settings.preloader_option+'"]')
                preloader_onchange(selected_preloader[0])
                $(".preloader_block").toggle()
            function preloader_onchange(event){
                var img = $(event).find('img').attr("src");
               var value = $(event).find('img').attr('value');
               var text = event.innerText;
               var item = '<li><img src="'+ img +'" alt="" /><span>'+ text +'</span></li><span class="arrow"></span>';
              $('.btn-select').html(item);
              $('.btn-select').attr('value', value);
              $('.btn-select').attr('id', 'preloader_ul_li');
              $(".preloader_block").toggle();}

            $(".btn-select").click(function(){
                $(".preloader_block").toggle();
            });
        },
//
        ////////////////////////
        /// Handlers
        ////////////////////////
        _on_customizer_toggler: function (event) {
            event.preventDefault();
            event.stopPropagation();
            this.$('.f-theme-customizer-panel').toggleClass('open')
        },

        _on_customizer_close: function (event) {
            event.preventDefault();
            event.stopPropagation();
            this.$('.f-theme-customizer-panel').removeClass('open')
        },

        _on_save_btn: function (event) {
            event.preventDefault();
            this.$('.f-theme-customizer-panel').removeClass('open')
            //$('body').append(this.loader);
            this._save_customizer_data().then(function(){
                window.location.reload();
            });
        },
    });
    SystrayMenu.Items.push(BackendThemeCustomizer);
});