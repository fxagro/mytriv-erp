# -*- coding: utf-8 -*-
{
    'name': 'Base REST API',
    'version': '17.0.1.0.0',
    'category': 'API',
    'summary': 'Base REST API functionality for MyTriv ERP',
    'description': """
        Base REST API addon providing REST endpoints for Odoo models.
        This addon provides basic REST API functionality for common operations.
    """,
    'author': 'MyTriv ERP',
    'website': 'https://github.com/fxagro/mytriv-erp',
    'license': 'LGPL-3',
    'depends': ['base', 'web', 'hr'],
    'data': [
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}