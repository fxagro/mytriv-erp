# -*- coding: utf-8 -*-
"""
Payroll Management Model for MyTriv ERP

This module handles payroll processing and salary management.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class HrPayroll(models.Model):
    """Payroll model for MyTriv ERP"""

    _name = 'hr.payroll'
    _description = 'Payroll'

    name = fields.Char(
        string='Payroll Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )

    # Period
    date_from = fields.Date(
        string='Start Date',
        required=True,
        help='Payroll period start date'
    )

    date_to = fields.Date(
        string='End Date',
        required=True,
        help='Payroll period end date'
    )

    # Employees
    employee_ids = fields.Many2many(
        'hr.employee',
        string='Employees',
        help='Employees included in this payroll'
    )

    # Payroll Details
    total_gross = fields.Float(
        string='Total Gross',
        compute='_compute_totals',
        store=True,
        help='Total gross salary'
    )

    total_deductions = fields.Float(
        string='Total Deductions',
        compute='_compute_totals',
        store=True,
        help='Total deductions'
    )

    total_net = fields.Float(
        string='Total Net',
        compute='_compute_totals',
        store=True,
        help='Total net salary'
    )

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('computed', 'Computed'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft')

    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    @api.model
    def create(self, vals):
        """Create payroll with auto-generated reference"""
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self._generate_payroll_reference()

        return super(HrPayroll, self).create(vals)

    def _generate_payroll_reference(self):
        """Generate unique payroll reference"""
        sequence = self.env['ir.sequence'].search([
            ('code', '=', 'hr.payroll')
        ], limit=1)

        if sequence:
            return sequence.next_by_id()
        else:
            last_payroll = self.search([], order='id desc', limit=1)
            return f'PAY{(last_payroll.id + 1):04d}' if last_payroll else 'PAY0001'

    @api.depends('payslip_ids.gross_salary', 'payslip_ids.deductions', 'payslip_ids.net_salary')
    def _compute_totals(self):
        """Compute payroll totals"""
        for payroll in self:
            payslips = payroll.payslip_ids

            payroll.total_gross = sum(payslip.gross_salary for payslip in payslips)
            payroll.total_deductions = sum(payslip.deductions for payslip in payslips)
            payroll.total_net = sum(payslip.net_salary for payslip in payslips)

    def action_compute(self):
        """Compute payroll"""
        self.write({'state': 'computed'})

        # Create payslips for all employees
        for payroll in self:
            for employee in payroll.employee_ids:
                self._create_payslip(employee, payroll)

    def _create_payslip(self, employee, payroll):
        """Create payslip for employee"""
        # Calculate salary components
        basic_salary = employee.basic_salary or 0
        allowances = self._calculate_allowances(employee, payroll)
        overtime = self._calculate_overtime(employee, payroll)
        deductions = self._calculate_deductions(employee, payroll)

        gross_salary = basic_salary + allowances + overtime
        net_salary = gross_salary - deductions

        # Create payslip
        payslip = self.env['hr.payslip'].create({
            'employee_id': employee.id,
            'payroll_id': payroll.id,
            'basic_salary': basic_salary,
            'allowances': allowances,
            'overtime': overtime,
            'deductions': deductions,
            'gross_salary': gross_salary,
            'net_salary': net_salary,
        })

        return payslip

    def _calculate_allowances(self, employee, payroll):
        """Calculate employee allowances"""
        # This would contain logic for various allowances
        return 0.0

    def _calculate_overtime(self, employee, payroll):
        """Calculate overtime pay"""
        # This would contain overtime calculation logic
        return 0.0

    def _calculate_deductions(self, employee, payroll):
        """Calculate employee deductions"""
        # This would contain deduction calculation logic
        return 0.0

    def action_confirm(self):
        """Confirm payroll"""
        self.write({'state': 'confirmed'})

    def action_paid(self):
        """Mark payroll as paid"""
        self.write({'state': 'paid'})

    def action_cancel(self):
        """Cancel payroll"""
        self.write({'state': 'cancelled'})


class HrPayslip(models.Model):
    """Payslip model for MyTriv ERP"""

    _name = 'hr.payslip'
    _description = 'Payslip'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True
    )

    payroll_id = fields.Many2one(
        'hr.payroll',
        string='Payroll',
        required=True
    )

    # Salary Components
    basic_salary = fields.Float(
        string='Basic Salary',
        help='Basic salary amount'
    )

    allowances = fields.Float(
        string='Allowances',
        help='Total allowances'
    )

    overtime = fields.Float(
        string='Overtime',
        help='Overtime pay'
    )

    deductions = fields.Float(
        string='Deductions',
        help='Total deductions'
    )

    # Totals
    gross_salary = fields.Float(
        string='Gross Salary',
        compute='_compute_gross_salary',
        store=True,
        help='Total gross salary'
    )

    net_salary = fields.Float(
        string='Net Salary',
        compute='_compute_net_salary',
        store=True,
        help='Net salary after deductions'
    )

    # Payment Information
    payment_date = fields.Date(
        string='Payment Date',
        help='Date when salary was paid'
    )

    payment_method = fields.Selection([
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('check', 'Check'),
    ], string='Payment Method', default='bank_transfer')

    bank_account_id = fields.Many2one(
        'res.partner.bank',
        string='Bank Account',
        help='Bank account for salary payment'
    )

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('computed', 'Computed'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft')

    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='employee_id.company_id',
        store=True
    )

    @api.depends('basic_salary', 'allowances', 'overtime')
    def _compute_gross_salary(self):
        """Compute gross salary"""
        for payslip in self:
            payslip.gross_salary = (
                payslip.basic_salary +
                payslip.allowances +
                payslip.overtime
            )

    @api.depends('gross_salary', 'deductions')
    def _compute_net_salary(self):
        """Compute net salary"""
        for payslip in self:
            payslip.net_salary = payslip.gross_salary - payslip.deductions

    def action_compute(self):
        """Compute payslip"""
        self.write({'state': 'computed'})

    def action_paid(self):
        """Mark payslip as paid"""
        self.write({
            'state': 'paid',
            'payment_date': datetime.now().date()
        })

    def action_cancel(self):
        """Cancel payslip"""
        self.write({'state': 'cancelled'})

    def print_payslip(self):
        """Print payslip report"""
        return self.env.ref('hr.action_report_payslip').report_action(self)


class HrPayrollStructure(models.Model):
    """Payroll structure model"""

    _name = 'hr.payroll.structure'
    _description = 'Payroll Structure'

    name = fields.Char(
        string='Structure Name',
        required=True,
        help='Name of the payroll structure'
    )

    code = fields.Char(
        string='Code',
        required=True,
        help='Unique code for payroll structure'
    )

    # Salary Rules
    rule_ids = fields.Many2many(
        'hr.salary.rule',
        string='Salary Rules',
        help='Salary rules in this structure'
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


class HrSalaryRule(models.Model):
    """Salary rule model"""

    _name = 'hr.salary.rule'
    _description = 'Salary Rule'

    name = fields.Char(
        string='Rule Name',
        required=True,
        help='Name of the salary rule'
    )

    code = fields.Char(
        string='Code',
        required=True,
        help='Unique code for salary rule'
    )

    category_id = fields.Many2one(
        'hr.salary.rule.category',
        string='Category',
        required=True,
        help='Category for this salary rule'
    )

    condition_python = fields.Text(
        string='Python Condition',
        help='Python condition for applying this rule'
    )

    amount_python = fields.Text(
        string='Python Amount',
        help='Python code for calculating amount'
    )

    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Rule evaluation sequence'
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )


class HrSalaryRuleCategory(models.Model):
    """Salary rule category model"""

    _name = 'hr.salary.rule.category'
    _description = 'Salary Rule Category'

    name = fields.Char(
        string='Category Name',
        required=True,
        translate=True
    )

    code = fields.Char(
        string='Code',
        required=True
    )

    parent_id = fields.Many2one(
        'hr.salary.rule.category',
        string='Parent Category'
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )