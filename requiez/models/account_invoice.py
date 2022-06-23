# -*- coding: utf-8 -*-
# Copyright 2018 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import fields, models, api
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'
    _name = 'account.move'

    date_payment = fields.Datetime('Payment Date',)
    prioritized = fields.Boolean('Prioritized', readonly=True)

    partner_region = fields.Selection(
        [('cs', 'CENTRO SUR'),
         ('nt', 'NORTE'),
         ('ob', 'OCCIDENTE BAJIO'),
         ('ex', 'EXTRANJERO')],
        string='Region',
        store=True
    )

    invoice_brand = fields.Char('Invoice brand', readonly=True)
