# -*- coding: utf-8 -*-
# Copyright 2022 Grupo Requiez (https://gruporequiez.com) <gflores@requiez.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': "product_locations",
    'summary': """
        Product Locations""",
    'description': """
    """,
    'author': "gflores",
    'website': "https://www.gruporequiez.com",
    'category': 'Inventory',
    'version': '0.0.1',
    'license': "LGPL-3",
    'depends': [
        'product',
        'stock', 'base',
    ],
    'data': [
        # security
        "security/location_security.xml",
        "security/ir.model.access.csv",
        # views
        'views/product_location_view.xml',
        'views/stock_move_line_view.xml',
        'views/upload_location_detail_view.xml',
        # Reports


    ],
    'demo': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
