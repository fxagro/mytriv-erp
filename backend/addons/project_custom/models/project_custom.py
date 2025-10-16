# -*- coding: utf-8 -*-
"""
Custom Project Model

This module extends the base project functionality with additional fields
and methods for enhanced project management linked to HR.
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ProjectCustom(models.Model):
    """Extended Project model with custom fields and functionality."""

    _name = 'project.project.custom'
    _description = 'Custom Project Extensions'
    _inherit = ['project.project']

    # Additional custom fields for enhanced project management
    project_type = fields.Selection([
        ('internal', 'Internal Project'),
        ('client', 'Client Project'),
        ('maintenance', 'Maintenance Project'),
        ('development', 'Development Project'),
        ('research', 'Research Project')
    ], string='Project Type', help='Type classification for the project')

    project_priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], string='Priority', default='medium', help='Priority level of the project')

    project_health = fields.Selection([
        ('green', 'On Track'),
        ('yellow', 'At Risk'),
        ('red', 'Critical'),
        ('blue', 'Completed')
    ], string='Project Health', default='green', compute='_compute_project_health', store=True)

    budget_allocated = fields.Monetary(
        string='Budget Allocated',
        currency_field='company_currency',
        help='Total budget allocated for this project'
    )

    budget_used = fields.Monetary(
        string='Budget Used',
        currency_field='company_currency',
        compute='_compute_budget_used',
        store=True,
        help='Total budget used so far'
    )

    budget_remaining = fields.Monetary(
        string='Budget Remaining',
        currency_field='company_currency',
        compute='_compute_budget_remaining',
        store=True,
        help='Remaining budget for the project'
    )

    project_manager_id = fields.Many2one(
        'res.users',
        string='Project Manager',
        help='User responsible for managing this project'
    )

    client_id = fields.Many2one(
        'res.partner',
        string='Client',
        domain=[('customer_rank', '>', 0)],
        help='Client/partner for this project'
    )

    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        help='HR department responsible for this project'
    )

    team_members = fields.Many2many(
        'hr.employee',
        string='Team Members',
        help='Employees assigned to this project'
    )

    planned_start_date = fields.Date(
        string='Planned Start Date',
        help='Planned start date for the project'
    )

    planned_end_date = fields.Date(
        string='Planned End Date',
        help='Planned end date for the project'
    )

    actual_start_date = fields.Date(
        string='Actual Start Date',
        help='Actual start date of the project'
    )

    completion_percentage = fields.Float(
        string='Completion Percentage',
        compute='_compute_completion_percentage',
        store=True,
        help='Overall completion percentage based on tasks'
    )

    # Computed fields for analytics
    total_tasks = fields.Integer(
        string='Total Tasks',
        compute='_compute_task_counts',
        store=True,
        help='Total number of tasks in the project'
    )

    completed_tasks = fields.Integer(
        string='Completed Tasks',
        compute='_compute_task_counts',
        store=True,
        help='Number of completed tasks'
    )

    overdue_tasks = fields.Integer(
        string='Overdue Tasks',
        compute='_compute_task_counts',
        store=True,
        help='Number of overdue tasks'
    )

    total_timesheet_hours = fields.Float(
        string='Total Timesheet Hours',
        compute='_compute_timesheet_hours',
        store=True,
        help='Total hours logged in timesheets'
    )

    @api.depends('task_ids.stage_id')
    def _compute_task_counts(self):
        """Compute task counts for the project."""
        for project in self:
            tasks = project.task_ids

            project.total_tasks = len(tasks)
            project.completed_tasks = len(tasks.filtered(lambda t: t.stage_id.is_closed))
            project.overdue_tasks = len(tasks.filtered(lambda t: t.date_deadline and t.date_deadline < fields.Date.today() and not t.stage_id.is_closed))

    @api.depends('budget_allocated', 'budget_used')
    def _compute_budget_remaining(self):
        """Compute remaining budget."""
        for project in self:
            project.budget_remaining = project.budget_allocated - project.budget_used

    @api.depends('task_ids')
    def _compute_budget_used(self):
        """Compute budget used based on timesheet costs."""
        for project in self:
            # Calculate based on timesheet entries
            timesheets = self.env['account.analytic.line'].search([
                ('project_id', '=', project.id)
            ])

            total_cost = sum(line.unit_amount * line.employee_id.hourly_cost for line in timesheets if line.employee_id.hourly_cost)
            project.budget_used = total_cost

    @api.depends('task_ids.stage_id')
    def _compute_completion_percentage(self):
        """Compute overall project completion percentage."""
        for project in self:
            if project.total_tasks > 0:
                project.completion_percentage = (project.completed_tasks / project.total_tasks) * 100
            else:
                project.completion_percentage = 0.0

    @api.depends('total_tasks', 'completed_tasks', 'overdue_tasks')
    def _compute_project_health(self):
        """Compute project health status."""
        for project in self:
            if project.completion_percentage >= 100:
                project.project_health = 'blue'
            elif project.overdue_tasks > 0:
                project.project_health = 'red'
            elif project.completion_percentage < 50 and project.total_tasks > 0:
                project.project_health = 'yellow'
            else:
                project.project_health = 'green'

    @api.depends('task_ids')
    def _compute_timesheet_hours(self):
        """Compute total timesheet hours for the project."""
        for project in self:
            timesheets = self.env['account.analytic.line'].search([
                ('project_id', '=', project.id)
            ])
            project.total_timesheet_hours = sum(timesheets.mapped('unit_amount'))

    def action_start_project(self):
        """Mark project as started."""
        self.write({'actual_start_date': fields.Date.today()})

    def action_complete_project(self):
        """Mark project as completed."""
        self.write({
            'stage_id': self.env['project.project.stage'].search([('is_closed', '=', True)], limit=1).id,
            'project_health': 'blue'
        })

    def action_add_team_member(self, employee_id):
        """Add an employee to the project team."""
        employee = self.env['hr.employee'].browse(employee_id)
        if employee not in self.team_members:
            self.write({'team_members': [(4, employee_id)]})

    def action_remove_team_member(self, employee_id):
        """Remove an employee from the project team."""
        self.write({'team_members': [(3, employee_id)]})

    def get_project_summary(self):
        """Get comprehensive project summary."""
        self.ensure_one()
        return {
            'project_name': self.name,
            'project_type': self.project_type,
            'project_priority': self.project_priority,
            'project_health': self.project_health,
            'completion_percentage': self.completion_percentage,
            'total_tasks': self.total_tasks,
            'completed_tasks': self.completed_tasks,
            'overdue_tasks': self.overdue_tasks,
            'budget_allocated': self.budget_allocated,
            'budget_used': self.budget_used,
            'budget_remaining': self.budget_remaining,
            'total_timesheet_hours': self.total_timesheet_hours,
            'planned_start_date': self.planned_start_date,
            'planned_end_date': self.planned_end_date,
            'actual_start_date': self.actual_start_date,
            'team_members_count': len(self.team_members)
        }

    @api.model
    def get_projects_by_health(self, health_status):
        """Get all projects with specific health status."""
        return self.search([('project_health', '=', health_status)])

    @api.model
    def get_projects_by_manager(self, manager_id):
        """Get all projects managed by a specific user."""
        return self.search([('project_manager_id', '=', manager_id)])

    @api.model
    def get_overdue_projects(self):
        """Get projects with overdue tasks."""
        return self.search([('overdue_tasks', '>', 0)])