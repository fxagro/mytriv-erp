# -*- coding: utf-8 -*-
{
    'name': 'Base',
    'version': '17.0.1.0.0',
    'category': 'Hidden',
    'summary': 'Base Module for MyTriv ERP',
    'description': """
        Base module for MyTriv ERP system.

        This module provides:
        - Core models and fields
        - User management and authentication
        - Company configuration
        - Security groups and access rights
        - Basic business logic and utilities
        - Database structure foundation
    """,
    'author': 'MyTriv ERP',
    'website': 'https://mytriv-erp.com',
    'license': 'LGPL-3',
    'depends': [],
    'data': [
        'security/base_security.xml',
        'security/ir.model.access.csv',
        'views/base_menus.xml',
        'views/base_views.xml',
        'views/res_config_views.xml',
        'data/base_data.xml',
        'data/ir_cron_data.xml',
    ],
    'demo': [
        'demo/base_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': True,
    'pre_init_hook': 'pre_init_hook',
    'post_init_hook': 'post_init_hook',
}