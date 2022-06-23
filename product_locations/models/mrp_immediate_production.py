# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare


class MrpImmediateProduction(models.TransientModel):
    # _name = 'mrp.immediate.production'
    _inherit = 'mrp.immediate.production'

    def location_assign(self, line):
        domain = [('product_id', '=', line.product_id.id),
                  ('location_id', '=', line.location_id.id),
                  ('state', '=', 'done')]
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
                    detail.update({'state': 'cancel'})
                    detail.unlink()
                else:
                    loc_qty += "%s = %s, " % (detail.internal_location_id.name,
                                              total_required)
                    detail.update({'product_qty': (detail.product_qty-total_required)})
                    break
        return loc_qty

    def process(self):
        res = super(MrpImmediateProduction, self).process()
        for move in self.immediate_production_line_ids.production_id.move_raw_ids:
            for line in move.move_line_ids:
                product_locations = self.location_assign(line)
                line.write({'internal_locations': product_locations})
        return res
