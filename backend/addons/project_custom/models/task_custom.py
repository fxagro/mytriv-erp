# -*- coding: utf-8 -*-
"""
Custom Task Model

This module extends the base task functionality with additional fields
and methods for enhanced task management.
"""

from odoo import models, fields, api


class TaskCustom(models.Model):
    """Extended Task model with custom fields and functionality."""

    _name = 'project.task.custom'
    _description = 'Custom Task Extensions'
    _inherit = ['project.task']

    # Additional custom fields for enhanced task management
    task_priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Medium'),
        ('2', 'High'),
        ('3', 'Urgent')
    ], string='Task Priority', default='1', help='Priority level of the task')

    task_complexity = fields.Selection([
        ('simple', 'Simple'),
        ('moderate', 'Moderate'),
        ('complex', 'Complex'),
        ('expert', 'Expert Level')
    ], string='Task Complexity', help='Complexity level of the task')

    estimated_hours = fields.Float(
        string='Estimated Hours',
        help='Estimated time to complete the task in hours'
    )

    actual_hours = fields.Float(
        string='Actual Hours',
        compute='_compute_actual_hours',
        store=True,
        help='Actual time spent on the task'
    )

    remaining_hours = fields.Float(
        string='Remaining Hours',
        compute='_compute_remaining_hours',
        store=True,
        help='Remaining time to complete the task'
    )

    progress_percentage = fields.Float(
        string='Progress (%)',
        default=0.0,
        help='Task completion progress percentage'
    )

    task_category = fields.Selection([
        ('development', 'Development'),
        ('design', 'Design'),
        ('testing', 'Testing'),
        ('documentation', 'Documentation'),
        ('meeting', 'Meeting'),
        ('research', 'Research'),
        ('maintenance', 'Maintenance'),
        ('other', 'Other')
    ], string='Task Category', help='Category classification for the task')

    assigned_department = fields.Many2one(
        'hr.department',
        string='Assigned Department',
        help='HR department responsible for this task'
    )

    skills_required = fields.Many2many(
        'hr.skill',
        string='Skills Required',
        help='Skills required to complete this task'
    )

    deliverables = fields.One2many(
        'project.task.deliverable',
        'task_id',
        string='Deliverables',
        help='Expected deliverables for this task'
    )

    dependencies = fields.Many2many(
        'project.task',
        'task_dependency_rel',
        'task_id',
        'depends_on_task_id',
        string='Task Dependencies',
        help='Tasks that this task depends on'
    )

    dependent_tasks = fields.Many2many(
        'project.task',
        'task_dependency_rel',
        'depends_on_task_id',
        'task_id',
        string='Dependent Tasks',
        help='Tasks that depend on this task'
    )

    @api.depends('timesheet_ids.unit_amount')
    def _compute_actual_hours(self):
        """Compute actual hours from timesheets."""
        for task in self:
            task.actual_hours = sum(task.timesheet_ids.mapped('unit_amount'))

    @api.depends('estimated_hours', 'actual_hours', 'progress_percentage')
    def _compute_remaining_hours(self):
        """Compute remaining hours based on progress."""
        for task in self:
            if task.progress_percentage > 0:
                task.remaining_hours = task.estimated_hours * (1 - task.progress_percentage / 100)
            else:
                task.remaining_hours = task.estimated_hours

    def action_update_progress(self, progress):
        """Update task progress percentage."""
        self.write({'progress_percentage': progress})

    def action_add_dependency(self, depends_on_task_id):
        """Add a task dependency."""
        if depends_on_task_id not in self.dependencies.ids:
            self.write({'dependencies': [(4, depends_on_task_id)]})

    def action_remove_dependency(self, depends_on_task_id):
        """Remove a task dependency."""
        self.write({'dependencies': [(3, depends_on_task_id)]})

    def get_task_summary(self):
        """Get comprehensive task summary."""
        self.ensure_one()
        return {
            'task_name': self.name,
            'task_priority': self.task_priority,
            'task_complexity': self.task_complexity,
            'estimated_hours': self.estimated_hours,
            'actual_hours': self.actual_hours,
            'remaining_hours': self.remaining_hours,
            'progress_percentage': self.progress_percentage,
            'task_category': self.task_category,
            'assigned_department': self.assigned_department.name if self.assigned_department else None,
            'skills_required_count': len(self.skills_required),
            'deliverables_count': len(self.deliverables),
            'dependencies_count': len(self.dependencies),
            'dependent_tasks_count': len(self.dependent_tasks)
        }

    @api.model
    def get_tasks_by_priority(self, priority):
        """Get all tasks with specific priority."""
        return self.search([('task_priority', '=', priority)])

    @api.model
    def get_tasks_by_complexity(self, complexity):
        """Get all tasks with specific complexity."""
        return self.search([('task_complexity', '=', complexity)])

    @api.model
    def get_overdue_tasks(self):
        """Get all overdue tasks."""
        return self.search([
            ('date_deadline', '<', fields.Date.today()),
            ('stage_id.is_closed', '=', False)
        ])