# -*- coding: utf-8 -*-
{
    'name': 'Sale Custom',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Custom sales order management for MyTriv ERP',
    'description': """
        Custom sales addon providing enhanced sales order management,
        customer tracking, and REST API endpoints for improved sales operations.
    """,
    'author': 'MyTriv ERP',
    'website': 'https://github.com/fxagro/mytriv-erp',
    'license': 'LGPL-3',
    'depends': ['base', 'sale', 'base_rest_api'],
    'data': [
        'security/ir.model.access.csv',
        'data/sale_custom_data.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}