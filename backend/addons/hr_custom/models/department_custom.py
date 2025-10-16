# -*- coding: utf-8 -*-
"""
Custom Department Model

This module extends the base HR department functionality with additional fields
and methods for enhanced department management.
"""

from odoo import models, fields, api


class DepartmentCustom(models.Model):
    """Extended Department model with custom fields and functionality."""

    _name = 'hr.department.custom'
    _description = 'Custom Department Extensions'
    _inherit = ['hr.department']

    # Additional custom fields for enhanced department management
    department_code = fields.Char(
        string='Department Code',
        required=True,
        help='Unique code for the department'
    )

    department_type = fields.Selection([
        ('operational', 'Operational'),
        ('support', 'Support'),
        ('administrative', 'Administrative'),
        ('executive', 'Executive'),
        ('project', 'Project-based')
    ], string='Department Type', help='Type classification for the department')

    budget_allocated = fields.Monetary(
        string='Budget Allocated',
        currency_field='company_currency',
        help='Annual budget allocated for this department'
    )

    budget_used = fields.Monetary(
        string='Budget Used',
        currency_field='company_currency',
        compute='_compute_budget_used',
        store=True,
        help='Budget used by this department'
    )

    budget_remaining = fields.Monetary(
        string='Budget Remaining',
        currency_field='company_currency',
        compute='_compute_budget_remaining',
        store=True,
        help='Remaining budget for this department'
    )

    manager_id = fields.Many2one(
        'hr.employee',
        string='Department Manager',
        help='Employee who manages this department'
    )

    parent_department_id = fields.Many2one(
        'hr.department',
        string='Parent Department',
        help='Parent department in organizational hierarchy'
    )

    location = fields.Char(
        string='Location',
        help='Physical location of the department'
    )

    cost_center = fields.Char(
        string='Cost Center',
        help='Cost center code for accounting purposes'
    )

    # Employee statistics
    total_employees = fields.Integer(
        string='Total Employees',
        compute='_compute_employee_counts',
        store=True,
        help='Total number of employees in this department'
    )

    active_employees = fields.Integer(
        string='Active Employees',
        compute='_compute_employee_counts',
        store=True,
        help='Number of active employees'
    )

    # Performance metrics
    average_performance_rating = fields.Float(
        string='Average Performance Rating',
        compute='_compute_performance_metrics',
        store=True,
        help='Average performance rating of department employees'
    )

    total_salary_cost = fields.Monetary(
        string='Total Salary Cost',
        currency_field='company_currency',
        compute='_compute_salary_cost',
        store=True,
        help='Total annual salary cost for the department'
    )

    @api.depends('budget_allocated', 'budget_used')
    def _compute_budget_remaining(self):
        """Compute remaining budget."""
        for department in self:
            department.budget_remaining = department.budget_allocated - department.budget_used

    @api.depends('employee_ids')
    def _compute_employee_counts(self):
        """Compute employee counts for the department."""
        for department in self:
            employees = department.employee_ids
            department.total_employees = len(employees)
            department.active_employees = len(employees.filtered(lambda e: e.active))

    @api.depends('employee_ids')
    def _compute_performance_metrics(self):
        """Compute performance metrics."""
        for department in self:
            employees = department.employee_ids.filtered(lambda e: e.active)
            if employees:
                # This would typically involve performance appraisal data
                # For now, using a default calculation
                department.average_performance_rating = 3.5
            else:
                department.average_performance_rating = 0.0

    @api.depends('employee_ids')
    def _compute_salary_cost(self):
        """Compute total salary cost."""
        for department in self:
            employees = department.employee_ids.filtered(lambda e: e.active)
            total_cost = sum(emp.contract_id.wage * 12 for emp in employees if emp.contract_id)
            department.total_salary_cost = total_cost

    def _compute_budget_used(self):
        """Compute budget used (simplified calculation)."""
        for department in self:
            # This would typically involve complex budget tracking
            # For now, using a percentage of allocated budget
            department.budget_used = department.budget_allocated * 0.6  # 60% used

    def action_update_budget(self, budget_amount):
        """Update department budget."""
        self.write({'budget_allocated': budget_amount})

    def get_department_summary(self):
        """Get comprehensive department summary."""
        self.ensure_one()
        return {
            'department_name': self.name,
            'department_code': self.department_code,
            'department_type': self.department_type,
            'manager_name': self.manager_id.name if self.manager_id else None,
            'parent_department': self.parent_department_id.name if self.parent_department_id else None,
            'location': self.location,
            'cost_center': self.cost_center,
            'total_employees': self.total_employees,
            'active_employees': self.active_employees,
            'budget_allocated': self.budget_allocated,
            'budget_used': self.budget_used,
            'budget_remaining': self.budget_remaining,
            'total_salary_cost': self.total_salary_cost,
            'average_performance_rating': self.average_performance_rating
        }

    @api.model
    def get_departments_by_type(self, department_type):
        """Get all departments of specific type."""
        return self.search([('department_type', '=', department_type)])

    @api.model
    def get_large_departments(self, min_employees=10):
        """Get departments with minimum number of employees."""
        # This would need a more complex query in real implementation
        return self.search([]).filtered(lambda d: d.total_employees >= min_employees)

    @api.model
    def get_department_hierarchy(self):
        """Get department organizational hierarchy."""
        departments = self.search([('parent_department_id', '=', False)])
        hierarchy = []

        for dept in departments:
            hierarchy.append({
                'department': dept.get_department_summary(),
                'children': self._get_child_departments(dept)
            })

        return hierarchy

    def _get_child_departments(self, parent_dept):
        """Get child departments recursively."""
        children = self.search([('parent_department_id', '=', parent_dept.id)])
        result = []

        for child in children:
            result.append({
                'department': child.get_department_summary(),
                'children': self._get_child_departments(child)
            })

        return result