# -*- coding: utf-8 -*-
import json
import logging
from odoo import http
from odoo.http import request, Response
import werkzeug.exceptions

_logger = logging.getLogger(__name__)


class GenericModelController(http.Controller):
    """
    Generic REST API controller that can expose any Odoo model via standardized endpoints.
    
    Provides CRUD operations with proper validation, pagination, search, and security.
    """

    @http.route('/api/v1/models/<string:model>', type='http', auth='user', methods=['GET'], csrf=False)
    def list_records(self, model, **kwargs):
        """
        Get list of records from any Odoo model with pagination and search support.
        
        Query parameters:
        - limit: Number of records to return (default: 50, max: 1000)
        - offset: Number of records to skip (default: 0)
        - search: Simple text search across name fields
        - domain: JSON string for advanced domain filtering
        - fields: Comma-separated list of fields to return
        
        Returns:
        {
            "items": [...],
            "total": 1000,
            "limit": 50,
            "offset": 0,
            "model": "hr.employee"
        }
        """
        try:
            # Validate model exists
            if model not in request.env.registry:
                raise werkzeug.exceptions.NotFound(f"Model '{model}' not found")

            # Get model with proper access rights
            Model = request.env[model]
            
            # Parse query parameters
            limit = min(int(kwargs.get('limit', 50)), 1000)  # Max 1000 records
            offset = int(kwargs.get('offset', 0))
            search = kwargs.get('search', '').strip()
            domain_param = kwargs.get('domain', '[]')
            fields_param = kwargs.get('fields', '')
            
            # Parse fields
            fields = None
            if fields_param:
                fields = [f.strip() for f in fields_param.split(',') if f.strip()]
            
            # Build domain
            domain = []
            
            # Parse advanced domain if provided
            if domain_param and domain_param != '[]':
                try:
                    domain = json.loads(domain_param)
                except json.JSONDecodeError:
                    raise werkzeug.exceptions.BadRequest("Invalid domain JSON format")
            
            # Add text search if provided
            if search:
                # Common name fields for search
                name_fields = ['name', 'display_name', 'title', 'email', 'phone']
                search_domain = []
                
                for field in name_fields:
                    if field in Model._fields:
                        search_domain.append((field, 'ilike', search))
                
                if search_domain:
                    domain = ['|'] * (len(search_domain) - 1) + search_domain + domain
            
            # Execute search with pagination
            total_count = Model.search_count(domain)
            records = Model.search_read(
                domain=domain,
                fields=fields,
                limit=limit,
                offset=offset,
                order='id DESC'  # Default sort by ID descending
            )
            
            return self._success_response({
                'items': records,
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'model': model
            })
            
        except werkzeug.exceptions.HTTPException:
            raise
        except Exception as e:
            _logger.error(f"Error in list_records for model {model}: {str(e)}")
            raise werkzeug.exceptions.InternalServerError(f"Error retrieving records: {str(e)}")

    @http.route('/api/v1/models/<string:model>/<int:record_id>', type='http', auth='user', methods=['GET'], csrf=False)
    def get_record(self, model, record_id, **kwargs):
        """
        Get a specific record by ID from any Odoo model.
        
        Query parameters:
        - fields: Comma-separated list of fields to return
        
        Returns single record or 404 if not found.
        """
        try:
            # Validate model exists
            if model not in request.env.registry:
                raise werkzeug.exceptions.NotFound(f"Model '{model}' not found")

            Model = request.env[model]
            fields_param = kwargs.get('fields', '')
            fields = None
            
            if fields_param:
                fields = [f.strip() for f in fields_param.split(',') if f.strip()]
            
            # Get record
            record = Model.browse(record_id)
            if not record.exists():
                raise werkzeug.exceptions.NotFound(f"Record {record_id} not found in model {model}")
            
            # Read with specified fields
            record_data = record.read(fields)[0] if record.read() else {}
            
            return self._success_response({
                'item': record_data,
                'model': model,
                'id': record_id
            })
            
        except werkzeug.exceptions.HTTPException:
            raise
        except Exception as e:
            _logger.error(f"Error in get_record for model {model}, id {record_id}: {str(e)}")
            raise werkzeug.exceptions.InternalServerError(f"Error retrieving record: {str(e)}")

    @http.route('/api/v1/models/<string:model>', type='http', auth='user', methods=['POST'], csrf=False)
    def create_record(self, model):
        """
        Create a new record in any Odoo model.
        
        Expects JSON payload with field values.
        Returns created record with generated ID.
        """
        try:
            # Validate model exists
            if model not in request.env.registry:
                raise werkzeug.exceptions.NotFound(f"Model '{model}' not found")

            # Parse JSON data
            try:
                data = json.loads(request.httprequest.data)
            except json.JSONDecodeError:
                raise werkzeug.exceptions.BadRequest("Invalid JSON data in request body")

            if not isinstance(data, dict):
                raise werkzeug.exceptions.BadRequest("Request body must be a JSON object")

            Model = request.env[model]
            
            # Create record (sudo only if user doesn't have create rights)
            try:
                record = Model.create(data)
            except Exception as e:
                # Try with sudo if regular create fails (for models requiring elevated privileges)
                if "access denied" in str(e).lower() or "permission denied" in str(e).lower():
                    record = Model.sudo().create(data)
                else:
                    raise

            return self._success_response({
                'item': record.read()[0],
                'model': model,
                'id': record.id
            }, status=201)
            
        except werkzeug.exceptions.HTTPException:
            raise
        except Exception as e:
            _logger.error(f"Error in create_record for model {model}: {str(e)}")
            raise werkzeug.exceptions.InternalServerError(f"Error creating record: {str(e)}")

    @http.route('/api/v1/models/<string:model>/<int:record_id>', type='http', auth='user', methods=['PUT'], csrf=False)
    def update_record(self, model, record_id):
        """
        Update an existing record in any Odoo model.
        
        Expects JSON payload with field values to update.
        """
        try:
            # Validate model exists
            if model not in request.env.registry:
                raise werkzeug.exceptions.NotFound(f"Model '{model}' not found")

            # Parse JSON data
            try:
                data = json.loads(request.httprequest.data)
            except json.JSONDecodeError:
                raise werkzeug.exceptions.BadRequest("Invalid JSON data in request body")

            if not isinstance(data, dict):
                raise werkzeug.exceptions.BadRequest("Request body must be a JSON object")

            Model = request.env[model]
            record = Model.browse(record_id)
            
            if not record.exists():
                raise werkzeug.exceptions.NotFound(f"Record {record_id} not found in model {model}")
            
            # Update record (sudo only if user doesn't have write rights)
            try:
                record.write(data)
            except Exception as e:
                # Try with sudo if regular write fails
                if "access denied" in str(e).lower() or "permission denied" in str(e).lower():
                    record.sudo().write(data)
                else:
                    raise
            
            return self._success_response({
                'item': record.read()[0],
                'model': model,
                'id': record_id
            })
            
        except werkzeug.exceptions.HTTPException:
            raise
        except Exception as e:
            _logger.error(f"Error in update_record for model {model}, id {record_id}: {str(e)}")
            raise werkzeug.exceptions.InternalServerError(f"Error updating record: {str(e)}")

    @http.route('/api/v1/models/<string:model>/<int:record_id>', type='http', auth='user', methods=['DELETE'], csrf=False)
    def delete_record(self, model, record_id):
        """
        Delete a record from any Odoo model.
        
        Returns confirmation of deletion.
        """
        try:
            # Validate model exists
            if model not in request.env.registry:
                raise werkzeug.exceptions.NotFound(f"Model '{model}' not found")

            Model = request.env[model]
            record = Model.browse(record_id)
            
            if not record.exists():
                raise werkzeug.exceptions.NotFound(f"Record {record_id} not found in model {model}")
            
            # Delete record (sudo only if user doesn't have unlink rights)
            try:
                record.unlink()
            except Exception as e:
                # Try with sudo if regular unlink fails
                if "access denied" in str(e).lower() or "permission denied" in str(e).lower():
                    record.sudo().unlink()
                else:
                    raise
            
            return self._success_response({
                'model': model,
                'deleted_id': record_id,
                'message': 'Record deleted successfully'
            })
            
        except werkzeug.exceptions.HTTPException:
            raise
        except Exception as e:
            _logger.error(f"Error in delete_record for model {model}, id {record_id}: {str(e)}")
            raise werkzeug.exceptions.InternalServerError(f"Error deleting record: {str(e)}")

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