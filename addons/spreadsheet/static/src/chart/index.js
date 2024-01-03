/** @flectra-module */

import * as spreadsheet from "@flectra/o-spreadsheet";

const { chartComponentRegistry } = spreadsheet.registries;
const { ChartJsComponent } = spreadsheet.components;

chartComponentRegistry.add("flectra_bar", ChartJsComponent);
chartComponentRegistry.add("flectra_line", ChartJsComponent);
chartComponentRegistry.add("flectra_pie", ChartJsComponent);

import { FlectraChartCorePlugin } from "./plugins/flectra_chart_core_plugin";
import { ChartFlectraMenuPlugin } from "./plugins/chart_flectra_menu_plugin";
import { FlectraChartUIPlugin } from "./plugins/flectra_chart_ui_plugin";

export { FlectraChartCorePlugin, ChartFlectraMenuPlugin, FlectraChartUIPlugin };
