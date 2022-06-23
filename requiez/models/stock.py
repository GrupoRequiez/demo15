# Copyright 2018 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api, exceptions, _


class StockMove(models.Model):
    _inherit = 'stock.move'
    _name = 'stock.move'

    def _action_assign(self):
        if self.env.context.get('from_planned'):
            return True
        return super(StockMove, self)._action_assign()


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    _name = 'stock.move.line'

    internal_locations = fields.Char('Internal locations')
