# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from odoo.exceptions import UserError


class ProductLocation(models.Model):
    _name = 'product.location'
    _description = 'Custom product locations'

    name = fields.Char('Name', required=True)
    active = fields.Boolean(string='Active')

    _sql_constraints = [('name_unique', 'UNIQUE(name)', "The location name must be unique")]


class ProductLocationDetail(models.Model):
    _name = 'product.location.detail'
    _description = 'Custom product locations'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, copy=False, index=True, default='draft')

    internal_location_id = fields.Many2one('product.location', 'Location name', required=True)
    product_id = fields.Many2one('product.product', 'Product', required=True)
    location_id = fields.Many2one('stock.location', 'Location', required=True, default=562)
    lot_id = fields.Many2one('stock.production.lot', 'Lot')
    product_qty = fields.Float('Quantity', required=True)
    tracking_type = fields.Selection('Tracking', related='product_id.tracking')
    comments = fields.Text('Comments')

    def unlink(self):
        for record in self:
            if record.state == 'done':
                raise UserError(
                    _('You cannot delete a validated record. You must cancel it first.'))
        return super(ProductLocationDetail, self).unlink()

    def action_validate(self):
        for record in self:
            domain = [('product_id', '=', self.product_id.id),
                      ('location_id', '=', self.location_id.id)]
            if self.product_id.tracking == 'lot':
                domain.append(('lot_id', '=', self.lot_id.id))
            quant_qty = self.env['stock.quant'].search(domain, limit=1).quantity
            if quant_qty > 0:
                domain.append(('state', '=', 'done'))
                pld_ids = self.env['product.location.detail'].search(domain)
                located_product_qty = sum(l.product_qty for l in pld_ids)
                remaining_qty = quant_qty-(located_product_qty+self.product_qty)
                if remaining_qty >= 0:
                    record.write({'state': 'done'})
                    return record
                else:
                    raise exceptions.Warning(
                        _("The available stock is not enough for this record %s %s" % (record.internal_location_id.name, record.product_id.default_code)))
            else:
                raise exceptions.Warning(
                    _("The available stock is not enough for this record %s %s" % (record.internal_location_id.name, record.product_id.default_code)))

    # def action_validate(self):
    #     for record in self:
    #         record.write({'state': 'done'})
    #     return True

    def action_cancel(self):
        for record in self:
            record.write({'state': 'cancel'})
        return True

    def action_draft(self):
        for record in self:
            record.write({'state': 'draft'})
        return True
