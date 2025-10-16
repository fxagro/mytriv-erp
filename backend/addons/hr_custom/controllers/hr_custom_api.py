# -*- coding: utf-8 -*-
"""
HR Custom API Controller

This module provides REST API endpoints for HR custom functionality,
extending the base REST API with HR-specific operations.
"""

import json
from odoo import http
from odoo.http import request
from datetime import datetime


class HrCustomAPI(http.Controller):
    """REST API controller for HR custom operations."""

    @http.route('/api/v1/hr/employees', type='json', auth='user', methods=['GET'], csrf=False)
    def get_employees(self, **kwargs):
        """Get employees with optional filtering."""
        try:
            # Get query parameters
            department_id = kwargs.get('department_id')
            grade = kwargs.get('grade')
            employment_type = kwargs.get('employment_type')
            active = kwargs.get('active', 'true').lower() == 'true'
            limit = int(kwargs.get('limit', 100))
            offset = int(kwargs.get('offset', 0))

            # Build domain for filtering
            domain = [('active', '=', active)]
            if department_id:
                domain.append(('department_id', '=', int(department_id)))
            if grade:
                domain.append(('employee_grade', '=', grade))
            if employment_type:
                domain.append(('employment_type', '=', employment_type))

            # Search employees
            employees = request.env['hr.employee'].sudo().search(
                domain,
                limit=limit,
                offset=offset
            )

            # Format response data
            data = []
            for employee in employees:
                employee_data = {
                    'id': employee.id,
                    'name': employee.name,
                    'employee_code': employee.employee_code,
                    'job_title': employee.job_title,
                    'work_email': employee.work_email,
                    'work_phone': employee.work_phone,
                    'department': employee.department_id.name if employee.department_id else None,
                    'employee_grade': employee.employee_grade,
                    'employment_type': employee.employment_type,
                    'work_schedule': employee.work_schedule,
                    'hourly_rate': employee.hourly_rate,
                    'monthly_salary': employee.monthly_salary,
                    'performance_rating': employee.performance_rating,
                    'active': employee.active
                }
                data.append(employee_data)

            return {
                'employees': data,
                'count': len(data),
                'total': len(request.env['hr.employee'].sudo().search(domain))
            }

        except Exception as e:
            return {'error': str(e)}

    @http.route('/api/v1/hr/departments', type='json', auth='user', methods=['GET'], csrf=False)
    def get_departments(self, **kwargs):
        """Get departments with optional filtering."""
        try:
            # Get query parameters
            department_type = kwargs.get('department_type')
            manager_id = kwargs.get('manager_id')
            limit = int(kwargs.get('limit', 100))
            offset = int(kwargs.get('offset', 0))

            # Build domain for filtering
            domain = []
            if department_type:
                domain.append(('department_type', '=', department_type))
            if manager_id:
                domain.append(('manager_id', '=', int(manager_id)))

            # Search departments
            departments = request.env['hr.department'].sudo().search(
                domain,
                limit=limit,
                offset=offset
            )

            # Format response data
            data = []
            for department in departments:
                department_data = {
                    'id': department.id,
                    'name': department.name,
                    'department_code': department.department_code,
                    'department_type': department.department_type,
                    'manager': department.manager_id.name if department.manager_id else None,
                    'parent_department': department.parent_department_id.name if department.parent_department_id else None,
                    'location': department.location,
                    'total_employees': department.total_employees,
                    'active_employees': department.active_employees,
                    'budget_allocated': department.budget_allocated,
                    'budget_remaining': department.budget_remaining
                }
                data.append(department_data)

            return {
                'departments': data,
                'count': len(data),
                'total': len(request.env['hr.department'].sudo().search(domain))
            }

        except Exception as e:
            return {'error': str(e)}

    @http.route('/api/v1/hr/attendance', type='json', auth='user', methods=['GET'], csrf=False)
    def get_attendance(self, **kwargs):
        """Get attendance records with optional filtering."""
        try:
            # Get query parameters
            employee_id = kwargs.get('employee_id')
            department_id = kwargs.get('department_id')
            attendance_type = kwargs.get('attendance_type')
            date_from = kwargs.get('date_from')
            date_to = kwargs.get('date_to')
            limit = int(kwargs.get('limit', 100))
            offset = int(kwargs.get('offset', 0))

            # Build domain for filtering
            domain = []
            if employee_id:
                domain.append(('employee_id', '=', int(employee_id)))
            if attendance_type:
                domain.append(('attendance_type', '=', attendance_type))
            if date_from:
                domain.append(('check_in', '>=', date_from))
            if date_to:
                domain.append(('check_out', '<=', date_to))

            # If department specified, get employees in that department
            if department_id:
                employees = request.env['hr.employee'].sudo().search([('department_id', '=', int(department_id))])
                domain.append(('employee_id', 'in', employees.ids))

            # Search attendance records
            attendance_records = request.env['hr.attendance'].sudo().search(
                domain,
                limit=limit,
                offset=offset
            )

            # Format response data
            data = []
            for record in attendance_records:
                record_data = {
                    'id': record.id,
                    'employee_name': record.employee_id.name,
                    'check_in': record.check_in.isoformat() if record.check_in else None,
                    'check_out': record.check_out.isoformat() if record.check_out else None,
                    'work_hours': record.work_hours,
                    'attendance_type': record.attendance_type,
                    'location': record.location,
                    'overtime_hours': record.overtime_hours,
                    'supervisor_approved': record.supervisor_approved
                }
                data.append(record_data)

            return {
                'attendance': data,
                'count': len(data),
                'total': len(request.env['hr.attendance'].sudo().search(domain))
            }

        except Exception as e:
            return {'error': str(e)}

    @http.route('/api/v1/hr/dashboard', type='json', auth='user', methods=['GET'], csrf=False)
    def get_hr_dashboard(self):
        """Get HR dashboard data."""
        try:
            # Get employees due for appraisal
            appraisal_due = request.env['hr.employee'].sudo().get_employees_due_appraisal()

            # Get high performers
            high_performers = request.env['hr.employee'].sudo().get_high_performers()

            # Get unapproved attendance
            unapproved_attendance = request.env['hr.attendance'].sudo().get_unapproved_attendance()

            # Get overtime attendance
            overtime_attendance = request.env['hr.attendance'].sudo().get_overtime_attendance()

            # Get department hierarchy
            department_hierarchy = request.env['hr.department'].sudo().get_department_hierarchy()

            dashboard_data = {
                'appraisal_due_count': len(appraisal_due),
                'high_performers_count': len(high_performers),
                'unapproved_attendance_count': len(unapproved_attendance),
                'overtime_attendance_count': len(overtime_attendance),
                'total_departments': len(request.env['hr.department'].sudo().search([])),
                'total_employees': len(request.env['hr.employee'].sudo().search([('active', '=', True)])),
                'department_hierarchy': department_hierarchy,
                'generated_at': datetime.now().isoformat()
            }

            return {'dashboard': dashboard_data}

        except Exception as e:
            return {'error': str(e)}