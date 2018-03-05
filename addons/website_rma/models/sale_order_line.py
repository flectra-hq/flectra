# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def get_return_qty(self, order_id, line_id):
        self._cr.execute("select s_line.id, r_line.product_id, "
                         "sum(r_line.qty_return) as return_qty from "
                         "rma_line "
                         "r_line, "
                         "rma_request req, sale_order so, "
                         "sale_order_line s_line where req.id = "
                         "r_line.rma_id and so.id = req.sale_order_id and "
                         "so.id = s_line.order_id and s_line.product_id = "
                         "r_line.product_id and so.id = %s and s_line.id "
                         "= %s " % (order_id, line_id) +
                         "group by(r_line.product_id, s_line.id)")
        result = self._cr.dictfetchall()
        if result:
            return result
