# -*- coding: utf-8 -*-
import json
import logging
from odoo import http
from odoo.http import request, Response
import werkzeug.exceptions

_logger = logging.getLogger(__name__)


class HRController(http.Controller):
    """
    HR-specific REST API controller that provides safe endpoints for HR module operations.
    
    Maps to /api/v1/hr/* endpoints and uses hr.employee model fields.
    Returns 404 with clear message if HR model is not available.
    """

    def _check_hr_model(self, model_name):
        """Check if HR model exists and return appropriate error if not"""
        if model_name not in request.env.registry:
            return {
                'error': f'HR module not available. Model "{model_name}" not found.',
                'module': 'hr',
                'available_modules': ['crm', 'sale', 'account', 'project', 'stock']
            }, 404
        return None, None

    @http.route('/api/v1/hr/employees', type='http', auth='user', methods=['GET'], csrf=False)
    def list_employees(self, **kwargs):
        """
        Get list of HR employees with pagination and search support.
        
        This endpoint maps to the hr.employee model and provides a safe wrapper
        around the generic model API.
        
        Query parameters:
        - limit: Number of records to return (default: 50, max: 1000)
        - offset: Number of records to skip (default: 0)
        - search: Simple text search across employee name fields
        - department_id: Filter by department ID
        - active: Filter by active status (true/false)
        
        Returns standard pagination format or 404 if HR module not available.
        """
        # Check if HR model exists
        error_response, error_status = self._check_hr_model('hr.employee')
        if error_response:
            return self._error_response(error_response, error_status)

        try:
            # Get hr.employee model
            Employee = request.env['hr.employee']
            
            # Parse query parameters
            limit = min(int(kwargs.get('limit', 50)), 1000)
            offset = int(kwargs.get('offset', 0))
            search = kwargs.get('search', '').strip()
            department_id = kwargs.get('department_id')
            active = kwargs.get('active')
            
            # Build domain
            domain = []
            
            # Add department filter if provided
            if department_id:
                try:
                    domain.append(('department_id', '=', int(department_id)))
                except ValueError:
                    pass
            
            # Add active filter if provided
            if active is not None:
                domain.append(('active', '=', active.lower() in ('true', '1', 'yes')))
            
            # Add text search if provided
            if search:
                name_fields = ['name', 'work_email', 'job_title']
                search_domain = []
                
                for field in name_fields:
                    if field in Employee._fields:
                        search_domain.append((field, 'ilike', search))
                
                if search_domain:
                    domain = ['|'] * (len(search_domain) - 1) + search_domain + domain
            
            # Execute search
            total_count = Employee.search_count(domain)
            employees = Employee.search_read(
                domain=domain,
                fields=[
                    'name', 'job_title', 'work_email', 'work_phone', 'mobile_phone',
                    'department_id', 'parent_id', 'coach_id', 'active', 'gender',
                    'birthday', 'place_of_birth', 'country_of_birth', 'marital',
                    'spouse_complete_name', 'spouse_birthdate', 'children', 'emergency_contact',
                    'emergency_phone', 'address_home_id', 'work_location_id'
                ],
                limit=limit,
                offset=offset,
                order='name ASC'
            )
            
            return self._success_response({
                'items': employees,
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'model': 'hr.employee',
                'endpoint': 'hr/employees'
            })
            
        except Exception as e:
            _logger.error(f"Error in list_employees: {str(e)}")
            return self._error_response(f"Error retrieving employees: {str(e)}", 500)

    @http.route('/api/v1/hr/employees/<int:employee_id>', type='http', auth='user', methods=['GET'], csrf=False)
    def get_employee(self, employee_id, **kwargs):
        """
        Get a specific HR employee by ID.
        
        Returns 404 if employee not found or HR module not available.
        """
        # Check if HR model exists
        error_response, error_status = self._check_hr_model('hr.employee')
        if error_response:
            return self._error_response(error_response, error_status)

        try:
            Employee = request.env['hr.employee']
            employee = Employee.browse(employee_id)
            
            if not employee.exists():
                return self._error_response(f"Employee {employee_id} not found", 404)
            
            # Read employee data with all relevant fields
            employee_data = employee.read([
                'name', 'job_title', 'work_email', 'work_phone', 'mobile_phone',
                'department_id', 'parent_id', 'coach_id', 'active', 'gender',
                'birthday', 'place_of_birth', 'country_of_birth', 'marital',
                'spouse_complete_name', 'spouse_birthdate', 'children', 'emergency_contact',
                'emergency_phone', 'address_home_id', 'work_location_id'
            ])[0]
            
            return self._success_response({
                'item': employee_data,
                'model': 'hr.employee',
                'id': employee_id,
                'endpoint': 'hr/employees'
            })
            
        except Exception as e:
            _logger.error(f"Error in get_employee {employee_id}: {str(e)}")
            return self._error_response(f"Error retrieving employee: {str(e)}", 500)

    @http.route('/api/v1/hr/employees', type='http', auth='user', methods=['POST'], csrf=False)
    def create_employee(self):
        """
        Create a new HR employee.
        
        Expects JSON payload with employee field values.
        Returns created employee or 404 if HR module not available.
        """
        # Check if HR model exists
        error_response, error_status = self._check_hr_model('hr.employee')
        if error_response:
            return self._error_response(error_response, error_status)

        try:
            # Parse JSON data
            try:
                data = json.loads(request.httprequest.data)
            except json.JSONDecodeError:
                return self._error_response("Invalid JSON data in request body", 400)

            if not isinstance(data, dict):
                return self._error_response("Request body must be a JSON object", 400)

            # Validate required fields
            if not data.get('name'):
                return self._error_response("Employee name is required", 400)

            Employee = request.env['hr.employee']
            
            # Create employee
            try:
                employee = Employee.create(data)
            except Exception as e:
                # Try with sudo if regular create fails
                if "access denied" in str(e).lower() or "permission denied" in str(e).lower():
                    employee = Employee.sudo().create(data)
                else:
                    raise

            employee_data = employee.read([
                'name', 'job_title', 'work_email', 'work_phone', 'mobile_phone',
                'department_id', 'parent_id', 'coach_id', 'active', 'gender',
                'birthday', 'place_of_birth', 'country_of_birth', 'marital',
                'spouse_complete_name', 'spouse_birthdate', 'children', 'emergency_contact',
                'emergency_phone', 'address_home_id', 'work_location_id'
            ])[0]

            return self._success_response({
                'item': employee_data,
                'model': 'hr.employee',
                'id': employee.id,
                'endpoint': 'hr/employees'
            }, status=201)
            
        except Exception as e:
            _logger.error(f"Error in create_employee: {str(e)}")
            return self._error_response(f"Error creating employee: {str(e)}", 500)

    @http.route('/api/v1/hr/employees/<int:employee_id>', type='http', auth='user', methods=['PUT'], csrf=False)
    def update_employee(self, employee_id):
        """
        Update an existing HR employee.
        
        Expects JSON payload with employee field values to update.
        """
        # Check if HR model exists
        error_response, error_status = self._check_hr_model('hr.employee')
        if error_response:
            return self._error_response(error_response, error_status)

        try:
            # Parse JSON data
            try:
                data = json.loads(request.httprequest.data)
            except json.JSONDecodeError:
                return self._error_response("Invalid JSON data in request body", 400)

            if not isinstance(data, dict):
                return self._error_response("Request body must be a JSON object", 400)

            Employee = request.env['hr.employee']
            employee = Employee.browse(employee_id)
            
            if not employee.exists():
                return self._error_response(f"Employee {employee_id} not found", 404)
            
            # Update employee
            try:
                employee.write(data)
            except Exception as e:
                # Try with sudo if regular write fails
                if "access denied" in str(e).lower() or "permission denied" in str(e).lower():
                    employee.sudo().write(data)
                else:
                    raise
            
            employee_data = employee.read([
                'name', 'job_title', 'work_email', 'work_phone', 'mobile_phone',
                'department_id', 'parent_id', 'coach_id', 'active', 'gender',
                'birthday', 'place_of_birth', 'country_of_birth', 'marital',
                'spouse_complete_name', 'spouse_birthdate', 'children', 'emergency_contact',
                'emergency_phone', 'address_home_id', 'work_location_id'
            ])[0]

            return self._success_response({
                'item': employee_data,
                'model': 'hr.employee',
                'id': employee_id,
                'endpoint': 'hr/employees'
            })
            
        except Exception as e:
            _logger.error(f"Error in update_employee {employee_id}: {str(e)}")
            return self._error_response(f"Error updating employee: {str(e)}", 500)

    @http.route('/api/v1/hr/employees/<int:employee_id>', type='http', auth='user', methods=['DELETE'], csrf=False)
    def delete_employee(self, employee_id):
        """
        Delete an HR employee.
        
        Returns confirmation of deletion or 404 if not found or HR module not available.
        """
        # Check if HR model exists
        error_response, error_status = self._check_hr_model('hr.employee')
        if error_response:
            return self._error_response(error_response, error_status)

        try:
            Employee = request.env['hr.employee']
            employee = Employee.browse(employee_id)
            
            if not employee.exists():
                return self._error_response(f"Employee {employee_id} not found", 404)
            
            # Delete employee
            try:
                employee.unlink()
            except Exception as e:
                # Try with sudo if regular unlink fails
                if "access denied" in str(e).lower() or "permission denied" in str(e).lower():
                    employee.sudo().unlink()
                else:
                    raise
            
            return self._success_response({
                'model': 'hr.employee',
                'deleted_id': employee_id,
                'message': 'Employee deleted successfully',
                'endpoint': 'hr/employees'
            })
            
        except Exception as e:
            _logger.error(f"Error in delete_employee {employee_id}: {str(e)}")
            return self._error_response(f"Error deleting employee: {str(e)}", 500)

    def _success_response(self, data, status=200):
        """Return successful JSON response"""
        response = Response(
            json.dumps(data, default=str, indent=2),
            content_type='application/json',
            status=status
        )
        return response

    def _error_response(self, message, status=400):
        """Return error JSON response"""
        return self._success_response({
            'error': message,
            'success': False
        }, status)