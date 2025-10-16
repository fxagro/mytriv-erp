# -*- coding: utf-8 -*-
"""
Project Custom API Controller

This module provides REST API endpoints for project custom functionality,
extending the base REST API with project management operations.
"""

import json
from odoo import http
from odoo.http import request
from datetime import datetime


class ProjectCustomAPI(http.Controller):
    """REST API controller for project custom operations."""

    @http.route('/api/v1/project/projects', type='json', auth='user', methods=['GET'], csrf=False)
    def get_projects(self, **kwargs):
        """Get projects with optional filtering."""
        try:
            # Get query parameters
            project_type = kwargs.get('project_type')
            priority = kwargs.get('priority')
            health_status = kwargs.get('health_status')
            manager_id = kwargs.get('manager_id')
            limit = int(kwargs.get('limit', 100))
            offset = int(kwargs.get('offset', 0))

            # Build domain for filtering
            domain = []
            if project_type:
                domain.append(('project_type', '=', project_type))
            if priority:
                domain.append(('project_priority', '=', priority))
            if health_status:
                domain.append(('project_health', '=', health_status))
            if manager_id:
                domain.append(('project_manager_id', '=', int(manager_id)))

            # Search projects
            projects = request.env['project.project'].sudo().search(
                domain,
                limit=limit,
                offset=offset
            )

            # Format response data
            data = []
            for project in projects:
                project_data = {
                    'id': project.id,
                    'name': project.name,
                    'project_type': project.project_type,
                    'project_priority': project.project_priority,
                    'project_health': project.project_health,
                    'completion_percentage': project.completion_percentage,
                    'total_tasks': project.total_tasks,
                    'completed_tasks': project.completed_tasks,
                    'overdue_tasks': project.overdue_tasks,
                    'budget_allocated': project.budget_allocated,
                    'budget_used': project.budget_used,
                    'budget_remaining': project.budget_remaining,
                    'total_timesheet_hours': project.total_timesheet_hours,
                    'project_manager': project.project_manager_id.name if project.project_manager_id else None,
                    'client_name': project.client_id.name if project.client_id else None,
                    'department_name': project.department_id.name if project.department_id else None,
                    'team_members_count': len(project.team_members)
                }
                data.append(project_data)

            return {
                'projects': data,
                'count': len(data),
                'total': len(request.env['project.project'].sudo().search(domain))
            }

        except Exception as e:
            return {'error': str(e)}

    @http.route('/api/v1/project/tasks', type='json', auth='user', methods=['GET'], csrf=False)
    def get_tasks(self, **kwargs):
        """Get tasks with optional filtering."""
        try:
            # Get query parameters
            project_id = kwargs.get('project_id')
            priority = kwargs.get('priority')
            complexity = kwargs.get('complexity')
            category = kwargs.get('category')
            limit = int(kwargs.get('limit', 100))
            offset = int(kwargs.get('offset', 0))

            # Build domain for filtering
            domain = []
            if project_id:
                domain.append(('project_id', '=', int(project_id)))
            if priority:
                domain.append(('task_priority', '=', priority))
            if complexity:
                domain.append(('task_complexity', '=', complexity))
            if category:
                domain.append(('task_category', '=', category))

            # Search tasks
            tasks = request.env['project.task'].sudo().search(
                domain,
                limit=limit,
                offset=offset
            )

            # Format response data
            data = []
            for task in tasks:
                task_data = {
                    'id': task.id,
                    'name': task.name,
                    'project_id': task.project_id.id if task.project_id else None,
                    'project_name': task.project_id.name if task.project_id else None,
                    'task_priority': task.task_priority,
                    'task_complexity': task.task_complexity,
                    'estimated_hours': task.estimated_hours,
                    'actual_hours': task.actual_hours,
                    'remaining_hours': task.remaining_hours,
                    'progress_percentage': task.progress_percentage,
                    'task_category': task.task_category,
                    'assigned_department': task.assigned_department.name if task.assigned_department else None,
                    'user_id': task.user_id.id if task.user_id else None,
                    'stage_name': task.stage_id.name if task.stage_id else None
                }
                data.append(task_data)

            return {
                'tasks': data,
                'count': len(data),
                'total': len(request.env['project.task'].sudo().search(domain))
            }

        except Exception as e:
            return {'error': str(e)}

    @http.route('/api/v1/project/timesheets', type='json', auth='user', methods=['GET'], csrf=False)
    def get_timesheets(self, **kwargs):
        """Get timesheets with optional filtering."""
        try:
            # Get query parameters
            employee_id = kwargs.get('employee_id')
            project_id = kwargs.get('project_id')
            work_type = kwargs.get('work_type')
            date_from = kwargs.get('date_from')
            date_to = kwargs.get('date_to')
            limit = int(kwargs.get('limit', 100))
            offset = int(kwargs.get('offset', 0))

            # Build domain for filtering
            domain = []
            if employee_id:
                domain.append(('employee_id', '=', int(employee_id)))
            if project_id:
                domain.append(('project_id', '=', int(project_id)))
            if work_type:
                domain.append(('work_type', '=', work_type))
            if date_from:
                domain.append(('date', '>=', date_from))
            if date_to:
                domain.append(('date', '<=', date_to))

            # Search timesheets
            timesheets = request.env['account.analytic.line'].sudo().search(
                domain,
                limit=limit,
                offset=offset
            )

            # Format response data
            data = []
            for timesheet in timesheets:
                timesheet_data = {
                    'id': timesheet.id,
                    'employee_name': timesheet.employee_id.name if timesheet.employee_id else None,
                    'project_name': timesheet.project_id.name if timesheet.project_id else None,
                    'task_name': timesheet.task_id.name if timesheet.task_id else None,
                    'date': timesheet.date.isoformat() if timesheet.date else None,
                    'unit_amount': timesheet.unit_amount,
                    'work_type': timesheet.work_type,
                    'location': timesheet.location,
                    'productivity_rating': timesheet.productivity_rating,
                    'hourly_cost': timesheet.hourly_cost,
                    'total_cost': timesheet.total_cost,
                    'is_approved': timesheet.is_approved
                }
                data.append(timesheet_data)

            return {
                'timesheets': data,
                'count': len(data),
                'total': len(request.env['account.analytic.line'].sudo().search(domain))
            }

        except Exception as e:
            return {'error': str(e)}

    @http.route('/api/v1/project/dashboard', type='json', auth='user', methods=['GET'], csrf=False)
    def get_project_dashboard(self):
        """Get project management dashboard data."""
        try:
            # Get overdue projects
            overdue_projects = request.env['project.project'].sudo().get_overdue_projects()

            # Get overdue tasks
            overdue_tasks = request.env['project.task'].sudo().get_overdue_tasks()

            # Get unapproved timesheets
            unapproved_timesheets = request.env['account.analytic.line'].sudo().get_unapproved_timesheets()

            # Get projects by health status
            green_projects = request.env['project.project'].sudo().get_projects_by_health('green')
            yellow_projects = request.env['project.project'].sudo().get_projects_by_health('yellow')
            red_projects = request.env['project.project'].sudo().get_projects_by_health('red')

            dashboard_data = {
                'overdue_projects_count': len(overdue_projects),
                'overdue_tasks_count': len(overdue_tasks),
                'unapproved_timesheets_count': len(unapproved_timesheets),
                'green_projects_count': len(green_projects),
                'yellow_projects_count': len(yellow_projects),
                'red_projects_count': len(red_projects),
                'generated_at': datetime.now().isoformat()
            }

            return {'dashboard': dashboard_data}

        except Exception as e:
            return {'error': str(e)}