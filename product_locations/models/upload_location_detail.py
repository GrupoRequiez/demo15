# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import date, datetime, timedelta
import logging
import csv
import codecs
import base64
import tempfile
import os
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError
import xlrd

_logger = logging.getLogger(__name__)


class UploadLocationDetail(models.TransientModel):
    _name = 'upload.location.detail'
    _description = 'Mass reference load of location details'

    name = fields.Char('File Name')
    data_file = fields.Binary('File')
    getted = fields.Boolean('Getted', default=False)

    def confirm(self):
        data = base64.b64decode(self.data_file)
        # Save file
        file_name = '/tmp/%s' % self.name
        with open(file_name, 'wb') as file:
            file.write(data)
        try:
            xl_workbook = xlrd.open_workbook(file.name)
        except:
            raise exceptions.Warning(
                'The only file extensions allowed are xls and xlsx')
        sheet_names = xl_workbook.sheet_names()
        xl_sheet = xl_workbook.sheet_by_name(sheet_names[0])
        # Number of columns
        num_cols = xl_sheet.ncols
        # Extract headers from xls file
        headers = ['id', 'location', 'product', 'bills', 'qtty', 'created']
        import_data = []
        ld_pool = self.env['product.location.detail']
        for row_idx in range(1, (xl_sheet.nrows)):    # Iterate through rows
            row_dict = {}
            for col_idx in range(0, num_cols):  # Iterate through columns
                # Get cell object by row, col
                cell_obj = xl_sheet.cell(row_idx, col_idx)
                row_dict[headers[col_idx]] = cell_obj.value
            import_data.append(row_dict)
        for row in import_data:
            product_id = self.env['product.product'].search([('default_code', '=', row['product'])])
            internal_location_id = self.env['product.location'].search(
                [('name', '=', row['location'])])
            if product_id and internal_location_id:
                if product_id.tracking == 'lot' and row['bills']:
                    lot_id = self.env['stock.production.lot'].search(
                        [('id', '=', int(row['bills']))])
                    if lot_id:
                        ld_pool.create({
                            'product_id': product_id.id,
                            'internal_location_id': internal_location_id.id,
                            'lot_id': lot_id.id,
                            'location_id': 562,
                            'product_qty': row['qtty'],
                        })
                    else:
                        msg = "The lot:%s not found!" % row['bills']
                        raise exceptions.Warning(_(msg))
                else:
                    ld_pool.create({
                        'product_id': product_id.id,
                        'internal_location_id': internal_location_id.id,
                        'location_id': 562,
                        'product_qty': row['qtty'],
                    })
            else:
                msg = "The location:%s or product:%s not found!" % (
                    row['location'], row['product'])
                raise exceptions.Warning(_(msg))
        return True
