# -*- coding: utf-8 -*-
{
    'name': 'Account Custom',
    'version': '17.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Custom accounting extensions for MyTriv ERP',
    'description': """
        Custom accounting addon providing enhanced chart of accounts management,
        journal entry automation, and reconciliation helpers for improved financial operations.
    """,
    'author': 'MyTriv ERP',
    'website': 'https://github.com/fxagro/mytriv-erp',
    'license': 'LGPL-3',
    'depends': ['base', 'account', 'base_rest_api'],
    'data': [
        'security/ir.model.access.csv',
        'data/account_custom_data.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}