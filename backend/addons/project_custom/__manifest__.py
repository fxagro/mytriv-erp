# -*- coding: utf-8 -*-
{
    'name': 'Project Custom',
    'version': '17.0.1.0.0',
    'category': 'Project Management',
    'summary': 'Custom project management extensions for MyTriv ERP',
    'description': """
        Custom project management addon providing enhanced task management,
        timesheet integration, and project stages linked to HR for improved project operations.
    """,
    'author': 'MyTriv ERP',
    'website': 'https://github.com/fxagro/mytriv-erp',
    'license': 'LGPL-3',
    'depends': ['base', 'project', 'hr', 'base_rest_api'],
    'data': [
        'security/ir.model.access.csv',
        'data/project_custom_data.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}