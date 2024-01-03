/** @flectra-module **/
import { getFlectraFunctions } from "@spreadsheet/helpers/flectra_functions_helpers";

/**
 * @typedef {import("@spreadsheet/helpers/flectra_functions_helpers").Token} Token
 * @typedef  {import("@spreadsheet/helpers/flectra_functions_helpers").FlectraFunctionDescription} FlectraFunctionDescription
 */

/**
 * @param {Token[]} tokens
 * @returns {number}
 */
export function getNumberOfAccountFormulas(tokens) {
    return getFlectraFunctions(tokens, ["FLECTRA.BALANCE", "FLECTRA.CREDIT", "FLECTRA.DEBIT"]).length;
}

/**
 * Get the first Account function description of the given formula.
 *
 * @param {Token[]} tokens
 * @returns {FlectraFunctionDescription | undefined}
 */
export function getFirstAccountFunction(tokens) {
    return getFlectraFunctions(tokens, ["FLECTRA.BALANCE", "FLECTRA.CREDIT", "FLECTRA.DEBIT"])[0];
}
