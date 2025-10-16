# -*- coding: utf-8 -*-
{
    'name': 'HR Custom',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Custom HR management extensions for MyTriv ERP',
    'description': """
        Custom HR addon providing enhanced department management,
        employee profiles, and attendance tracking with REST API integration.
    """,
    'author': 'MyTriv ERP',
    'website': 'https://github.com/fxagro/mytriv-erp',
    'license': 'LGPL-3',
    'depends': ['base', 'hr', 'base_rest_api'],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_custom_data.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}