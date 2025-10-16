# -*- coding: utf-8 -*-
"""
Employee Management Model for MyTriv ERP

This module handles employee information and management.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    """Employee model for MyTriv ERP"""

    _name = 'hr.employee'
    _description = 'Employee'
    _inherits = {'res.users': 'user_id'}

    # Relations
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        ondelete='cascade',
        help='Related user account'
    )

    # Personal Information
    employee_id = fields.Char(
        string='Employee ID',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )

    first_name = fields.Char(
        string='First Name',
        required=True,
        help='Employee first name'
    )

    last_name = fields.Char(
        string='Last Name',
        required=True,
        help='Employee last name'
    )

    middle_name = fields.Char(
        string='Middle Name',
        help='Employee middle name'
    )

    birth_date = fields.Date(
        string='Birth Date',
        help='Employee date of birth'
    )

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string='Gender')

    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
    ], string='Marital Status')

    blood_type = fields.Selection([
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ], string='Blood Type')

    # Contact Information
    personal_email = fields.Char(
        string='Personal Email',
        help='Personal email address'
    )

    personal_phone = fields.Char(
        string='Personal Phone',
        help='Personal phone number'
    )

    emergency_contact = fields.Char(
        string='Emergency Contact',
        help='Emergency contact person'
    )

    emergency_phone = fields.Char(
        string='Emergency Phone',
        help='Emergency contact phone'
    )

    # Address Information
    address_home = fields.Text(
        string='Home Address',
        help='Employee home address'
    )

    # Employment Information
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        help='Employee department'
    )

    job_id = fields.Many2one(
        'hr.job',
        string='Job Position',
        help='Employee job position'
    )

    manager_id = fields.Many2one(
        'hr.employee',
        string='Manager',
        help='Employee manager'
    )

    coach_id = fields.Many2one(
        'hr.employee',
        string='Coach',
        help='Employee coach/mentor'
    )

    # Employment Details
    employee_type = fields.Selection([
        ('permanent', 'Permanent'),
        ('contract', 'Contract'),
        ('intern', 'Intern'),
        ('consultant', 'Consultant'),
        ('temporary', 'Temporary'),
    ], string='Employee Type', default='permanent')

    contract_type = fields.Selection([
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('probation', 'Probation'),
    ], string='Contract Type', default='full_time')

    # Work Schedule
    work_location = fields.Char(
        string='Work Location',
        help='Employee work location'
    )

    work_phone = fields.Char(
        string='Work Phone',
        help='Employee work phone number'
    )

    # Employment Dates
    joining_date = fields.Date(
        string='Joining Date',
        help='Date when employee joined the company'
    )

    confirmation_date = fields.Date(
        string='Confirmation Date',
        help='Date when employee was confirmed'
    )

    resignation_date = fields.Date(
        string='Resignation Date',
        help='Date when employee resigned'
    )

    termination_date = fields.Date(
        string='Termination Date',
        help='Date when employment was terminated'
    )

    # Status
    employee_status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('resigned', 'Resigned'),
        ('terminated', 'Terminated'),
        ('retired', 'Retired'),
    ], string='Status', default='active')

    # Financial Information
    basic_salary = fields.Float(
        string='Basic Salary',
        help='Employee basic salary'
    )

    hourly_rate = fields.Float(
        string='Hourly Rate',
        help='Employee hourly rate'
    )

    bank_account_id = fields.Many2one(
        'res.partner.bank',
        string='Bank Account',
        help='Employee bank account for salary'
    )

    # Documents
    passport_id = fields.Char(
        string='Passport No',
        help='Employee passport number'
    )

    id_card = fields.Char(
        string='ID Card',
        help='Employee ID card number'
    )

    tax_id = fields.Char(
        string='Tax ID',
        help='Employee tax identification number'
    )

    # Education
    education_level = fields.Selection([
        ('high_school', 'High School'),
        ('diploma', 'Diploma'),
        ('bachelor', 'Bachelor Degree'),
        ('master', 'Master Degree'),
        ('doctorate', 'Doctorate'),
        ('other', 'Other'),
    ], string='Education Level')

    education_field = fields.Char(
        string='Field of Study',
        help='Field of study or major'
    )

    institution = fields.Char(
        string='Institution',
        help='Educational institution'
    )

    graduation_year = fields.Integer(
        string='Graduation Year',
        help='Year of graduation'
    )

    # Skills and Certifications
    skill_ids = fields.Many2many(
        'hr.skill',
        string='Skills'
    )

    certificate_ids = fields.One2many(
        'hr.certificate',
        'employee_id',
        string='Certificates'
    )

    # Notes
    notes = fields.Text(
        string='Notes',
        help='Internal notes about the employee'
    )

    # Statistics
    attendance_count = fields.Integer(
        string='Attendance Count',
        compute='_compute_attendance_count'
    )

    leave_count = fields.Integer(
        string='Leave Count',
        compute='_compute_leave_count'
    )

    @api.model
    def create(self, vals):
        """Create employee with auto-generated employee ID"""
        if vals.get('employee_id', _('New')) == _('New'):
            vals['employee_id'] = self._generate_employee_id()

        return super(HrEmployee, self).create(vals)

    def _generate_employee_id(self):
        """Generate unique employee ID"""
        sequence = self.env['ir.sequence'].search([
            ('code', '=', 'hr.employee')
        ], limit=1)

        if sequence:
            return sequence.next_by_id()
        else:
            # Fallback to simple numbering
            last_employee = self.search([], order='id desc', limit=1)
            return f'EMP{(last_employee.id + 1):04d}' if last_employee else 'EMP0001'

    @api.depends('attendance_ids')
    def _compute_attendance_count(self):
        """Compute attendance count"""
        for employee in self:
            employee.attendance_count = len(employee.attendance_ids)

    @api.depends('leave_ids')
    def _compute_leave_count(self):
        """Compute leave count"""
        for employee in self:
            employee.leave_count = len(employee.leave_ids)

    @api.constrains('birth_date')
    def _check_birth_date(self):
        """Validate birth date"""
        for employee in self:
            if employee.birth_date and employee.birth_date >= fields.Date.today():
                raise ValidationError(_("Birth date must be in the past"))

    def action_view_attendance(self):
        """View employee attendance"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Attendance'),
            'res_model': 'hr.attendance',
            'view_mode': 'tree,form',
            'domain': [('employee_id', '=', self.id)],
            'context': {'default_employee_id': self.id}
        }

    def action_view_leaves(self):
        """View employee leaves"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Leaves'),
            'res_model': 'hr.leave',
            'view_mode': 'tree,form',
            'domain': [('employee_id', '=', self.id)],
            'context': {'default_employee_id': self.id}
        }

    def action_employee_contract(self):
        """View employee contract"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Contract'),
            'res_model': 'hr.contract',
            'view_mode': 'form',
            'domain': [('employee_id', '=', self.id)],
            'context': {'default_employee_id': self.id}
        }

    def toggle_active(self):
        """Toggle employee active status"""
        for employee in self:
            if employee.employee_status == 'active':
                employee.employee_status = 'inactive'
            else:
                employee.employee_status = 'active'


