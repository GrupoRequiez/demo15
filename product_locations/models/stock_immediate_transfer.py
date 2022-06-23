# -*- coding: utf-8 -*-


from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError


class StockImmediateTransfer(models.TransientModel):
    # _name = 'stock.immediate.transfer'
    _inherit = 'stock.immediate.transfer'

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
                if total_required == detail.product_qty:
                    loc_qty += "%s = %s, " % (detail.internal_location_id.name,
                                              detail.product_qty)
                    detail.update({'state': 'cancel'})
                    detail.unlink()
                    break
                elif total_required > detail.product_qty:
                    loc_qty += "%s = %s, " % (detail.internal_location_id.name,
                                              detail.product_qty)
                    total_required -= detail.product_qty
                    detail.update({'state': 'cancel'})
                    detail.unlink()
                else:
                    loc_qty += "%s = %s, " % (detail.internal_location_id.name,
                                              total_required)
                    detail.update({'product_qty': (detail.product_qty-total_required)})
                    break
        return loc_qty

    def process(self):
        res = super(StockImmediateTransfer, self).process()
        for transfer_line_id in self.immediate_transfer_line_ids:
            picking_id = transfer_line_id.picking_id
            for line in picking_id.move_line_ids_without_package:
                product_locations = self.location_assign(line)
                line.write({'internal_locations': product_locations})
        return res
