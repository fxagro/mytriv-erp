# -*- coding: utf-8 -*-
"""
CRM Custom API Controller

This module provides REST API endpoints for CRM custom functionality,
extending the base REST API with CRM-specific operations.
"""

import json
from odoo import http
from odoo.http import request
from datetime import datetime, timedelta


class CrmCustomAPI(http.Controller):
    """REST API controller for CRM custom operations."""

    @http.route('/api/v1/crm/leads', type='json', auth='user', methods=['GET'], csrf=False)
    def get_crm_leads(self, **kwargs):
        """Get CRM leads with optional filtering."""
        try:
            # Get query parameters
            priority = kwargs.get('priority')
            stage_id = kwargs.get('stage_id')
            qualification_status = kwargs.get('qualification_status')
            limit = int(kwargs.get('limit', 100))
            offset = int(kwargs.get('offset', 0))

            # Build domain for filtering
            domain = []
            if priority:
                domain.append(('lead_priority', '=', priority))
            if stage_id:
                domain.append(('stage_id', '=', int(stage_id)))
            if qualification_status:
                domain.append(('lead_qualification_status', '=', qualification_status))

            # Search leads
            leads = request.env['crm.lead'].sudo().search(
                domain,
                limit=limit,
                offset=offset
            )

            # Format response data
            data = []
            for lead in leads:
                lead_data = {
                    'id': lead.id,
                    'name': lead.name,
                    'partner_name': lead.partner_name,
                    'email_from': lead.email_from,
                    'phone': lead.phone,
                    'stage_id': lead.stage_id.id if lead.stage_id else None,
                    'stage_name': lead.stage_id.name if lead.stage_id else None,
                    'user_id': lead.user_id.id if lead.user_id else None,
                    'user_name': lead.user_id.name if lead.user_id else None,
                    'priority': lead.priority,
                    'lead_priority': lead.lead_priority,
                    'expected_revenue': lead.expected_revenue,
                    'conversion_probability': lead.conversion_probability,
                    'lead_qualification_status': lead.lead_qualification_status,
                    'create_date': lead.create_date.isoformat() if lead.create_date else None,
                    'date_deadline': lead.date_deadline.isoformat() if lead.date_deadline else None,
                    'is_overdue': lead.is_overdue,
                    'days_since_creation': lead.days_since_creation
                }
                data.append(lead_data)

            return {
                'leads': data,
                'count': len(data),
                'total': len(request.env['crm.lead'].sudo().search(domain))
            }

        except Exception as e:
            return {'error': str(e)}

    @http.route('/api/v1/crm/leads/<int:lead_id>', type='json', auth='user', methods=['GET'], csrf=False)
    def get_crm_lead(self, lead_id):
        """Get a specific CRM lead by ID."""
        try:
            lead = request.env['crm.lead'].sudo().browse(lead_id)

            if not lead.exists():
                return {'error': 'Lead not found'}

            lead_data = {
                'id': lead.id,
                'name': lead.name,
                'partner_name': lead.partner_name,
                'email_from': lead.email_from,
                'phone': lead.phone,
                'stage_id': lead.stage_id.id if lead.stage_id else None,
                'stage_name': lead.stage_id.name if lead.stage_id else None,
                'user_id': lead.user_id.id if lead.user_id else None,
                'user_name': lead.user_id.name if lead.user_id else None,
                'priority': lead.priority,
                'lead_priority': lead.lead_priority,
                'expected_revenue': lead.expected_revenue,
                'conversion_probability': lead.conversion_probability,
                'lead_qualification_status': lead.lead_qualification_status,
                'lead_source_detail': lead.lead_source_detail,
                'last_contact_date': lead.last_contact_date.isoformat() if lead.last_contact_date else None,
                'next_follow_up_date': lead.next_follow_up_date.isoformat() if lead.next_follow_up_date else None,
                'create_date': lead.create_date.isoformat() if lead.create_date else None,
                'date_deadline': lead.date_deadline.isoformat() if lead.date_deadline else None,
                'is_overdue': lead.is_overdue,
                'days_since_creation': lead.days_since_creation
            }

            return {'lead': lead_data}

        except Exception as e:
            return {'error': str(e)}

    @http.route('/api/v1/crm/leads', type='json', auth='user', methods=['POST'], csrf=False)
    def create_crm_lead(self, **kwargs):
        """Create a new CRM lead."""
        try:
            # Extract lead data from request
            lead_data = {}
            for key, value in kwargs.items():
                if hasattr(request.env['crm.lead']._fields, key):
                    lead_data[key] = value

            # Create the lead
            lead = request.env['crm.lead'].sudo().create(lead_data)

            return {
                'id': lead.id,
                'name': lead.name,
                'message': 'Lead created successfully'
            }

        except Exception as e:
            return {'error': str(e)}

    @http.route('/api/v1/crm/leads/<int:lead_id>/qualify', type='json', auth='user', methods=['POST'], csrf=False)
    def qualify_lead(self, lead_id):
        """Mark a lead as qualified."""
        try:
            lead = request.env['crm.lead'].sudo().browse(lead_id)

            if not lead.exists():
                return {'error': 'Lead not found'}

            lead.action_set_qualified()

            return {
                'id': lead.id,
                'message': 'Lead marked as qualified',
                'qualification_status': lead.lead_qualification_status
            }

        except Exception as e:
            return {'error': str(e)}

    @http.route('/api/v1/crm/leads/<int:lead_id>/unqualify', type='json', auth='user', methods=['POST'], csrf=False)
    def unqualify_lead(self, lead_id):
        """Mark a lead as unqualified."""
        try:
            lead = request.env['crm.lead'].sudo().browse(lead_id)

            if not lead.exists():
                return {'error': 'Lead not found'}

            lead.action_set_unqualified()

            return {
                'id': lead.id,
                'message': 'Lead marked as unqualified',
                'qualification_status': lead.lead_qualification_status
            }

        except Exception as e:
            return {'error': str(e)}

    @http.route('/api/v1/crm/leads/<int:lead_id>/follow-up', type='json', auth='user', methods=['POST'], csrf=False)
    def schedule_follow_up(self, lead_id, **kwargs):
        """Schedule a follow-up for a lead."""
        try:
            lead = request.env['crm.lead'].sudo().browse(lead_id)

            if not lead.exists():
                return {'error': 'Lead not found'}

            days = int(kwargs.get('days', 7))
            lead.action_schedule_follow_up(days)

            return {
                'id': lead.id,
                'message': f'Follow-up scheduled in {days} days',
                'next_follow_up_date': lead.next_follow_up_date.isoformat() if lead.next_follow_up_date else None
            }

        except Exception as e:
            return {'error': str(e)}

    @http.route('/api/v1/crm/funnel-analytics', type='json', auth='user', methods=['GET'], csrf=False)
    def get_funnel_analytics(self, **kwargs):
        """Get CRM funnel analytics."""
        try:
            days = int(kwargs.get('days', 30))

            # Get funnel overview
            overview = request.env['crm.funnel.analytics'].sudo().get_funnel_overview(days)

            return {'analytics': overview}

        except Exception as e:
            return {'error': str(e)}

    @http.route('/api/v1/crm/stages', type='json', auth='user', methods=['GET'], csrf=False)
    def get_crm_stages(self):
        """Get all CRM stages with statistics."""
        try:
            stages = request.env['crm.stage'].sudo().search([])

            data = []
            for stage in stages:
                stage_data = {
                    'id': stage.id,
                    'name': stage.name,
                    'sequence': stage.sequence,
                    'is_won': stage.is_won,
                    'requirements': stage.requirements,
                    'lead_count': stage.lead_count,
                    'average_conversion_time': stage.average_conversion_time,
                    'success_rate': stage.success_rate
                }
                data.append(stage_data)

            return {
                'stages': data,
                'count': len(data)
            }

        except Exception as e:
            return {'error': str(e)}

    @http.route('/api/v1/crm/dashboard', type='json', auth='user', methods=['GET'], csrf=False)
    def get_crm_dashboard(self):
        """Get CRM dashboard data."""
        try:
            # Get overdue leads
            overdue_leads = request.env['crm.lead'].sudo().get_overdue_leads()

            # Get leads needing follow-up
            follow_up_leads = request.env['crm.lead'].sudo().get_leads_needing_follow_up()

            # Get funnel overview
            funnel_overview = request.env['crm.funnel.analytics'].sudo().get_funnel_overview()

            # Get pipeline overview
            pipeline_overview = request.env['crm.stage'].sudo().get_pipeline_overview()

            dashboard_data = {
                'overdue_leads_count': len(overdue_leads),
                'follow_up_leads_count': len(follow_up_leads),
                'funnel_overview': funnel_overview,
                'pipeline_overview': pipeline_overview,
                'generated_at': datetime.now().isoformat()
            }

            return {'dashboard': dashboard_data}

        except Exception as e:
            return {'error': str(e)}