# Copyright 2018 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models, api


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    partner_region = fields.Selection(
        [('cs', 'CENTRO SUR'),
         ('nt', 'NORTE'),
         ('ob', 'OCCIDENTE BAJIO'),
         ('ex', 'EXTRANJERO')],
        string='Region',
    )
    invoice_brand = fields.Char('Invoice brand', readonly=True)

    @api.model
    def _group_by(self):
        group_by_str = super(AccountInvoiceReport, self)._group_by()
        group_by_str += """
        , move.partner_region
        , move.invoice_brand
        """
        return group_by_str

    @api.model
    def _sub_select(self):
        sub_select_str = super(AccountInvoiceReport, self)._sub_select()
        sub_select_str += """
        , move.partner_region as partner_region
        , move.invoice_brand as invoice_brand
        """
        return sub_select_str

    @api.model
    def _select(self):
        select_str = super(AccountInvoiceReport, self)._select()
        select_str += """
        , move.partner_region
        , move.invoice_brand
        """
        return select_str
