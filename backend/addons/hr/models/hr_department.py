# -*- coding: utf-8 -*-
"""
Department Management Model for MyTriv ERP

This module handles department and organizational structure.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class HrDepartment(models.Model):
    """Department model for MyTriv ERP"""

    _name = 'hr.department'
    _description = 'Department'
    _parent_name = 'parent_id'
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'parent_id, name'

    name = fields.Char(
        string='Department Name',
        required=True,
        translate=True,
        help='Name of the department'
    )

    complete_name = fields.Char(
        string='Complete Name',
        compute='_compute_complete_name',
        store=True,
        help='Complete department name with parent hierarchy'
    )

    # Hierarchy
    parent_id = fields.Many2one(
        'hr.department',
        string='Parent Department',
        index=True,
        ondelete='cascade',
        help='Parent department'
    )

    child_ids = fields.One2many(
        'hr.department',
        'parent_id',
        string='Child Departments',
        help='Child departments'
    )

    # Management
    manager_id = fields.Many2one(
        'hr.employee',
        string='Department Manager',
        domain=[('employee_status', '=', 'active')],
        help='Department manager'
    )

    # Contact Information
    department_head = fields.Char(
        string='Department Head',
        help='Name of department head'
    )

    phone = fields.Char(
        string='Phone',
        help='Department phone number'
    )

    email = fields.Char(
        string='Email',
        help='Department email address'
    )

    # Location
    location = fields.Char(
        string='Location',
        help='Department location or office'
    )

    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    # Statistics
    employee_count = fields.Integer(
        string='Employee Count',
        compute='_compute_employee_count',
        help='Number of employees in this department'
    )

    total_salary = fields.Float(
        string='Total Salary',
        compute='_compute_total_salary',
        help='Total salary of all employees in this department'
    )

    # Budget
    budget = fields.Float(
        string='Department Budget',
        help='Annual budget for this department'
    )

    spent_budget = fields.Float(
        string='Spent Budget',
        compute='_compute_spent_budget',
        help='Amount spent from department budget'
    )

    # Description
    description = fields.Text(
        string='Description',
        translate=True,
        help='Description of the department'
    )

    # Status
    active = fields.Boolean(
        string='Active',
        default=True,
        help='If unchecked, this department will be archived'
    )

    # Color for UI
    color = fields.Integer(
        string='Color Index',
        help='Color for department in UI'
    )

    @api.depends('name', 'parent_id')
    def _compute_complete_name(self):
        """Compute complete department name with hierarchy"""
        for department in self:
            if department.parent_id:
                department.complete_name = f"{department.parent_id.complete_name} / {department.name}"
            else:
                department.complete_name = department.name

    @api.depends('employee_ids')
    def _compute_employee_count(self):
        """Compute number of employees in department"""
        for department in self:
            department.employee_count = len(department.employee_ids)

    @api.depends('employee_ids.basic_salary')
    def _compute_total_salary(self):
        """Compute total salary of department employees"""
        for department in self:
            total = sum(emp.basic_salary for emp in department.employee_ids if emp.basic_salary)
            department.total_salary = total

    @api.depends('expense_ids.amount')
    def _compute_spent_budget(self):
        """Compute spent budget from expenses"""
        for department in self:
            total_spent = sum(expense.amount for expense in department.expense_ids if expense.state == 'approved')
            department.spent_budget = total_spent

    @api.constrains('parent_id')
    def _check_parent_id(self):
        """Prevent recursive hierarchy"""
        if not self._check_recursion():
            raise ValidationError(_("You cannot create recursive departments"))

    def name_get(self):
        """Get department name with hierarchy"""
        result = []
        for department in self:
            name = department.complete_name
            result.append((department.id, name))
        return result

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """Search departments by name"""
        if args is None:
            args = []

        domain = args + ['|', ('name', operator, name), ('complete_name', operator, name)]
        return self.search(domain, limit=limit).name_get()

    def action_view_employees(self):
        """View employees in this department"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Department Employees'),
            'res_model': 'hr.employee',
            'view_mode': 'tree,form',
            'domain': [('department_id', '=', self.id)],
            'context': {'default_department_id': self.id}
        }

    def action_view_subdepartments(self):
        """View sub-departments"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sub-departments'),
            'res_model': 'hr.department',
            'view_mode': 'tree,form',
            'domain': [('parent_id', '=', self.id)],
            'context': {'default_parent_id': self.id}
        }

    def toggle_active(self):
        """Toggle department active status"""
        for department in self:
            department.active = not department.active

    # Budget management methods
    def action_request_budget(self):
        """Request budget allocation"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Request Budget'),
            'res_model': 'hr.department.budget',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_department_id': self.id}
        }

    def _get_budget_status(self):
        """Get budget status"""
        self.ensure_one()
        if self.spent_budget > self.budget:
            return 'over_budget'
        elif self.spent_budget > (self.budget * 0.8):
            return 'warning'
        else:
            return 'normal'


class HrJob(models.Model):
    """Job position model for MyTriv ERP"""

    _name = 'hr.job'
    _description = 'Job Position'

    name = fields.Char(
        string='Job Title',
        required=True,
        translate=True,
        help='Job position title'
    )

    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        help='Department for this job position'
    )

    # Job Details
    job_description = fields.Html(
        string='Job Description',
        help='Detailed job description'
    )

    requirements = fields.Html(
        string='Requirements',
        help='Job requirements and qualifications'
    )

    # Employment Details
    employee_type = fields.Selection([
        ('permanent', 'Permanent'),
        ('contract', 'Contract'),
        ('intern', 'Intern'),
        ('consultant', 'Consultant'),
    ], string='Employment Type', default='permanent')

    contract_type = fields.Selection([
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
    ], string='Contract Type', default='full_time')

    # Salary Information
    min_salary = fields.Float(
        string='Minimum Salary',
        help='Minimum salary for this position'
    )

    max_salary = fields.Float(
        string='Maximum Salary',
        help='Maximum salary for this position'
    )

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('closed', 'Closed'),
    ], string='Status', default='draft')

    # Statistics
    employee_count = fields.Integer(
        string='Employee Count',
        compute='_compute_employee_count',
        help='Number of employees in this position'
    )

    no_of_recruitment = fields.Integer(
        string='Expected New Employees',
        help='Number of new employees expected for this position'
    )

    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    @api.depends('employee_ids')
    def _compute_employee_count(self):
        """Compute number of employees in this job position"""
        for job in self:
            job.employee_count = len(job.employee_ids)

    def action_open_job(self):
        """Open job position for recruitment"""
        self.write({'state': 'open'})

    def action_close_job(self):
        """Close job position"""
        self.write({'state': 'closed'})

    def action_view_employees(self):
        """View employees in this job position"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Job Position Employees'),
            'res_model': 'hr.employee',
            'view_mode': 'tree,form',
            'domain': [('job_id', '=', self.id)],
            'context': {'default_job_id': self.id}
        }