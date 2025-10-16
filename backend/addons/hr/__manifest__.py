# -*- coding: utf-8 -*-
{
    'name': 'Human Resources',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Human Resources Management',
    'description': """
        Human Resources Management module for MyTriv ERP.

        This module provides:
        - Employee management and information
        - Department and job position management
        - Attendance tracking and time management
        - Leave and absence management
        - Payroll and salary management
        - Recruitment and applicant tracking
        - Performance evaluation and reviews
        - Employee contracts and documents
        - HR reports and analytics
    """,
    'author': 'MyTriv ERP',
    'website': 'https://mytriv-erp.com',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/hr_security.xml',
        'security/ir.model.access.csv',
        'views/hr_menus.xml',
        'views/hr_employee_views.xml',
        'views/hr_department_views.xml',
        'views/hr_attendance_views.xml',
        'views/hr_leave_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_recruitment_views.xml',
        'views/hr_payroll_views.xml',
        'data/hr_data.xml',
        'data/hr_sequence.xml',
    ],
    'demo': [
        'demo/hr_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}