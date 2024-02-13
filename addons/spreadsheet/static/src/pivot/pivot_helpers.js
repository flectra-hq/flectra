/** @flectra-module **/

import { _t } from "@web/core/l10n/translation";
import { getFlectraFunctions } from "../helpers/flectra_functions_helpers";

/** @typedef {import("@spreadsheet/helpers/flectra_functions_helpers").Token} Token */

export const pivotFormulaRegex = /^=.*PIVOT/;

//--------------------------------------------------------------------------
// Public
//--------------------------------------------------------------------------

/**
 * Parse a spreadsheet formula and detect the number of PIVOT functions that are
 * present in the given formula.
 *
 * @param {Token[]} tokens
 *
 * @returns {number}
 */
export function getNumberOfPivotFormulas(tokens) {
    return getFlectraFunctions(tokens, [
        "FLECTRA.PIVOT",
        "FLECTRA.PIVOT.HEADER",
        "FLECTRA.PIVOT.POSITION",
        "FLECTRA.PIVOT.TABLE",
    ]).length;
}

/**
 * Get the first Pivot function description of the given formula.
 *
 * @param {Token[]} tokens
 *
 * @returns {import("../helpers/flectra_functions_helpers").FlectraFunctionDescription|undefined}
 */
export function getFirstPivotFunction(tokens) {
    return getFlectraFunctions(tokens, [
        "FLECTRA.PIVOT",
        "FLECTRA.PIVOT.HEADER",
        "FLECTRA.PIVOT.POSITION",
        "FLECTRA.PIVOT.TABLE",
    ])[0];
}

/**
 * Build a pivot formula expression
 *
 * @param {string} formula formula to be used (PIVOT or PIVOT.HEADER)
 * @param {*} args arguments of the formula
 *
 * @returns {string}
 */
export function makePivotFormula(formula, args) {
    return `=${formula}(${args
        .map((arg) => {
            const stringIsNumber =
                typeof arg == "string" && !isNaN(arg) && Number(arg).toString() === arg;
            const convertToNumber = typeof arg == "number" || stringIsNumber;
            return convertToNumber ? `${arg}` : `"${arg.toString().replace(/"/g, '\\"')}"`;
        })
        .join(",")})`;
}

export const PERIODS = {
    day: _t("Day"),
    week: _t("Week"),
    month: _t("Month"),
    quarter: _t("Quarter"),
    year: _t("Year"),
};
