/** @flectra-module */

import { coreTypes, CorePlugin, helpers } from "@flectra/o-spreadsheet";
import { omit } from "@web/core/utils/objects";
const { deepEquals } = helpers;

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
            case "DUPLICATE_SHEET":
                this.updateOnDuplicateSheet(cmd.sheetId, cmd.sheetIdTo);
                break;
        }
    }

    updateOnDuplicateSheet(sheetIdFrom, sheetIdTo) {
        for (const oldChartId of this.getters.getChartIds(sheetIdFrom)) {
            if (!this.flectraMenuReference[oldChartId]) {
                continue;
            }
            const oldChartDefinition = this.getters.getChartDefinition(oldChartId);
            const oldFigure = this.getters.getFigure(sheetIdFrom, oldChartId);
            const newChartId = this.getters.getChartIds(sheetIdTo).find((newChartId) => {
                const newChartDefinition = this.getters.getChartDefinition(newChartId);
                const newFigure = this.getters.getFigure(sheetIdTo, newChartId);
                return (
                    deepEquals(oldChartDefinition, newChartDefinition) &&
                    deepEquals(omit(newFigure, "id"), omit(oldFigure, "id")) // compare size and position
                );
            });

            if (newChartId) {
                this.history.update(
                    "flectraMenuReference",
                    newChartId,
                    this.flectraMenuReference[oldChartId]
                );
            }
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
