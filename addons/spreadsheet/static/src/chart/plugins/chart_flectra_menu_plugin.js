/** @flectra-module */

import { coreTypes, CorePlugin } from "@flectra/o-spreadsheet";

/** Plugin that link charts with Flectra menus. It can contain either the Id of the flectra menu, or its xml id. */
export class ChartFlectraMenuPlugin extends CorePlugin {
    constructor(config) {
        super(config);
        this.flectraMenuReference = {};
    }

    /**
     * Handle a spreadsheet command
     * @param {Object} cmd Command
     */
    handle(cmd) {
        switch (cmd.type) {
            case "LINK_FLECTRA_MENU_TO_CHART":
                this.history.update("flectraMenuReference", cmd.chartId, cmd.flectraMenuId);
                break;
            case "DELETE_FIGURE":
                this.history.update("flectraMenuReference", cmd.id, undefined);
                break;
        }
    }

    /**
     * Get flectra menu linked to the chart
     *
     * @param {string} chartId
     * @returns {object | undefined}
     */
    getChartFlectraMenu(chartId) {
        const menuId = this.flectraMenuReference[chartId];
        return menuId ? this.getters.getIrMenu(menuId) : undefined;
    }

    import(data) {
        if (data.chartFlectraMenusReferences) {
            this.flectraMenuReference = data.chartFlectraMenusReferences;
        }
    }

    export(data) {
        data.chartFlectraMenusReferences = this.flectraMenuReference;
    }
}
ChartFlectraMenuPlugin.getters = ["getChartFlectraMenu"];

coreTypes.add("LINK_FLECTRA_MENU_TO_CHART");