class HrSkill(models.Model):
    """Employee skills model"""

    _name = 'hr.skill'
    _description = 'Employee Skills'

    name = fields.Char(
        string='Skill Name',
        required=True,
        help='Name of the skill'
    )

    skill_type = fields.Selection([
        ('technical', 'Technical'),
        ('soft', 'Soft Skill'),
        ('language', 'Language'),
        ('certification', 'Certification'),
    ], string='Skill Type', default='technical')

    description = fields.Text(
        string='Description',
        help='Description of the skill'
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )


class HrCertificate(models.Model):
    """Employee certificates model"""

    _name = 'hr.certificate'
    _description = 'Employee Certificates'

    name = fields.Char(
        string='Certificate Name',
        required=True,
        help='Name of the certificate'
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        ondelete='cascade'
    )

    certificate_number = fields.Char(
        string='Certificate Number',
        help='Certificate number or ID'
    )

    issuing_organization = fields.Char(
        string='Issuing Organization',
        help='Organization that issued the certificate'
    )

    issue_date = fields.Date(
        string='Issue Date',
        help='Date when certificate was issued'
    )

    expiry_date = fields.Date(
        string='Expiry Date',
        help='Date when certificate expires'
    )

    description = fields.Text(
        string='Description',
        help='Description of the certificate'
    )

    attachment_id = fields.Many2one(
        'ir.attachment',
        string='Attachment',
        help='Certificate document attachment'
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    @api.constrains('expiry_date')
    def _check_expiry_date(self):
        """Check if certificate is expired"""
        for certificate in self:
            if certificate.expiry_date and certificate.expiry_date < fields.Date.today():
                _logger.warning(f"Certificate {certificate.name} has expired")