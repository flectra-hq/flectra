/** @flectra-module */

import { Component } from "@flectra/owl";
import { useSelfOrder } from "@pos_self_order/app/self_order_service";

export class CancelPopup extends Component {
    static template = "pos_self_order.CancelPopup";

    setup() {
        this.selfOrder = useSelfOrder();
    }

    confirm() {
        this.props.close();
        this.props.confirm();
    }
}
