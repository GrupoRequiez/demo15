# Copyright 2016 Antiun Ingenieria S.L. - Javier Iniesta
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _
from datetime import date, datetime, timedelta
import logging
from collections import defaultdict

_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = "mrp.production"
    _name = "mrp.production"
    _description = ""

    order_classification = fields.Selection([
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D')],
        string="Order",
        default="A")


class MrpProductionList(models.TransientModel):
    _name = "mrp.production.material.list"
    _description = "mrp.production.material.list"

    def get_outgoing_materials(self):
        mrp_ids = self.env['mrp.production'].browse(self._context.get('active_ids'))
        dict_orders = defaultdict(lambda: defaultdict(dict))
        extra_data = dict()
        for mrp_id in mrp_ids:
            if mrp_id.state != 'done':
                msg = 'This report can only be generated if the Production Order is "Done". %s' % mrp_id.name
                raise exceptions.Warning(_(msg))
            else:
                dict_orders[mrp_id.name].update({
                    '0details': {
                        'mrp_product': mrp_id.product_id.default_code,
                        'mrp_product_name': mrp_id.product_id.name,
                        'partner_name': mrp_id.partner_id.name,
                        'mrp_qty': mrp_id.product_uom_qty,
                        'mrp_obs': mrp_id.sale_line_observation,
                    }})
                for moves in mrp_id.move_raw_ids:
                    for move in moves:
                        internal_locations = ""
                        for line in move.move_line_ids:
                            internal_locations += "%s " % line.internal_locations
                        dict_orders[mrp_id.name].update({
                            str(line.id): {
                                'move_product': move.product_id.default_code,
                                'move_product_name': move.product_id.name,
                                'move_qty': move.quantity_done,
                                'locations': internal_locations
                            }})

        extra_data['ids'] = [value.name for value in mrp_ids]
        extra_data['moves'] = dict_orders
        extra_data['date'] = (datetime.now() - timedelta(hours=5)).strftime('%d-%m-%Y %H:%M:%S')
        data = dict()
        data['extra_data'] = extra_data
        material_list_report = self.env.ref(
            'requiez.action_print_report_material_list')
        return material_list_report.report_action(self, data=data)
