# -*- coding: utf-8 -*-
"""
Contract Management Model for MyTriv ERP

This module handles employee contracts and employment terms.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class HrContract(models.Model):
    """Contract model for MyTriv ERP"""

    _name = 'hr.contract'
    _description = 'Employee Contract'

    name = fields.Char(
        string='Contract Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        help='Employee for this contract'
    )

    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        related='employee_id.department_id',
        store=True
    )

    job_id = fields.Many2one(
        'hr.job',
        string='Job Position',
        related='employee_id.job_id',
        store=True
    )

    # Contract Details
    contract_type = fields.Selection([
        ('permanent', 'Permanent'),
        ('fixed_term', 'Fixed Term'),
        ('probation', 'Probation'),
        ('internship', 'Internship'),
        ('consultant', 'Consultant'),
    ], string='Contract Type', default='permanent')

    date_start = fields.Date(
        string='Start Date',
        required=True,
        help='Contract start date'
    )

    date_end = fields.Date(
        string='End Date',
        help='Contract end date (for fixed term contracts)'
    )

    trial_date_end = fields.Date(
        string='Trial End Date',
        help='End date of trial period'
    )

    # Work Schedule
    working_hours = fields.Float(
        string='Working Hours per Week',
        default=40.0,
        help='Standard working hours per week'
    )

    work_location = fields.Char(
        string='Work Location',
        help='Employee work location'
    )

    # Salary Information
    wage = fields.Float(
        string='Wage',
        required=True,
        help='Employee wage'
    )

    wage_type = fields.Selection([
        ('monthly', 'Monthly'),
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
    ], string='Wage Type', default='monthly')

    # Benefits
    benefits = fields.Text(
        string='Benefits',
        help='Employee benefits description'
    )

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('pending', 'Pending'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft')

    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='employee_id.company_id',
        store=True
    )

    @api.model
    def create(self, vals):
        """Create contract with auto-generated reference"""
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self._generate_contract_reference()

        return super(HrContract, self).create(vals)

    def _generate_contract_reference(self):
        """Generate unique contract reference"""
        sequence = self.env['ir.sequence'].search([
            ('code', '=', 'hr.contract')
        ], limit=1)

        if sequence:
            return sequence.next_by_id()
        else:
            last_contract = self.search([], order='id desc', limit=1)
            return f'CON{(last_contract.id + 1):04d}' if last_contract else 'CON0001'

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        """Validate contract dates"""
        for contract in self:
            if contract.date_end and contract.date_end <= contract.date_start:
                raise ValidationError(_("End date must be after start date"))

    def action_activate(self):
        """Activate contract"""
        self.write({'state': 'active'})

    def action_expire(self):
        """Mark contract as expired"""
        self.write({'state': 'expired'})

    def action_cancel(self):
        """Cancel contract"""
        self.write({'state': 'cancelled'})

    def is_active(self):
        """Check if contract is active"""
        self.ensure_one()
        today = datetime.now().date()
        return (
            self.state == 'active' and
            self.date_start <= today and
            (not self.date_end or self.date_end >= today)
        )