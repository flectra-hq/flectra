/** @flectra-module **/

import { Component } from "@flectra/owl";

export class WarningNotification extends Component {
    static template = "website_sale.warningNotification";
    static props = {
        warning: [String, { toString: Function }],
    }
}
