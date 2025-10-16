# -*- coding: utf-8 -*-
{
    'name': 'Sales Management',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Sales Order Management',
    'description': """
        Sales Management module for MyTriv ERP.

        This module provides:
        - Sales order and quotation management
        - Customer and partner management
        - Product catalog and pricing
        - Sales team and commission management
        - Delivery and shipping management
        - Invoicing and payment tracking
        - Sales reporting and analytics
        - Discount and promotion management
        - Sales forecasting and planning
    """,
    'author': 'MyTriv ERP',
    'website': 'https://mytriv-erp.com',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/sale_security.xml',
        'security/ir.model.access.csv',
        'views/sale_menus.xml',
        'views/sale_order_views.xml',
        'views/sale_quotation_views.xml',
        'views/product_views.xml',
        'views/customer_views.xml',
        'views/delivery_views.xml',
        'views/invoice_views.xml',
        'data/sale_data.xml',
        'data/sale_sequence.xml',
    ],
    'demo': [
        'demo/sale_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}