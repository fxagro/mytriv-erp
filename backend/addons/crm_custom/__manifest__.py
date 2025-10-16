# -*- coding: utf-8 -*-
{
    'name': 'CRM Custom',
    'version': '17.0.1.0.0',
    'category': 'Customer Relationship Management',
    'summary': 'Custom CRM enhancements for MyTriv ERP',
    'description': """
        Custom CRM addon providing enhanced lead management, contact tracking,
        sales stages, and funnel analytics for improved customer relationship management.
    """,
    'author': 'MyTriv ERP',
    'website': 'https://github.com/fxagro/mytriv-erp',
    'license': 'LGPL-3',
    'depends': ['base', 'crm', 'base_rest_api'],
    'data': [
        'security/ir.model.access.csv',
        'data/crm_custom_data.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}