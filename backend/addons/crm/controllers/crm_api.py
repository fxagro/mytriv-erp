# -*- coding: utf-8 -*-
"""
CRM API Controller for MyTriv ERP

This module provides REST API endpoints for CRM functionality.
"""

import json
import logging
from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class CrmApiController(http.Controller):
    """CRM API Controller"""

    @http.route('/api/crm/leads', type='json', auth='user', methods=['GET'])
    def get_leads(self, **kwargs):
        """Get leads list"""
        leads = request.env['crm.lead'].search_read(
            domain=[('active', '=', True)],
            fields=['id', 'name', 'lead_id', 'contact_name', 'email_from', 'stage_id', 'user_id', 'planned_revenue']
        )
        return {
            'success': True,
            'data': leads
        }

    @http.route('/api/crm/leads/<int:lead_id>', type='json', auth='user', methods=['GET'])
    def get_lead(self, lead_id, **kwargs):
        """Get specific lead"""
        lead = request.env['crm.lead'].browse(lead_id)
        if not lead.exists():
            return {
                'success': False,
                'error': 'Lead not found'
            }

        return {
            'success': True,
            'data': {
                'id': lead.id,
                'name': lead.name,
                'lead_id': lead.lead_id,
                'contact_name': lead.contact_name,
                'email_from': lead.email_from,
                'phone': lead.phone,
                'partner_name': lead.partner_name,
                'stage_id': lead.stage_id.id if lead.stage_id else None,
                'user_id': lead.user_id.id if lead.user_id else None,
                'planned_revenue': lead.planned_revenue,
                'priority': lead.priority,
                'description': lead.description,
            }
        }

    @http.route('/api/crm/leads', type='json', auth='user', methods=['POST'])
    def create_lead(self, **kwargs):
        """Create new lead"""
        try:
            lead = request.env['crm.lead'].create({
                'name': kwargs.get('name'),
                'contact_name': kwargs.get('contact_name'),
                'email_from': kwargs.get('email_from'),
                'phone': kwargs.get('phone'),
                'partner_name': kwargs.get('partner_name'),
                'planned_revenue': kwargs.get('planned_revenue'),
                'description': kwargs.get('description'),
            })

            return {
                'success': True,
                'data': {'id': lead.id}
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @http.route('/api/crm/opportunities', type='json', auth='user', methods=['GET'])
    def get_opportunities(self, **kwargs):
        """Get opportunities list"""
        opportunities = request.env['crm.opportunity'].search_read(
            domain=[('active', '=', True)],
            fields=['id', 'name', 'opportunity_id', 'partner_id', 'stage_id', 'user_id', 'planned_revenue']
        )
        return {
            'success': True,
            'data': opportunities
        }

    @http.route('/api/crm/opportunities/<int:opportunity_id>', type='json', auth='user', methods=['GET'])
    def get_opportunity(self, opportunity_id, **kwargs):
        """Get specific opportunity"""
        opportunity = request.env['crm.opportunity'].browse(opportunity_id)
        if not opportunity.exists():
            return {
                'success': False,
                'error': 'Opportunity not found'
            }

        return {
            'success': True,
            'data': {
                'id': opportunity.id,
                'name': opportunity.name,
                'opportunity_id': opportunity.opportunity_id,
                'partner_id': opportunity.partner_id.id if opportunity.partner_id else None,
                'contact_name': opportunity.contact_name,
                'email_from': opportunity.email_from,
                'phone': opportunity.phone,
                'stage_id': opportunity.stage_id.id if opportunity.stage_id else None,
                'user_id': opportunity.user_id.id if opportunity.user_id else None,
                'planned_revenue': opportunity.planned_revenue,
                'probability': opportunity.probability,
                'description': opportunity.description,
            }
        }

    @http.route('/api/crm/opportunities', type='json', auth='user', methods=['POST'])
    def create_opportunity(self, **kwargs):
        """Create new opportunity"""
        try:
            opportunity = request.env['crm.opportunity'].create({
                'name': kwargs.get('name'),
                'partner_id': kwargs.get('partner_id'),
                'contact_name': kwargs.get('contact_name'),
                'email_from': kwargs.get('email_from'),
                'phone': kwargs.get('phone'),
                'planned_revenue': kwargs.get('planned_revenue'),
                'probability': kwargs.get('probability'),
                'description': kwargs.get('description'),
            })

            return {
                'success': True,
                'data': {'id': opportunity.id}
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @http.route('/api/crm/activities', type='json', auth='user', methods=['POST'])
    def create_activity(self, **kwargs):
        """Create new activity"""
        try:
            activity = request.env['crm.activity'].create({
                'name': kwargs.get('name'),
                'activity_type': kwargs.get('activity_type'),
                'description': kwargs.get('description'),
                'lead_id': kwargs.get('lead_id'),
                'opportunity_id': kwargs.get('opportunity_id'),
                'partner_id': kwargs.get('partner_id'),
                'date_deadline': kwargs.get('date_deadline'),
                'user_id': kwargs.get('user_id'),
            })

            return {
                'success': True,
                'data': {'id': activity.id}
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @http.route('/api/crm/meetings', type='json', auth='user', methods=['POST'])
    def schedule_meeting(self, **kwargs):
        """Schedule a meeting"""
        try:
            meeting = request.env['crm.meeting'].create({
                'name': kwargs.get('name'),
                'description': kwargs.get('description'),
                'lead_id': kwargs.get('lead_id'),
                'opportunity_id': kwargs.get('opportunity_id'),
                'partner_id': kwargs.get('partner_id'),
                'start_datetime': kwargs.get('start_datetime'),
                'end_datetime': kwargs.get('end_datetime'),
                'location': kwargs.get('location'),
                'meeting_type': kwargs.get('meeting_type'),
                'user_id': kwargs.get('user_id'),
            })

            return {
                'success': True,
                'data': {'id': meeting.id}
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @http.route('/api/crm/phonecalls', type='json', auth='user', methods=['POST'])
    def log_phone_call(self, **kwargs):
        """Log a phone call"""
        try:
            phonecall = request.env['crm.phonecall'].create({
                'name': kwargs.get('name'),
                'description': kwargs.get('description'),
                'lead_id': kwargs.get('lead_id'),
                'opportunity_id': kwargs.get('opportunity_id'),
                'partner_id': kwargs.get('partner_id'),
                'call_date': kwargs.get('call_date'),
                'duration': kwargs.get('duration'),
                'call_type': kwargs.get('call_type'),
                'call_purpose': kwargs.get('call_purpose'),
                'call_result': kwargs.get('call_result'),
                'user_id': kwargs.get('user_id'),
            })

            return {
                'success': True,
                'data': {'id': phonecall.id}
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @http.route('/api/crm/dashboard', type='json', auth='user', methods=['GET'])
    def get_crm_dashboard(self, **kwargs):
        """Get CRM dashboard data"""
        try:
            # Lead statistics
            total_leads = request.env['crm.lead'].search_count([('active', '=', True)])
            new_leads = request.env['crm.lead'].search_count([
                ('active', '=', True),
                ('date_open', '>=', datetime.now().replace(day=1))
            ])

            # Opportunity statistics
            total_opportunities = request.env['crm.opportunity'].search_count([('active', '=', True)])
            won_opportunities = request.env['crm.opportunity'].search_count([
                ('active', '=', True),
                ('stage_id.is_won', '=', True)
            ])

            # Revenue statistics
            total_revenue = sum(request.env['crm.opportunity'].search([
                ('active', '=', True),
                ('stage_id.is_won', '=', True)
            ]).mapped('planned_revenue'))

            # Activity statistics
            upcoming_activities = request.env['crm.activity'].search_count([
                ('state', '=', 'planned'),
                ('date_deadline', '>=', datetime.now().date())
            ])

            overdue_activities = request.env['crm.activity'].search_count([
                ('state', '=', 'planned'),
                ('date_deadline', '<', datetime.now().date())
            ])

            return {
                'success': True,
                'data': {
                    'total_leads': total_leads,
                    'new_leads': new_leads,
                    'total_opportunities': total_opportunities,
                    'won_opportunities': won_opportunities,
                    'total_revenue': total_revenue,
                    'upcoming_activities': upcoming_activities,
                    'overdue_activities': overdue_activities,
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }