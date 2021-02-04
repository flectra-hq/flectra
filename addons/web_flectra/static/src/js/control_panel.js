/**********************************************************************************
*
*    Copyright (c) 2017-today MuK IT GmbH.
*
*    This file is part of MuK Grid Snippets
*    (see https://mukit.at).
*
*    This program is free software: you can redistribute it and/or modify
*    it under the terms of the GNU Lesser General Public License as published by
*    the Free Software Foundation, either version 3 of the License, or
*    (at your option) any later version.
*
*    This program is distributed in the hope that it will be useful,
*    but WITHOUT ANY WARRANTY; without even the implied warranty of
*    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*    GNU Lesser General Public License for more details.
*
*    You should have received a copy of the GNU Lesser General Public License
*    along with this program. If not, see <http://www.gnu.org/licenses/>.
*
**********************************************************************************/

flectra.define('web_flectra.ControlPanel', function (require) {
"use strict";

const ControlPanel = require('web.ControlPanel');
const config = require('web.config');

const { useState } = owl.hooks;

if (!config.device.isMobile) {
    return;
}

ControlPanel.patch('web_flectra.ControlPanel', T => {
	
    class ControlPanelPatch extends T {
        constructor() {
            super(...arguments);
            this.state = useState({
                showViewSwitcherButtons: false,
            });
            this.isMobile = true;
        }
        mounted() {
            super.mounted();
            this.onWindowClickEvent = this._onWindowClick.bind(this);
            window.addEventListener('click', this.onWindowClickEvent);
        }
        willUnmount() {
            super.willUnmount();
            window.removeEventListener('click', this.onWindowClickEvent);
        }
        _onWindowClick(event) {
            if (this.state.showViewSwitcherButtons && !event.target.closest('.o_cp_switch_buttons')) {
                this.state.showViewSwitcherButtons = false;
            }
        }
        _getCurrentViewIcon() {
        	const currentView = this.props.views.find((view) => { 
        		return view.type === this.env.view.type 
        	})
        	return currentView.icon;
        }
    }

    return ControlPanelPatch;
});

});
