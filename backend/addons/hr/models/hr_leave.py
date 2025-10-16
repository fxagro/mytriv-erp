# -*- coding: utf-8 -*-
"""
Leave Management Model for MyTriv ERP

This module handles employee leave requests and management.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class HrLeave(models.Model):
    """Leave model for MyTriv ERP"""

    _name = 'hr.leave'
    _description = 'Leave'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Relations
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        help='Employee requesting leave'
    )

    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        related='employee_id.department_id',
        store=True
    )

    manager_id = fields.Many2one(
        'hr.employee',
        string='Manager',
        related='employee_id.manager_id',
        store=True
    )

    # Leave Details
    leave_type_id = fields.Many2one(
        'hr.leave.type',
        string='Leave Type',
        required=True,
        help='Type of leave requested'
    )

    date_from = fields.Datetime(
        string='Start Date',
        required=True,
        help='Leave start date and time'
    )

    date_to = fields.Datetime(
        string='End Date',
        required=True,
        help='Leave end date and time'
    )

    number_of_days = fields.Float(
        string='Duration (Days)',
        compute='_compute_number_of_days',
        store=True,
        help='Number of days for this leave'
    )

    # Description
    description = fields.Text(
        string='Description',
        help='Reason for leave request'
    )

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('validate1', 'Validated'),
        ('validate2', 'Second Validation'),
        ('refuse', 'Refused'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', track_visibility='onchange')

    # Validation
    validated_by = fields.Many2one(
        'hr.employee',
        string='Validated By',
        help='Employee who validated this leave'
    )

    validated_date = fields.Datetime(
        string='Validation Date',
        help='Date when leave was validated'
    )

    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='employee_id.company_id',
        store=True
    )

    @api.depends('date_from', 'date_to')
    def _compute_number_of_days(self):
        """Compute number of leave days"""
        for leave in self:
            if leave.date_from and leave.date_to:
                delta = leave.date_to - leave.date_from
                leave.number_of_days = delta.days + 1
            else:
                leave.number_of_days = 0

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        """Validate leave dates"""
        for leave in self:
            if leave.date_from >= leave.date_to:
                raise ValidationError(_("End date must be after start date"))

            if leave.date_from < datetime.now():
                raise ValidationError(_("Leave cannot be in the past"))

    def action_confirm(self):
        """Confirm leave request"""
        self.write({'state': 'confirm'})

    def action_validate(self):
        """Validate leave request"""
        self.write({
            'state': 'validate1',
            'validated_by': self.env.user.employee_id.id,
            'validated_date': datetime.now()
        })

    def action_second_validate(self):
        """Second level validation"""
        self.write({'state': 'validate2'})

    def action_refuse(self):
        """Refuse leave request"""
        self.write({'state': 'refuse'})

    def action_cancel(self):
        """Cancel leave request"""
        self.write({'state': 'cancel'})

    def action_draft(self):
        """Set leave back to draft"""
        self.write({'state': 'draft'})

    @api.model
    def get_leave_balance(self, employee_id, leave_type_id=None):
        """Get leave balance for employee"""
        employee = self.env['hr.employee'].browse(employee_id)

        # Get leave allocations for employee
        allocations = self.env['hr.leave.allocation'].search([
            ('employee_id', '=', employee_id),
            ('state', '=', 'validate')
        ])

        if leave_type_id:
            allocations = allocations.filtered(lambda a: a.leave_type_id.id == leave_type_id)

        balance = {}
        for allocation in allocations:
            leave_type = allocation.leave_type_id.name
            if leave_type not in balance:
                balance[leave_type] = {
                    'allocated': 0,
                    'used': 0,
                    'remaining': 0
                }

            balance[leave_type]['allocated'] += allocation.number_of_days

            # Calculate used days
            used_leaves = self.search([
                ('employee_id', '=', employee_id),
                ('leave_type_id', '=', allocation.leave_type_id.id),
                ('state', '=', 'validate'),
                ('date_from', '>=', allocation.date_from),
                ('date_to', '<=', allocation.date_to)
            ])

            used = sum(leave.number_of_days for leave in used_leaves)
            balance[leave_type]['used'] = used
            balance[leave_type]['remaining'] = allocation.number_of_days - used

        return balance


class HrLeaveType(models.Model):
    """Leave type model"""

    _name = 'hr.leave.type'
    _description = 'Leave Type'

    name = fields.Char(
        string='Leave Type',
        required=True,
        translate=True,
        help='Name of the leave type'
    )

    code = fields.Char(
        string='Code',
        required=True,
        help='Unique code for leave type'
    )

    description = fields.Text(
        string='Description',
        help='Description of the leave type'
    )

    max_days = fields.Integer(
        string='Max Days',
        help='Maximum days allowed for this leave type'
    )

    requires_approval = fields.Boolean(
        string='Requires Approval',
        default=True,
        help='If true, leave requires approval'
    )

    requires_document = fields.Boolean(
        string='Requires Document',
        default=False,
        help='If true, leave requires supporting document'
    )

    color = fields.Integer(
        string='Color',
        help='Color for UI representation'
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )


class HrLeaveAllocation(models.Model):
    """Leave allocation model"""

    _name = 'hr.leave.allocation'
    _description = 'Leave Allocation'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True
    )

    leave_type_id = fields.Many2one(
        'hr.leave.type',
        string='Leave Type',
        required=True
    )

    number_of_days = fields.Float(
        string='Number of Days',
        required=True,
        help='Number of days allocated'
    )

    date_from = fields.Date(
        string='Start Date',
        required=True,
        help='Allocation start date'
    )

    date_to = fields.Date(
        string='End Date',
        required=True,
        help='Allocation end date'
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('validate', 'Validated'),
        ('refuse', 'Refused'),
    ], string='State', default='draft')

    notes = fields.Text(
        string='Notes'
    )

    def action_confirm(self):
        """Confirm allocation"""
        self.write({'state': 'confirm'})

    def action_validate(self):
        """Validate allocation"""
        self.write({'state': 'validate'})

    def action_refuse(self):
        """Refuse allocation"""
        self.write({'state': 'refuse'})