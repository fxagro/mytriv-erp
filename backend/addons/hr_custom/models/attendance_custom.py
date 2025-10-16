# -*- coding: utf-8 -*-
"""
Custom Attendance Model

This module extends attendance functionality with enhanced tracking
and reporting capabilities.
"""

from odoo import models, fields, api
from datetime import datetime, timedelta


class AttendanceCustom(models.Model):
    """Extended Attendance model with custom fields and functionality."""

    _name = 'hr.attendance.custom'
    _description = 'Custom Attendance Extensions'
    _inherit = ['hr.attendance']

    # Additional custom fields for enhanced attendance tracking
    attendance_type = fields.Selection([
        ('regular', 'Regular'),
        ('overtime', 'Overtime'),
        ('vacation', 'Vacation'),
        ('sick_leave', 'Sick Leave'),
        ('personal_leave', 'Personal Leave'),
        ('training', 'Training'),
        ('business_trip', 'Business Trip'),
        ('remote_work', 'Remote Work')
    ], string='Attendance Type', help='Type of attendance/work')

    location = fields.Selection([
        ('office', 'Office'),
        ('home', 'Home'),
        ('client_site', 'Client Site'),
        ('travel', 'Travel'),
        ('other', 'Other')
    ], string='Work Location', help='Location where work was performed')

    work_hours = fields.Float(
        string='Work Hours',
        compute='_compute_work_hours',
        store=True,
        help='Total hours worked in this attendance record'
    )

    break_hours = fields.Float(
        string='Break Hours',
        default=0.0,
        help='Hours taken for breaks during work'
    )

    productivity_notes = fields.Text(
        string='Productivity Notes',
        help='Notes about productivity during this attendance period'
    )

    supervisor_approved = fields.Boolean(
        string='Supervisor Approved',
        default=False,
        help='Whether attendance was approved by supervisor'
    )

    approved_by = fields.Many2one(
        'hr.employee',
        string='Approved By',
        help='Supervisor who approved this attendance'
    )

    # Overtime tracking
    overtime_hours = fields.Float(
        string='Overtime Hours',
        default=0.0,
        help='Overtime hours worked'
    )

    overtime_reason = fields.Text(
        string='Overtime Reason',
        help='Reason for working overtime'
    )

    # Remote work tracking
    remote_work_address = fields.Char(
        string='Remote Work Address',
        help='Address when working remotely'
    )

    remote_work_approved = fields.Boolean(
        string='Remote Work Approved',
        default=False,
        help='Whether remote work was pre-approved'
    )

    @api.depends('check_in', 'check_out')
    def _compute_work_hours(self):
        """Compute total work hours."""
        for attendance in self:
            if attendance.check_in and attendance.check_out:
                delta = attendance.check_out - attendance.check_in
                attendance.work_hours = delta.total_seconds() / 3600 - attendance.break_hours
            else:
                attendance.work_hours = 0.0

    def action_approve_attendance(self):
        """Approve attendance record."""
        self.write({
            'supervisor_approved': True,
            'approved_by': self.env.user.employee_id.id
        })

    def action_check_in_remote(self, address=None):
        """Check in for remote work."""
        check_in_data = {
            'employee_id': self.employee_id.id,
            'check_in': datetime.now(),
            'attendance_type': 'remote_work',
            'location': 'home'
        }

        if address:
            check_in_data['remote_work_address'] = address

        return self.create(check_in_data)

    def action_check_out_remote(self):
        """Check out from remote work."""
        self.write({
            'check_out': datetime.now(),
            'remote_work_approved': True
        })

    def get_attendance_summary(self):
        """Get comprehensive attendance summary."""
        self.ensure_one()
        return {
            'employee_name': self.employee_id.name,
            'check_in': self.check_in.isoformat() if self.check_in else None,
            'check_out': self.check_out.isoformat() if self.check_out else None,
            'work_hours': self.work_hours,
            'attendance_type': self.attendance_type,
            'location': self.location,
            'overtime_hours': self.overtime_hours,
            'supervisor_approved': self.supervisor_approved,
            'approved_by': self.approved_by.name if self.approved_by else None
        }

    @api.model
    def get_attendance_by_employee(self, employee_id, start_date=None, end_date=None):
        """Get attendance records for specific employee in date range."""
        domain = [('employee_id', '=', employee_id)]
        if start_date:
            domain.append(('check_in', '>=', start_date))
        if end_date:
            domain.append(('check_out', '<=', end_date))

        return self.search(domain)

    @api.model
    def get_attendance_by_department(self, department_id, start_date=None, end_date=None):
        """Get attendance records for specific department in date range."""
        # Get employees in department
        employees = self.env['hr.employee'].search([('department_id', '=', department_id)])
        employee_ids = employees.ids

        domain = [('employee_id', 'in', employee_ids)]
        if start_date:
            domain.append(('check_in', '>=', start_date))
        if end_date:
            domain.append(('check_out', '<=', end_date))

        return self.search(domain)

    @api.model
    def get_unapproved_attendance(self):
        """Get attendance records pending approval."""
        return self.search([('supervisor_approved', '=', False)])

    @api.model
    def get_overtime_attendance(self, start_date=None, end_date=None):
        """Get attendance records with overtime."""
        domain = [('overtime_hours', '>', 0)]
        if start_date:
            domain.append(('check_in', '>=', start_date))
        if end_date:
            domain.append(('check_out', '<=', end_date))

        return self.search(domain)

    @api.model
    def get_remote_work_attendance(self, start_date=None, end_date=None):
        """Get remote work attendance records."""
        domain = [('attendance_type', '=', 'remote_work')]
        if start_date:
            domain.append(('check_in', '>=', start_date))
        if end_date:
            domain.append(('check_out', '<=', end_date))

        return self.search(domain)

    @api.model
    def get_attendance_report(self, start_date, end_date, department_id=None):
        """Generate attendance report for date range."""
        domain = [
            ('check_in', '>=', start_date),
            ('check_out', '<=', end_date)
        ]

        if department_id:
            employees = self.env['hr.employee'].search([('department_id', '=', department_id)])
            domain.append(('employee_id', 'in', employees.ids))

        attendance_records = self.search(domain)

        # Generate report data
        report_data = {
            'total_records': len(attendance_records),
            'total_work_hours': sum(attendance_records.mapped('work_hours')),
            'total_overtime_hours': sum(attendance_records.mapped('overtime_hours')),
            'approved_records': len(attendance_records.filtered('supervisor_approved')),
            'remote_work_records': len(attendance_records.filtered(lambda r: r.attendance_type == 'remote_work')),
            'start_date': start_date,
            'end_date': end_date,
            'department_id': department_id
        }

        return report_data