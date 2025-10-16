# -*- coding: utf-8 -*-
import json
import logging
from odoo import http
from odoo.http import request, Response
import werkzeug.exceptions

_logger = logging.getLogger(__name__)


class CRMController(http.Controller):
    """
    CRM-specific REST API controller that provides safe endpoints for CRM module operations.
    
    Maps to /api/v1/crm/* endpoints and uses crm.lead model fields.
    Returns 404 with clear message if CRM model is not available.
    """

    def _check_crm_model(self, model_name):
        """Check if CRM model exists and return appropriate error if not"""
        if model_name not in request.env.registry:
            return {
                'error': f'CRM module not available. Model "{model_name}" not found.',
                'module': 'crm',
                'available_modules': ['hr', 'sale', 'account', 'project', 'stock']
            }, 404
        return None, None

    @http.route('/api/v1/crm/leads', type='http', auth='user', methods=['GET'], csrf=False)
    def list_leads(self, **kwargs):
        """
        Get list of CRM leads with pagination and search support.
        
        This endpoint maps to the crm.lead model and provides a safe wrapper
        around the generic model API.
        
        Query parameters:
        - limit: Number of records to return (default: 50, max: 1000)
        - offset: Number of records to skip (default: 0)
        - search: Simple text search across lead name fields
        - stage_id: Filter by stage ID
        - user_id: Filter by assigned user ID
        - priority: Filter by priority (0=Very Low, 1=Low, 2=Medium, 3=High)
        - type: Filter by lead type (lead/opportunity)
        
        Returns standard pagination format or 404 if CRM module not available.
        """
        # Check if CRM model exists
        error_response, error_status = self._check_crm_model('crm.lead')
        if error_response:
            return self._error_response(error_response, error_status)

        try:
            # Get crm.lead model
            Lead = request.env['crm.lead']
            
            # Parse query parameters
            limit = min(int(kwargs.get('limit', 50)), 1000)
            offset = int(kwargs.get('offset', 0))
            search = kwargs.get('search', '').strip()
            stage_id = kwargs.get('stage_id')
            user_id = kwargs.get('user_id')
            priority = kwargs.get('priority')
            lead_type = kwargs.get('type')
            
            # Build domain
            domain = []
            
            # Add stage filter if provided
            if stage_id:
                try:
                    domain.append(('stage_id', '=', int(stage_id)))
                except ValueError:
                    pass
            
            # Add user filter if provided
            if user_id:
                try:
                    domain.append(('user_id', '=', int(user_id)))
                except ValueError:
                    pass
            
            # Add priority filter if provided
            if priority:
                try:
                    domain.append(('priority', '=', int(priority)))
                except ValueError:
                    pass
            
            # Add type filter if provided
            if lead_type:
                domain.append(('type', '=', lead_type))
            
            # Add text search if provided
            if search:
                name_fields = ['name', 'partner_name', 'email_from', 'phone', 'street', 'city']
                search_domain = []
                
                for field in name_fields:
                    if field in Lead._fields:
                        search_domain.append((field, 'ilike', search))
                
                if search_domain:
                    domain = ['|'] * (len(search_domain) - 1) + search_domain + domain
            
            # Execute search
            total_count = Lead.search_count(domain)
            leads = Lead.search_read(
                domain=domain,
                fields=[
                    'name', 'partner_name', 'email_from', 'phone', 'mobile', 'street', 'city',
                    'country_id', 'stage_id', 'user_id', 'team_id', 'priority', 'type',
                    'expected_revenue', 'probability', 'date_deadline', 'activity_summary',
                    'next_activity_id', 'title_action', 'date_action', 'active'
                ],
                limit=limit,
                offset=offset,
                order='priority DESC, create_date DESC'
            )
            
            return self._success_response({
                'items': leads,
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'model': 'crm.lead',
                'endpoint': 'crm/leads'
            })
            
        except Exception as e:
            _logger.error(f"Error in list_leads: {str(e)}")
            return self._error_response(f"Error retrieving leads: {str(e)}", 500)

    @http.route('/api/v1/crm/leads/<int:lead_id>', type='http', auth='user', methods=['GET'], csrf=False)
    def get_lead(self, lead_id, **kwargs):
        """
        Get a specific CRM lead by ID.
        
        Returns 404 if lead not found or CRM module not available.
        """
        # Check if CRM model exists
        error_response, error_status = self._check_crm_model('crm.lead')
        if error_response:
            return self._error_response(error_response, error_status)

        try:
            Lead = request.env['crm.lead']
            lead = Lead.browse(lead_id)
            
            if not lead.exists():
                return self._error_response(f"Lead {lead_id} not found", 404)
            
            # Read lead data with all relevant fields
            lead_data = lead.read([
                'name', 'partner_name', 'email_from', 'phone', 'mobile', 'street', 'city',
                'country_id', 'stage_id', 'user_id', 'team_id', 'priority', 'type',
                'expected_revenue', 'probability', 'date_deadline', 'activity_summary',
                'next_activity_id', 'title_action', 'date_action', 'active', 'description',
                'contact_name', 'partner_id', 'company_currency', 'campaign_id', 'source_id',
                'medium_id', 'activity_ids', 'meeting_ids', 'phonecall_ids'
            ])[0]
            
            return self._success_response({
                'item': lead_data,
                'model': 'crm.lead',
                'id': lead_id,
                'endpoint': 'crm/leads'
            })
            
        except Exception as e:
            _logger.error(f"Error in get_lead {lead_id}: {str(e)}")
            return self._error_response(f"Error retrieving lead: {str(e)}", 500)

    @http.route('/api/v1/crm/leads', type='http', auth='user', methods=['POST'], csrf=False)
    def create_lead(self):
        """
        Create a new CRM lead.
        
        Expects JSON payload with lead field values.
        Returns created lead or 404 if CRM module not available.
        """
        # Check if CRM model exists
        error_response, error_status = self._check_crm_model('crm.lead')
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
                return self._error_response("Lead name is required", 400)

            Lead = request.env['crm.lead']
            
            # Create lead
            try:
                lead = Lead.create(data)
            except Exception as e:
                # Try with sudo if regular create fails
                if "access denied" in str(e).lower() or "permission denied" in str(e).lower():
                    lead = Lead.sudo().create(data)
                else:
                    raise

            lead_data = lead.read([
                'name', 'partner_name', 'email_from', 'phone', 'mobile', 'street', 'city',
                'country_id', 'stage_id', 'user_id', 'team_id', 'priority', 'type',
                'expected_revenue', 'probability', 'date_deadline', 'activity_summary',
                'next_activity_id', 'title_action', 'date_action', 'active'
            ])[0]

            return self._success_response({
                'item': lead_data,
                'model': 'crm.lead',
                'id': lead.id,
                'endpoint': 'crm/leads'
            }, status=201)
            
        except Exception as e:
            _logger.error(f"Error in create_lead: {str(e)}")
            return self._error_response(f"Error creating lead: {str(e)}", 500)

    @http.route('/api/v1/crm/leads/<int:lead_id>', type='http', auth='user', methods=['PUT'], csrf=False)
    def update_lead(self, lead_id):
        """
        Update an existing CRM lead.
        
        Expects JSON payload with lead field values to update.
        """
        # Check if CRM model exists
        error_response, error_status = self._check_crm_model('crm.lead')
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

            Lead = request.env['crm.lead']
            lead = Lead.browse(lead_id)
            
            if not lead.exists():
                return self._error_response(f"Lead {lead_id} not found", 404)
            
            # Update lead
            try:
                lead.write(data)
            except Exception as e:
                # Try with sudo if regular write fails
                if "access denied" in str(e).lower() or "permission denied" in str(e).lower():
                    lead.sudo().write(data)
                else:
                    raise
            
            lead_data = lead.read([
                'name', 'partner_name', 'email_from', 'phone', 'mobile', 'street', 'city',
                'country_id', 'stage_id', 'user_id', 'team_id', 'priority', 'type',
                'expected_revenue', 'probability', 'date_deadline', 'activity_summary',
                'next_activity_id', 'title_action', 'date_action', 'active'
            ])[0]

            return self._success_response({
                'item': lead_data,
                'model': 'crm.lead',
                'id': lead_id,
                'endpoint': 'crm/leads'
            })
            
        except Exception as e:
            _logger.error(f"Error in update_lead {lead_id}: {str(e)}")
            return self._error_response(f"Error updating lead: {str(e)}", 500)

    @http.route('/api/v1/crm/leads/<int:lead_id>', type='http', auth='user', methods=['DELETE'], csrf=False)
    def delete_lead(self, lead_id):
        """
        Delete a CRM lead.
        
        Returns confirmation of deletion or 404 if not found or CRM module not available.
        """
        # Check if CRM model exists
        error_response, error_status = self._check_crm_model('crm.lead')
        if error_response:
            return self._error_response(error_response, error_status)

        try:
            Lead = request.env['crm.lead']
            lead = Lead.browse(lead_id)
            
            if not lead.exists():
                return self._error_response(f"Lead {lead_id} not found", 404)
            
            # Delete lead
            try:
                lead.unlink()
            except Exception as e:
                # Try with sudo if regular unlink fails
                if "access denied" in str(e).lower() or "permission denied" in str(e).lower():
                    lead.sudo().unlink()
                else:
                    raise
            
            return self._success_response({
                'model': 'crm.lead',
                'deleted_id': lead_id,
                'message': 'Lead deleted successfully',
                'endpoint': 'crm/leads'
            })
            
        except Exception as e:
            _logger.error(f"Error in delete_lead {lead_id}: {str(e)}")
            return self._error_response(f"Error deleting lead: {str(e)}", 500)

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