# -*- coding: utf-8 -*-
"""
Attendance Management Model for MyTriv ERP

This module handles employee attendance tracking and time management.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class HrAttendance(models.Model):
    """Attendance model for MyTriv ERP"""

    _name = 'hr.attendance'
    _description = 'Attendance'
    _order = 'check_in desc'

    # Relations
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        ondelete='cascade',
        help='Employee for this attendance record'
    )

    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        related='employee_id.department_id',
        store=True,
        help='Department of the employee'
    )

    # Check In/Out
    check_in = fields.Datetime(
        string='Check In',
        required=True,
        default=lambda self: datetime.now(),
        help='Date and time when employee checked in'
    )

    check_out = fields.Datetime(
        string='Check Out',
        help='Date and time when employee checked out'
    )

    # Work Duration
    worked_hours = fields.Float(
        string='Worked Hours',
        compute='_compute_worked_hours',
        store=True,
        help='Total hours worked'
    )

    # Attendance Status
    attendance_status = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('half_day', 'Half Day'),
        ('overtime', 'Overtime'),
    ], string='Status', compute='_compute_attendance_status', store=True)

    # Location (for remote work)
    check_in_location = fields.Char(
        string='Check In Location',
        help='Location where employee checked in'
    )

    check_out_location = fields.Char(
        string='Check Out Location',
        help='Location where employee checked out'
    )

    # IP Address tracking
    check_in_ip = fields.Char(
        string='Check In IP',
        help='IP address used for check in'
    )

    check_out_ip = fields.Char(
        string='Check Out IP',
        help='IP address used for check out'
    )

    # Notes
    notes = fields.Text(
        string='Notes',
        help='Additional notes about attendance'
    )

    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='employee_id.company_id',
        store=True
    )

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('validated', 'Validated'),
    ], string='State', default='draft')

    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        """Compute worked hours"""
        for attendance in self:
            if attendance.check_in and attendance.check_out:
                delta = attendance.check_out - attendance.check_in
                attendance.worked_hours = delta.total_seconds() / 3600
            else:
                attendance.worked_hours = 0.0

    @api.depends('worked_hours', 'check_in')
    def _compute_attendance_status(self):
        """Compute attendance status based on worked hours and schedule"""
        for attendance in self:
            if not attendance.check_in:
                attendance.attendance_status = 'absent'
            elif attendance.worked_hours >= 8:
                attendance.attendance_status = 'present'
            elif attendance.worked_hours >= 4:
                attendance.attendance_status = 'half_day'
            else:
                attendance.attendance_status = 'absent'

    @api.constrains('check_in', 'check_out')
    def _check_check_in_out(self):
        """Validate check in/out times"""
        for attendance in self:
            if attendance.check_out and attendance.check_out < attendance.check_in:
                raise ValidationError(_("Check out time must be after check in time"))

    def action_check_in(self):
        """Check in employee"""
        for employee in self.env['hr.employee'].browse(self.env.context.get('active_id', [])):
            # Check if employee already checked in today
            today = datetime.now().date()
            existing_attendance = self.search([
                ('employee_id', '=', employee.id),
                ('check_in', '>=', datetime.combine(today, datetime.min.time())),
                ('check_in', '<=', datetime.combine(today, datetime.max.time())),
                ('check_out', '=', False)
            ])

            if existing_attendance:
                raise UserError(_("Employee already checked in today"))

            # Create attendance record
            self.create({
                'employee_id': employee.id,
                'check_in': datetime.now(),
                'state': 'draft'
            })

    def action_check_out(self):
        """Check out employee"""
        for employee in self.env['hr.employee'].browse(self.env.context.get('active_id', [])):
            today = datetime.now().date()
            attendance = self.search([
                ('employee_id', '=', employee.id),
                ('check_in', '>=', datetime.combine(today, datetime.min.time())),
                ('check_in', '<=', datetime.combine(today, datetime.max.time())),
                ('check_out', '=', False)
            ], limit=1)

            if not attendance:
                raise UserError(_("No check in found for today"))

            attendance.write({
                'check_out': datetime.now(),
                'state': 'confirmed'
            })

    def action_confirm_attendance(self):
        """Confirm attendance record"""
        self.write({'state': 'confirmed'})

    def action_validate_attendance(self):
        """Validate attendance record"""
        self.write({'state': 'validated'})

    @api.model
    def get_today_attendance(self, employee_id=None):
        """Get today's attendance for employee"""
        domain = [
            ('check_in', '>=', datetime.combine(datetime.now().date(), datetime.min.time())),
            ('check_in', '<=', datetime.combine(datetime.now().date(), datetime.max.time())),
        ]

        if employee_id:
            domain.append(('employee_id', '=', employee_id))

        return self.search(domain)

    @api.model
    def get_monthly_attendance(self, employee_id, year=None, month=None):
        """Get monthly attendance for employee"""
        if not year:
            year = datetime.now().year
        if not month:
            month = datetime.now().month

        start_date = datetime(year, month, 1)
        end_date = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)

        return self.search([
            ('employee_id', '=', employee_id),
            ('check_in', '>=', start_date),
            ('check_in', '<', end_date),
        ])

    def get_attendance_summary(self, employee_id, start_date, end_date):
        """Get attendance summary for date range"""
        attendances = self.search([
            ('employee_id', '=', employee_id),
            ('check_in', '>=', start_date),
            ('check_in', '<=', end_date),
            ('state', '=', 'validated')
        ])

        total_days = 0
        total_hours = 0
        present_days = 0
        absent_days = 0
        late_days = 0

        for attendance in attendances:
            total_days += 1
            total_hours += attendance.worked_hours or 0

            if attendance.attendance_status == 'present':
                present_days += 1
            elif attendance.attendance_status == 'absent':
                absent_days += 1
            elif attendance.attendance_status == 'late':
                late_days += 1

        return {
            'total_days': total_days,
            'total_hours': total_hours,
            'present_days': present_days,
            'absent_days': absent_days,
            'late_days': late_days,
            'average_hours': total_hours / total_days if total_days > 0 else 0,
        }


