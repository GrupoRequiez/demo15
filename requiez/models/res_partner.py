# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import api, fields, models, exceptions, _


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _name = 'res.partner'

    credit_avaiable = fields.Monetary(
        compute='_get_credit_used'
    )
    credit_expired = fields.Boolean(
        compute='_get_credit_used',
    )
    credit_ignore = fields.Boolean(
        default=False,
    )
    credit_used = fields.Monetary(
        compute='_get_credit_used',
    )
    credit_limit = fields.Monetary()
    grace_days = fields.Integer()
    expired_ignore = fields.Boolean(
        default=False,
    )
    sale_order_ignore = fields.Boolean(
        default=False,
    )

    partner_region = fields.Selection(
        [('cs', 'CENTRO SUR'),
         ('nt', 'NORTE'),
         ('ob', 'OCCIDENTE BAJIO'),
         ('ex', 'EXTRANJERO')],
        required=True,
        string='Region',
        # default='ex',
        help='Select partner region classification')

    # pylint:disable=W8104
    def _get_credit_used(self):
        payment_term_credits_ids = (
            [payment.id
             for payment in self.env['account.payment.term'].search([])
             if payment.line_ids[-1] and payment.line_ids[-1].days >= 0])
        invoices = self.env['account.move'].search([
            ('partner_id', '=', self.id),
            ('state', '=', 'posted'),
            ('payment_state', 'in', ('not_paid', 'in_payment')),
            ('move_type', '=', 'out_invoice'),
            ('invoice_payment_term_id', 'in', payment_term_credits_ids)])
        if not self.expired_ignore:
            self.credit_expired = False
            today = fields.Date.from_string(fields.Date.today())
            # for invoice in invoices:
            for invoice in (invoices.filtered(lambda r: r.name.split('/')[0] != 'VNMSI')):
                date_due = fields.Date.from_string(invoice.invoice_date_due)
                if date_due + timedelta(days=self.grace_days) <= today:
                    self.credit_expired = True
        self.credit_avaiable = self.credit_limit
        self.credit_used = 0
        company_currency = self.env.user.company_id.currency_id
        company_id = self.env.user.company_id.currency_id
        if not self.sale_order_ignore:
            sale_total = 0
            for sale in (self.env['sale.order'].search([
                    ('partner_id', '=', self.id),
                    ('state', '=', 'sale'),
                    ('invoice_status', '=', 'to invoice')])):
                self.credit_used += (
                    sale.currency_id._convert(
                        sale.amount_total,
                        company_currency,
                        company_id,
                        sale.date_order))

        if not self.credit_ignore:
            for invoice in (invoices.filtered(lambda r:
                                              r.name.split('/')[0]
                                              != 'VNMSI')):
                self.credit_used += (
                    invoice.currency_id._convert(invoice.amount_total,
                                                 company_currency,
                                                 company_id,
                                                 invoice.invoice_date))
        self.credit_avaiable -= self.credit_used

    def toggle_active(self):
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        for record in self:
            record.active = not record.active
