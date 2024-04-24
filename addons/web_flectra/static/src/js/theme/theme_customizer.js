/** @flectra-module **/

import { Component, onWillStart, useRef, useEffect } from "@flectra/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";


export class ThemeCustomizer extends Component{
    static template = 'web_flectra.theme_customizer.menu';
    static props = {};

    setup() {
        this.rpc = useService('rpc');
        this.user = useService('user');
        this.themeRef = useRef('themeRef');
        this.brandRef = useRef('brandRef');
        this.bgRef = useRef('bgRef');
        this.sidedRef = useRef('sidedRef');

        onWillStart(async () => {
            await this.readData();
        });

        useEffect(() => {
            this.initColorPicker()
        });
    }

    initColorPicker() {
        const items = [this.brandRef.el ,this.bgRef.el ,this.sidedRef.el ];
        items.forEach((el) => {
            var spectrum = $(el).spectrum({
                color: $(el).val(),
                showInput: true,
                hideAfterPaletteSelect: true,
                clickoutFiresChange: true,
                showInitial: true,
                preferredFormat: "rgb",
            });
            spectrum.on("move.spectrum", (e, tinycolor) => {
                this._OnColorChange(e, tinycolor);
            });
        });
    }

    onSave() {
        this.onClose();
        this.saveData().then(() => {
            window.location.reload();
        });
    }

    async onReset() {
        if (this.user.isAdmin) {
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
    }

    async saveData() {
        var company_settings = {}
        var company_settings_old = this.company_settings
        var company_container = $(this.themeRef.el.querySelector('.f-theme-customizer-content .company_settings'));
        var colorPicker = company_container.find('.color_picker_component');
        company_settings['theme_menu_style'] = company_container.find('#select_menu option:selected').val()
        company_settings['preloader_option'] = company_container.find('#select_preloaders option:selected').val()
        company_settings['theme_font_name'] = company_container.find('#select_font option:selected').val()
        if(company_container.find('#google_font_val').val()){
            company_settings['google_font'] = company_container.find('#google_font_val').val().toString();
        }

        colorPicker.each(function () {
            var name = $(this).attr('data-identity')
            var color_value = $(this).find('input.color-inp-value').val()
            color_value = color_value.trim();
            company_settings[name] = color_value;
        })

        company_settings = this._diff(company_settings, company_settings_old);
        await this._write_data('company_settings', company_settings);

        /* Get user_settings from ui. */
        var user_settings = {}
        var user_settings_old = this.user_settings
        var user_container = $(this.themeRef.el.querySelector('.f-theme-customizer-content .user_settings'));

        user_settings['dark_mode'] = user_container.find('#toggle_darkmode').prop('checked')
        user_settings['chatter_position'] = user_container.find('#select_chatter option:selected').val()

        user_settings = this._diff(user_settings, user_settings_old);
        const data = await this._write_data('user_settings', user_settings);
        return true;
    }

    async _write_data(setting_type, data) {
        var result = {}
        if (setting_type && data) {
            result[setting_type] = data;
        }
        return this.rpc('/web/backend_theme_customizer/write', result);
    }

    _diff(dict1, dict2) {
        var result = {};
        $.each(dict1, function (key, value) {
            if (!dict2.hasOwnProperty(key) || dict2[key] !== dict1[key]) {
                result[key] = value;
            }
        });
        return result;
    }

    _OnColorChange(e, tinycolor){
        if($(e.target).hasClass('color-picker-base-spectrum')){
            var value = tinycolor.toRgbString();
            $(e.target).val(value);
            $(e.target).parent().parent().find('.color-inp-value').val(value);
        }
    }

    onClick() {
        this.themeRef.el.querySelector('.f-theme-customizer-panel').classList.add('open');
    }

    onClose() {
        this.themeRef.el.querySelector('.f-theme-customizer-panel').classList.remove('open');
    }

    async readData() {
        return await this.rpc('/web/backend_theme_customizer/read', {}
        ).then((data) => {
            this.company_settings = data.company_settings;
            this.user_settings = data.user_settings;
            if(this.company_settings['theme_font_name'] == 'google-font'){
            }

        }) ;
    }

    onChangeFont(){
        var font = $('#select_font').val();
        if(font == 'google-font'){
            $('.google-font-input').removeClass('d-none');
        }else{
            $('.google-font-input').addClass('d-none');
        }
    }
}

const systrayItem = {
    Component: ThemeCustomizer,
};

registry.category("systray").add("theme_customizer", systrayItem, { sequence: 1, force: true });
