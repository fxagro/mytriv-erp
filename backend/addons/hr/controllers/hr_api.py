# -*- coding: utf-8 -*-
"""
HR API Controller for MyTriv ERP

This module provides REST API endpoints for HR functionality.
"""

import json
import logging
from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class HrApiController(http.Controller):
    """HR API Controller"""

    @http.route('/api/hr/employees', type='json', auth='user', methods=['GET'])
    def get_employees(self, **kwargs):
        """Get employees list"""
        employees = request.env['hr.employee'].search_read(
            domain=[('active', '=', True)],
            fields=['id', 'name', 'employee_id', 'department_id', 'job_id', 'work_email']
        )
        return {
            'success': True,
            'data': employees
        }

    @http.route('/api/hr/employees/<int:employee_id>', type='json', auth='user', methods=['GET'])
    def get_employee(self, employee_id, **kwargs):
        """Get specific employee"""
        employee = request.env['hr.employee'].browse(employee_id)
        if not employee.exists():
            return {
                'success': False,
                'error': 'Employee not found'
            }

        return {
            'success': True,
            'data': {
                'id': employee.id,
                'name': employee.name,
                'employee_id': employee.employee_id,
                'department_id': employee.department_id.id if employee.department_id else None,
                'job_id': employee.job_id.id if employee.job_id else None,
                'work_email': employee.work_email,
                'work_phone': employee.work_phone,
                'joining_date': employee.joining_date.isoformat() if employee.joining_date else None,
                'employee_status': employee.employee_status,
            }
        }

    @http.route('/api/hr/employees', type='json', auth='user', methods=['POST'])
    def create_employee(self, **kwargs):
        """Create new employee"""
        try:
            employee = request.env['hr.employee'].create({
                'name': kwargs.get('name'),
                'employee_id': kwargs.get('employee_id'),
                'work_email': kwargs.get('work_email'),
                'department_id': kwargs.get('department_id'),
                'job_id': kwargs.get('job_id'),
            })

            return {
                'success': True,
                'data': {'id': employee.id}
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @http.route('/api/hr/departments', type='json', auth='user', methods=['GET'])
    def get_departments(self, **kwargs):
        """Get departments list"""
        departments = request.env['hr.department'].search_read(
            domain=[('active', '=', True)],
            fields=['id', 'name', 'complete_name', 'manager_id', 'employee_count']
        )
        return {
            'success': True,
            'data': departments
        }

    @http.route('/api/hr/attendance/checkin', type='json', auth='user', methods=['POST'])
    def check_in(self, **kwargs):
        """Employee check in"""
        try:
            employee_id = kwargs.get('employee_id')
            if not employee_id:
                return {
                    'success': False,
                    'error': 'Employee ID is required'
                }

            employee = request.env['hr.employee'].browse(employee_id)
            if not employee.exists():
                return {
                    'success': False,
                    'error': 'Employee not found'
                }

            # Create attendance record
            attendance = request.env['hr.attendance'].create({
                'employee_id': employee_id,
                'check_in': kwargs.get('timestamp') or fields.Datetime.now(),
                'check_in_location': kwargs.get('location'),
                'check_in_ip': request.httprequest.remote_addr,
            })

            return {
                'success': True,
                'data': {'attendance_id': attendance.id}
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @http.route('/api/hr/attendance/checkout', type='json', auth='user', methods=['POST'])
    def check_out(self, **kwargs):
        """Employee check out"""
        try:
            employee_id = kwargs.get('employee_id')
            if not employee_id:
                return {
                    'success': False,
                    'error': 'Employee ID is required'
                }

            # Find today's attendance record
            today = datetime.now().date()
            attendance = request.env['hr.attendance'].search([
                ('employee_id', '=', employee_id),
                ('check_in', '>=', datetime.combine(today, datetime.min.time())),
                ('check_in', '<=', datetime.combine(today, datetime.max.time())),
                ('check_out', '=', False)
            ], limit=1)

            if not attendance:
                return {
                    'success': False,
                    'error': 'No check-in found for today'
                }

            # Update attendance record
            attendance.write({
                'check_out': kwargs.get('timestamp') or fields.Datetime.now(),
                'check_out_location': kwargs.get('location'),
                'check_out_ip': request.httprequest.remote_addr,
            })

            return {
                'success': True,
                'data': {
                    'attendance_id': attendance.id,
                    'worked_hours': attendance.worked_hours
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @http.route('/api/hr/leaves', type='json', auth='user', methods=['POST'])
    def create_leave_request(self, **kwargs):
        """Create leave request"""
        try:
            leave = request.env['hr.leave'].create({
                'employee_id': kwargs.get('employee_id'),
                'leave_type_id': kwargs.get('leave_type_id'),
                'date_from': kwargs.get('date_from'),
                'date_to': kwargs.get('date_to'),
                'description': kwargs.get('description'),
            })

            return {
                'success': True,
                'data': {'leave_id': leave.id}
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @http.route('/api/hr/leaves/approve', type='json', auth='user', methods=['POST'])
    def approve_leave(self, **kwargs):
        """Approve leave request"""
        try:
            leave_id = kwargs.get('leave_id')
            leave = request.env['hr.leave'].browse(leave_id)

            if not leave.exists():
                return {
                    'success': False,
                    'error': 'Leave request not found'
                }

            leave.action_validate()

            return {
                'success': True,
                'message': 'Leave approved successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @http.route('/api/hr/dashboard', type='json', auth='user', methods=['GET'])
    def get_hr_dashboard(self, **kwargs):
        """Get HR dashboard data"""
        try:
            # Employee statistics
            total_employees = request.env['hr.employee'].search_count([('active', '=', True)])
            active_employees = request.env['hr.employee'].search_count([
                ('active', '=', True),
                ('employee_status', '=', 'active')
            ])

            # Department statistics
            departments = request.env['hr.department'].search_count([('active', '=', True)])

            # Attendance today
            today_attendance = request.env['hr.attendance'].search_count([
                ('check_in', '>=', datetime.combine(datetime.now().date(), datetime.min.time())),
                ('check_in', '<=', datetime.combine(datetime.now().date(), datetime.max.time())),
            ])

            # Pending leaves
            pending_leaves = request.env['hr.leave'].search_count([
                ('state', 'in', ['confirm', 'validate1'])
            ])

            return {
                'success': True,
                'data': {
                    'total_employees': total_employees,
                    'active_employees': active_employees,
                    'departments': departments,
                    'today_attendance': today_attendance,
                    'pending_leaves': pending_leaves,
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }