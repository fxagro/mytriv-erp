# -*- coding: utf-8 -*-
"""
Custom Timesheet Model

This module extends timesheet functionality with enhanced tracking
and HR integration capabilities.
"""

from odoo import models, fields, api


class TimesheetCustom(models.Model):
    """Extended Timesheet model with custom fields and functionality."""

    _name = 'account.analytic.line.custom'
    _description = 'Custom Timesheet Extensions'
    _inherit = ['account.analytic.line']

    # Additional custom fields for enhanced timesheet management
    work_type = fields.Selection([
        ('billable', 'Billable'),
        ('non_billable', 'Non-billable'),
        ('overtime', 'Overtime'),
        ('training', 'Training'),
        ('meeting', 'Meeting'),
        ('research', 'Research')
    ], string='Work Type', help='Type of work performed')

    location = fields.Selection([
        ('office', 'Office'),
        ('home', 'Home'),
        ('client_site', 'Client Site'),
        ('remote', 'Remote')
    ], string='Work Location', help='Location where work was performed')

    productivity_rating = fields.Selection([
        ('1', 'Very Low'),
        ('2', 'Low'),
        ('3', 'Medium'),
        ('4', 'High'),
        ('5', 'Very High')
    ], string='Productivity Rating', help='Self-assessed productivity rating')

    overtime_hours = fields.Float(
        string='Overtime Hours',
        default=0.0,
        help='Number of overtime hours worked'
    )

    break_time = fields.Float(
        string='Break Time (hours)',
        default=0.0,
        help='Time taken for breaks during work'
    )

    client_feedback = fields.Text(
        string='Client Feedback',
        help='Feedback received from client about the work'
    )

    internal_notes = fields.Text(
        string='Internal Notes',
        help='Internal notes about the timesheet entry'
    )

    # HR integration fields
    employee_department = fields.Many2one(
        'hr.department',
        string='Employee Department',
        related='employee_id.department_id',
        store=True,
        help='Department of the employee'
    )

    employee_grade = fields.Many2one(
        'hr.payroll.grade',
        string='Employee Grade',
        related='employee_id.grade_id',
        store=True,
        help='Payroll grade of the employee'
    )

    hourly_cost = fields.Monetary(
        string='Hourly Cost',
        related='employee_id.hourly_cost',
        store=True,
        currency_field='company_currency',
        help='Hourly cost rate for the employee'
    )

    total_cost = fields.Monetary(
        string='Total Cost',
        compute='_compute_total_cost',
        store=True,
        currency_field='company_currency',
        help='Total cost for this timesheet entry'
    )

    @api.depends('unit_amount', 'hourly_cost')
    def _compute_total_cost(self):
        """Compute total cost for the timesheet entry."""
        for timesheet in self:
            timesheet.total_cost = timesheet.unit_amount * timesheet.hourly_cost

    def action_approve_timesheet(self):
        """Approve the timesheet entry."""
        self.write({'is_approved': True})

    def action_reject_timesheet(self):
        """Reject the timesheet entry."""
        self.write({'is_approved': False})

    def get_timesheet_summary(self):
        """Get comprehensive timesheet summary."""
        self.ensure_one()
        return {
            'employee_name': self.employee_id.name,
            'project_name': self.project_id.name if self.project_id else None,
            'task_name': self.task_id.name if self.task_id else None,
            'date': self.date,
            'unit_amount': self.unit_amount,
            'work_type': self.work_type,
            'location': self.location,
            'productivity_rating': self.productivity_rating,
            'hourly_cost': self.hourly_cost,
            'total_cost': self.total_cost,
            'is_approved': self.is_approved
        }

    @api.model
    def get_timesheets_by_employee(self, employee_id, start_date=None, end_date=None):
        """Get timesheets for a specific employee in date range."""
        domain = [('employee_id', '=', employee_id)]
        if start_date:
            domain.append(('date', '>=', start_date))
        if end_date:
            domain.append(('date', '<=', end_date))

        return self.search(domain)

    @api.model
    def get_timesheets_by_project(self, project_id, start_date=None, end_date=None):
        """Get timesheets for a specific project in date range."""
        domain = [('project_id', '=', project_id)]
        if start_date:
            domain.append(('date', '>=', start_date))
        if end_date:
            domain.append(('date', '<=', end_date))

        return self.search(domain)

    @api.model
    def get_unapproved_timesheets(self):
        """Get all unapproved timesheets."""
        return self.search([('is_approved', '=', False)])

    @api.model
    def get_overtime_timesheets(self, start_date=None, end_date=None):
        """Get timesheets with overtime hours."""
        domain = [('overtime_hours', '>', 0)]
        if start_date:
            domain.append(('date', '>=', start_date))
        if end_date:
            domain.append(('date', '<=', end_date))

        return self.search(domain)