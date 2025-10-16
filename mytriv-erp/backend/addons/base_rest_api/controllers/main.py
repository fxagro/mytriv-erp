# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request, Response
import werkzeug.exceptions


class EmployeeAPI(http.Controller):
    @http.route('/api/v1/employees', type='json', auth='user', methods=['GET'], csrf=False)
    def list_employees(self):
        """Get list of all employees"""
        try:
            employees = request.env['hr.employee'].sudo().search([])
            data = []
            for employee in employees:
                data.append({
                    "id": employee.id,
                    "name": employee.name,
                    "job_title": employee.job_title,
                    "work_email": employee.work_email,
                    "work_phone": employee.work_phone,
                    "active": employee.active
                })
            return data
        except Exception as e:
            return {"error": str(e)}

    @http.route('/api/v1/employees', type='json', auth='user', methods=['POST'], csrf=False)
    def create_employee(self, **payload):
        """Create a new employee"""
        try:
            if not payload.get('name'):
                return {"error": "Employee name is required"}

            employee = request.env['hr.employee'].sudo().create(payload)
            return {
                "id": employee.id,
                "name": employee.name,
                "message": "Employee created successfully"
            }
        except Exception as e:
            return {"error": str(e)}


class BaseRestController(http.Controller):

    @http.route('/api/models', type='http', auth='none', methods=['GET'], csrf=False)
    def get_models(self):
        """Get list of available models"""
        try:
            models = request.env['ir.model'].sudo().search_read([], ['model', 'name'])
            return self._response({'models': models})
        except Exception as e:
            return self._error_response(str(e))

    @http.route('/api/models/<string:model_name>', type='http', auth='none', methods=['GET'], csrf=False)
    def get_model_records(self, model_name, **kwargs):
        """Get records from a specific model"""
        try:
            # Check if model exists
            if model_name not in request.env:
                raise werkzeug.exceptions.NotFound(f"Model '{model_name}' not found")

            model = request.env[model_name].sudo()
            domain = kwargs.get('domain', '[]')
            fields = kwargs.get('fields', None)
            limit = int(kwargs.get('limit', 100))
            offset = int(kwargs.get('offset', 0))

            # Parse domain if provided
            if isinstance(domain, str):
                domain = json.loads(domain)

            records = model.search_read(
                domain=domain,
                fields=fields,
                limit=limit,
                offset=offset
            )

            return self._response({
                'model': model_name,
                'records': records,
                'count': len(records)
            })

        except json.JSONDecodeError:
            return self._error_response("Invalid domain format")
        except Exception as e:
            return self._error_response(str(e))

    @http.route('/api/models/<string:model_name>/<int:record_id>', type='http', auth='none', methods=['GET'], csrf=False)
    def get_model_record(self, model_name, record_id):
        """Get a specific record by ID"""
        try:
            if model_name not in request.env:
                raise werkzeug.exceptions.NotFound(f"Model '{model_name}' not found")

            model = request.env[model_name].sudo()
            record = model.browse(record_id)

            if not record.exists():
                raise werkzeug.exceptions.NotFound(f"Record {record_id} not found in model {model_name}")

            return self._response({
                'model': model_name,
                'record': record.read()[0] if record.read() else {}
            })

        except Exception as e:
            return self._error_response(str(e))

    @http.route('/api/models/<string:model_name>', type='http', auth='none', methods=['POST'], csrf=False)
    def create_model_record(self, model_name):
        """Create a new record"""
        try:
            if model_name not in request.env:
                raise werkzeug.exceptions.NotFound(f"Model '{model_name}' not found")

            data = json.loads(request.httprequest.data)
            model = request.env[model_name].sudo()
            record = model.create(data)

            return self._response({
                'model': model_name,
                'record': record.read()[0],
                'id': record.id
            }, status=201)

        except json.JSONDecodeError:
            return self._error_response("Invalid JSON data")
        except Exception as e:
            return self._error_response(str(e))

    @http.route('/api/models/<string:model_name>/<int:record_id>', type='http', auth='none', methods=['PUT'], csrf=False)
    def update_model_record(self, model_name, record_id):
        """Update a specific record"""
        try:
            if model_name not in request.env:
                raise werkzeug.exceptions.NotFound(f"Model '{model_name}' not found")

            data = json.loads(request.httprequest.data)
            model = request.env[model_name].sudo()
            record = model.browse(record_id)

            if not record.exists():
                raise werkzeug.exceptions.NotFound(f"Record {record_id} not found in model {model_name}")

            record.write(data)

            return self._response({
                'model': model_name,
                'record': record.read()[0],
                'id': record.id
            })

        except json.JSONDecodeError:
            return self._error_response("Invalid JSON data")
        except Exception as e:
            return self._error_response(str(e))

    @http.route('/api/models/<string:model_name>/<int:record_id>', type='http', auth='none', methods=['DELETE'], csrf=False)
    def delete_model_record(self, model_name, record_id):
        """Delete a specific record"""
        try:
            if model_name not in request.env:
                raise werkzeug.exceptions.NotFound(f"Model '{model_name}' not found")

            model = request.env[model_name].sudo()
            record = model.browse(record_id)

            if not record.exists():
                raise werkzeug.exceptions.NotFound(f"Record {record_id} not found in model {model_name}")

            record.unlink()

            return self._response({
                'model': model_name,
                'deleted_id': record_id,
                'message': 'Record deleted successfully'
            })

        except Exception as e:
            return self._error_response(str(e))

    def _response(self, data, status=200):
        """Return JSON response"""
        response = Response(
            json.dumps(data, default=str),
            content_type='application/json',
            status=status
        )
        return response

    def _error_response(self, message, status=400):
        """Return error response"""
        return self._response({
            'error': message
        }, status)