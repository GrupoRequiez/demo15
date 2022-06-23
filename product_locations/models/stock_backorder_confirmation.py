# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError


class StockBackorderConfirmation(models.TransientModel):
    # _name = 'stock.backorder.confirmation'
    _inherit = 'stock.backorder.confirmation'

    def location_assign(self, line):
        domain = [('product_id', '=', line.product_id.id),
                  ('location_id', '=', line.location_id.id)]
        if line.product_id.tracking == 'lot':
            domain.append(('lot_id', '=', line.lot_id.id))
        location_detail_ids = self.env['product.location.detail'].search(
            domain, order='id')
        total_required = line.qty_done
        loc_qty = ""
        if location_detail_ids:
            for detail in location_detail_ids:
                if total_required >= detail.product_qty:
                    loc_qty += "%s = %s, " % (detail.internal_location_id.name,
                                              detail.product_qty)
                    total_required -= detail.product_qty
                    detail.sudo().unlink()
                else:
                    loc_qty += "%s = %s, " % (detail.internal_location_id.name,
                                              total_required)
                    detail.update({'product_qty': (detail.product_qty-total_required)})
                    break
        return loc_qty

    def process(self):
        res = super(StockBackorderConfirmation, self).process()
        for confirmation_line_id in self.backorder_confirmation_line_ids:
            picking_id = confirmation_line_id.picking_id
            for line in picking_id.move_line_ids_without_package:
                product_locations = self.location_assign(line)
                line.write({'internal_locations': product_locations})
        return res

    def process_cancel_backorder(self):
        res = super(StockBackorderConfirmation, self).process_cancel_backorder()
        for confirmation_line_id in self.backorder_confirmation_line_ids:
            picking_id = confirmation_line_id.picking_id
            for line in picking_id.move_line_ids_without_package:
                product_locations = self.location_assign(line)
                line.write({'internal_locations': product_locations})
        return res
