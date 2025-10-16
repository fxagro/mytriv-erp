# -*- coding: utf-8 -*-
"""
Custom Employee Model

This module extends the base employee functionality with additional fields
and methods for enhanced employee profile management.
"""

from odoo import models, fields, api


class EmployeeCustom(models.Model):
    """Extended Employee model with custom fields and functionality."""

    _name = 'hr.employee.custom'
    _description = 'Custom Employee Extensions'
    _inherit = ['hr.employee']

    # Additional custom fields for enhanced employee management
    employee_code = fields.Char(
        string='Employee Code',
        required=True,
        help='Unique employee identification code'
    )

    employee_grade = fields.Selection([
        ('junior', 'Junior'),
        ('senior', 'Senior'),
        ('lead', 'Lead'),
        ('manager', 'Manager'),
        ('senior_manager', 'Senior Manager'),
        ('director', 'Director'),
        ('executive', 'Executive')
    ], string='Employee Grade', help='Employee level/grade in organization')

    employment_type = fields.Selection([
        ('permanent', 'Permanent'),
        ('contract', 'Contract'),
        ('intern', 'Intern'),
        ('consultant', 'Consultant'),
        ('temporary', 'Temporary')
    ], string='Employment Type', default='permanent', help='Type of employment')

    work_schedule = fields.Selection([
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('flexible', 'Flexible'),
        ('shift', 'Shift Work')
    ], string='Work Schedule', default='full_time', help='Work schedule type')

    # Financial information
    hourly_rate = fields.Monetary(
        string='Hourly Rate',
        currency_field='currency_id',
        help='Hourly rate for the employee'
    )

    monthly_salary = fields.Monetary(
        string='Monthly Salary',
        currency_field='currency_id',
        compute='_compute_monthly_salary',
        store=True,
        help='Monthly salary based on hourly rate'
    )

    annual_salary = fields.Monetary(
        string='Annual Salary',
        currency_field='currency_id',
        compute='_compute_annual_salary',
        store=True,
        help='Annual salary including benefits'
    )

    # Skills and certifications
    skills = fields.Many2many(
        'hr.skill',
        string='Skills',
        help='Employee skills and competencies'
    )

    certifications = fields.One2many(
        'hr.employee.certification',
        'employee_id',
        string='Certifications',
        help='Professional certifications and licenses'
    )

    languages = fields.One2many(
        'hr.employee.language',
        'employee_id',
        string='Languages',
        help='Languages spoken by the employee'
    )

    # Performance and development
    performance_rating = fields.Selection([
        ('1', 'Below Expectations'),
        ('2', 'Meets Expectations'),
        ('3', 'Exceeds Expectations'),
        ('4', 'Outstanding')
    ], string='Performance Rating', help='Current performance rating')

    last_appraisal_date = fields.Date(
        string='Last Appraisal Date',
        help='Date of last performance appraisal'
    )

    next_appraisal_date = fields.Date(
        string='Next Appraisal Date',
        help='Scheduled date for next performance appraisal'
    )

    training_hours = fields.Float(
        string='Training Hours (YTD)',
        default=0.0,
        help='Training hours completed year-to-date'
    )

    # Personal information
    emergency_contact_name = fields.Char(
        string='Emergency Contact Name',
        help='Name of emergency contact person'
    )

    emergency_contact_phone = fields.Char(
        string='Emergency Contact Phone',
        help='Phone number of emergency contact'
    )

    emergency_contact_relationship = fields.Char(
        string='Emergency Contact Relationship',
        help='Relationship to emergency contact'
    )

    blood_type = fields.Selection([
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-')
    ], string='Blood Type', help='Employee blood type for medical emergencies')

    dietary_restrictions = fields.Char(
        string='Dietary Restrictions',
        help='Special dietary requirements or restrictions'
    )

    @api.depends('hourly_rate')
    def _compute_monthly_salary(self):
        """Compute monthly salary from hourly rate."""
        for employee in self:
            if employee.hourly_rate:
                # Assuming 40 hours/week * 4.33 weeks/month
                employee.monthly_salary = employee.hourly_rate * 40 * 4.33
            else:
                employee.monthly_salary = 0.0

    @api.depends('monthly_salary')
    def _compute_annual_salary(self):
        """Compute annual salary from monthly salary."""
        for employee in self:
            employee.annual_salary = employee.monthly_salary * 12

    def action_update_performance_rating(self, rating):
        """Update employee performance rating."""
        self.write({
            'performance_rating': rating,
            'last_appraisal_date': fields.Date.today()
        })

    def action_schedule_appraisal(self, days=90):
        """Schedule next performance appraisal."""
        next_date = fields.Date.today() + timedelta(days=days)
        self.write({'next_appraisal_date': next_date})

    def get_employee_summary(self):
        """Get comprehensive employee summary."""
        self.ensure_one()
        return {
            'employee_name': self.name,
            'employee_code': self.employee_code,
            'employee_grade': self.employee_grade,
            'employment_type': self.employment_type,
            'work_schedule': self.work_schedule,
            'department': self.department_id.name if self.department_id else None,
            'job_title': self.job_title,
            'work_email': self.work_email,
            'work_phone': self.work_phone,
            'hourly_rate': self.hourly_rate,
            'monthly_salary': self.monthly_salary,
            'annual_salary': self.annual_salary,
            'performance_rating': self.performance_rating,
            'last_appraisal_date': self.last_appraisal_date,
            'next_appraisal_date': self.next_appraisal_date,
            'training_hours': self.training_hours,
            'skills_count': len(self.skills),
            'certifications_count': len(self.certifications),
            'active': self.active
        }

    @api.model
    def get_employees_by_grade(self, grade):
        """Get all employees of specific grade."""
        return self.search([('employee_grade', '=', grade)])

    @api.model
    def get_employees_by_department(self, department_id):
        """Get all employees in specific department."""
        return self.search([('department_id', '=', department_id)])

    @api.model
    def get_employees_due_appraisal(self):
        """Get employees due for performance appraisal."""
        today = fields.Date.today()
        return self.search([
            ('next_appraisal_date', '<=', today),
            ('active', '=', True)
        ])

    @api.model
    def get_high_performers(self):
        """Get employees with high performance ratings."""
        return self.search([
            ('performance_rating', 'in', ['3', '4']),
            ('active', '=', True)
        ])