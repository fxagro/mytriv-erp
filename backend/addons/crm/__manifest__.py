# -*- coding: utf-8 -*-
{
    'name': 'Customer Relationship Management',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Customer Relationship Management',
    'description': """
        Customer Relationship Management module for MyTriv ERP.

        This module provides:
        - Lead management and qualification
        - Opportunity tracking and pipeline management
        - Customer relationship management
        - Sales team management and performance
        - Marketing campaign integration
        - Customer communication and support
        - Activity scheduling and tracking
        - Sales forecasting and analytics
        - Customer segmentation and analysis
        - Partner and contact management
    """,
    'author': 'MyTriv ERP',
    'website': 'https://mytriv-erp.com',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/crm_security.xml',
        'security/ir.model.access.csv',
        'views/crm_menus.xml',
        'views/crm_lead_views.xml',
        'views/crm_opportunity_views.xml',
        'views/crm_partner_views.xml',
        'views/crm_activity_views.xml',
        'views/crm_team_views.xml',
        'views/crm_stage_views.xml',
        'data/crm_data.xml',
        'data/crm_sequence.xml',
    ],
    'demo': [
        'demo/crm_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}