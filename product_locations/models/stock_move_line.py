# -*- coding: utf-8 -*-


from odoo import fields, models, api, exceptions, _


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    _name = 'stock.move.line'

    internal_locations = fields.Char('Internal locations')