class HrAttendancePolicy(models.Model):
    """Attendance policy model"""

    _name = 'hr.attendance.policy'
    _description = 'Attendance Policy'

    name = fields.Char(
        string='Policy Name',
        required=True,
        help='Name of the attendance policy'
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    # Work Schedule
    working_hours = fields.Float(
        string='Working Hours per Day',
        default=8.0,
        help='Standard working hours per day'
    )

    start_time = fields.Float(
        string='Start Time',
        default=9.0,
        help='Standard start time (24-hour format)'
    )

    end_time = fields.Float(
        string='End Time',
        default=17.0,
        help='Standard end time (24-hour format)'
    )

    # Break Settings
    break_hours = fields.Float(
        string='Break Hours',
        default=1.0,
        help='Total break hours per day'
    )

    # Late Policy
    grace_period = fields.Integer(
        string='Grace Period (minutes)',
        default=15,
        help='Grace period for late arrival'
    )

    late_threshold = fields.Integer(
        string='Late Threshold (minutes)',
        default=30,
        help='Minutes after which employee is considered late'
    )

    # Overtime Policy
    max_overtime = fields.Float(
        string='Max Overtime (hours)',
        default=4.0,
        help='Maximum overtime hours allowed per day'
    )

    overtime_rate = fields.Float(
        string='Overtime Rate',
        default=1.5,
        help='Overtime pay rate multiplier'
    )

    # Weekend Policy
    weekend_work = fields.Boolean(
        string='Allow Weekend Work',
        default=False,
        help='Allow work on weekends'
    )

    weekend_rate = fields.Float(
        string='Weekend Rate',
        default=2.0,
        help='Weekend work rate multiplier'
    )

    # Holiday Policy
    holiday_work = fields.Boolean(
        string='Allow Holiday Work',
        default=False,
        help='Allow work on holidays'
    )

    holiday_rate = fields.Float(
        string='Holiday Rate',
        default=2.0,
        help='Holiday work rate multiplier'
    )

    # Description
    description = fields.Text(
        string='Description',
        help='Description of the attendance policy'
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    def get_applicable_policy(self, employee_id, date=None):
        """Get applicable attendance policy for employee"""
        if not date:
            date = datetime.now().date()

        employee = self.env['hr.employee'].browse(employee_id)

        # Check if employee has specific policy
        if hasattr(employee, 'attendance_policy_id'):
            if employee.attendance_policy_id:
                return employee.attendance_policy_id

        # Return company default policy
        return self.search([
            ('company_id', '=', employee.company_id.id),
            ('active', '=', True)
        ], limit=1)