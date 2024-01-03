/** @flectra-module */

/**
 * This file is meant to load the different subparts of the module
 * to guarantee their plugins are loaded in the right order
 *
 * dependency:
 *             other plugins
 *                   |
 *                  ...
 *                   |
 *                filters
 *                /\    \
 *               /  \    \
 *           pivot  list  Flectra chart
 */

/** TODO: Introduce a position parameter to the plugin registry in order to load them in a specific order */
import * as spreadsheet from "@flectra/o-spreadsheet";
const { corePluginRegistry, coreViewsPluginRegistry } = spreadsheet.registries;

import { GlobalFiltersCorePlugin, GlobalFiltersUIPlugin } from "@spreadsheet/global_filters/index";
import { PivotCorePlugin, PivotUIPlugin } from "@spreadsheet/pivot/index"; // list depends on filter for its getters
import { ListCorePlugin, ListUIPlugin } from "@spreadsheet/list/index"; // pivot depends on filter for its getters
import {
    ChartFlectraMenuPlugin,
    FlectraChartCorePlugin,
    FlectraChartUIPlugin,
} from "@spreadsheet/chart/index"; // Flectrachart depends on filter for its getters

corePluginRegistry.add("FlectraGlobalFiltersCorePlugin", GlobalFiltersCorePlugin);
corePluginRegistry.add("FlectraPivotCorePlugin", PivotCorePlugin);
corePluginRegistry.add("FlectraListCorePlugin", ListCorePlugin);
corePluginRegistry.add("flectraChartCorePlugin", FlectraChartCorePlugin);
corePluginRegistry.add("chartFlectraMenuPlugin", ChartFlectraMenuPlugin);

coreViewsPluginRegistry.add("FlectraGlobalFiltersUIPlugin", GlobalFiltersUIPlugin);
coreViewsPluginRegistry.add("FlectraPivotUIPlugin", PivotUIPlugin);
coreViewsPluginRegistry.add("FlectraListUIPlugin", ListUIPlugin);
coreViewsPluginRegistry.add("flectraChartUIPlugin", FlectraChartUIPlugin);
