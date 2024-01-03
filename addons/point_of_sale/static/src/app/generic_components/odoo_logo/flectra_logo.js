/** @flectra-module */

import { Component } from "@flectra/owl";

export class FlectraLogo extends Component {
    static template = "point_of_sale.FlectraLogo";
    static props = {
        class: { type: String, optional: true },
        style: { type: String, optional: true },
        monochrome: { type: Boolean, optional: true },
    };
    static defaultProps = {
        class: "",
        style: "",
        monochrome: false,
    };
}
