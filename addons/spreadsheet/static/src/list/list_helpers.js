/** @flectra-module */

import { getFlectraFunctions } from "../helpers/flectra_functions_helpers";

/** @typedef {import("@spreadsheet/helpers/flectra_functions_helpers").Token} Token */

/**
 * Parse a spreadsheet formula and detect the number of LIST functions that are
 * present in the given formula.
 *
 * @param {Token[]} tokens
 *
 * @returns {number}
 */
export function getNumberOfListFormulas(tokens) {
    return getFlectraFunctions(tokens, ["FLECTRA.LIST", "FLECTRA.LIST.HEADER"]).length;
}

/**
 * Get the first List function description of the given formula.
 *
 * @param {Token[]} tokens
 *
 * @returns {import("../helpers/flectra_functions_helpers").FlectraFunctionDescription|undefined}
 */
export function getFirstListFunction(tokens) {
    return getFlectraFunctions(tokens, ["FLECTRA.LIST", "FLECTRA.LIST.HEADER"])[0];
}
