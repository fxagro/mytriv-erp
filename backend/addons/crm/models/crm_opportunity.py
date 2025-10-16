# -*- coding: utf-8 -*-
"""
Opportunity Management Model for MyTriv ERP

This module handles opportunity tracking and pipeline management.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class CrmOpportunity(models.Model):
    """Opportunity model for MyTriv ERP"""

    _name = 'crm.opportunity'
    _description = 'Opportunity'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Basic Information
    name = fields.Char(
        string='Opportunity Name',
        required=True,
        help='Name of the opportunity'
    )

    opportunity_id = fields.Char(
        string='Opportunity ID',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )

    # Customer Information
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        help='Customer for this opportunity'
    )

    contact_name = fields.Char(
        string='Contact Name',
        help='Primary contact person'
    )

    email_from = fields.Char(
        string='Email',
        help='Email address'
    )

    phone = fields.Char(
        string='Phone',
        help='Phone number'
    )

    # Opportunity Details
    description = fields.Text(
        string='Description',
        help='Description of the opportunity'
    )

    priority = fields.Selection([
        ('0', 'Very Low'),
        ('1', 'Low'),
        ('2', 'Medium'),
        ('3', 'High'),
        ('4', 'Very High'),
    ], string='Priority', default='1')

    # Sales Team
    team_id = fields.Many2one(
        'crm.team',
        string='Sales Team',
        required=True,
        default=lambda self: self._get_default_team_id()
    )

    user_id = fields.Many2one(
        'res.users',
        string='Salesperson',
        index=True,
        track_visibility='onchange',
        default=lambda self: self.env.user
    )

    # Pipeline Stage
    stage_id = fields.Many2one(
        'crm.stage',
        string='Stage',
        track_visibility='onchange',
        index=True,
        group_expand='_read_group_stage_ids',
        default=lambda self: self._get_default_stage_id()
    )

    # Financial Information
    planned_revenue = fields.Float(
        string='Expected Revenue',
        track_visibility='onchange',
        help='Expected revenue from this opportunity'
    )

    probability = fields.Float(
        string='Probability (%)',
        group_expand='_read_group_probability',
        help='Probability of winning this opportunity'
    )

    # Dates
    date_open = fields.Datetime(
        string='Created',
        readonly=True,
        default=lambda self: datetime.now()
    )

    date_closed = fields.Datetime(
        string='Closed',
        readonly=True,
        help='Date when opportunity was closed'
    )

    date_deadline = fields.Date(
        string='Deadline',
        help='Deadline for closing this opportunity'
    )

    # Activity Information
    next_activity_id = fields.Many2one(
        'crm.activity',
        string='Next Activity'
    )

    date_action = fields.Date(
        string='Next Activity Date'
    )

    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    # Status
    active = fields.Boolean(
        string='Active',
        default=True
    )

    # Lost Reason
    lost_reason = fields.Many2one(
        'crm.lost.reason',
        string='Lost Reason'
    )

    @api.model
    def create(self, vals):
        """Create opportunity with auto-generated ID"""
        if vals.get('opportunity_id', _('New')) == _('New'):
            vals['opportunity_id'] = self._generate_opportunity_id()

        return super(CrmOpportunity, self).create(vals)

    def _generate_opportunity_id(self):
        """Generate unique opportunity ID"""
        sequence = self.env['ir.sequence'].search([
            ('code', '=', 'crm.opportunity')
        ], limit=1)

        if sequence:
            return sequence.next_by_id()
        else:
            last_opportunity = self.search([], order='id desc', limit=1)
            return f'OPP{(last_opportunity.id + 1):04d}' if last_opportunity else 'OPP0001'

    @api.model
    def _get_default_stage_id(self):
        """Get default stage"""
        return self.env['crm.stage'].search([
            ('is_default', '=', True)
        ], limit=1)

    @api.model
    def _get_default_team_id(self):
        """Get default sales team"""
        return self.env['crm.team'].search([
            ('company_id', '=', self.env.company.id)
        ], limit=1)

    def action_mark_won(self):
        """Mark opportunity as won"""
        self.write({
            'stage_id': self.env['crm.stage'].search([('is_won', '=', True)], limit=1).id,
            'date_closed': datetime.now(),
            'probability': 100
        })

    def action_mark_lost(self):
        """Mark opportunity as lost"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Mark as Lost'),
            'res_model': 'crm.opportunity.lost',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_opportunity_id': self.id}
        }

    def action_schedule_meeting(self):
        """Schedule meeting for opportunity"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Schedule Meeting'),
            'res_model': 'crm.meeting',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_opportunity_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_email_from': self.email_from,
            }
        }

    @api.model
    def get_opportunities_by_stage(self):
        """Get opportunities grouped by stage"""
        opportunities = self.read_group(
            domain=[('active', '=', True)],
            fields=['stage_id'],
            groupby=['stage_id']
        )

        result = {}
        for opportunity in opportunities:
            stage_name = self.env['crm.stage'].browse(opportunity['stage_id'][0]).name
            result[stage_name] = opportunity['stage_id_count']

        return result

    @api.model
    def get_opportunity_conversion_rate(self, start_date=None, end_date=None):
        """Get opportunity conversion rate"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()

        total_opportunities = self.search_count([
            ('date_open', '>=', start_date),
            ('date_open', '<=', end_date)
        ])

        won_opportunities = self.search_count([
            ('date_open', '>=', start_date),
            ('date_open', '<=', end_date),
            ('stage_id.is_won', '=', True)
        ])

        if total_opportunities == 0:
            return 0.0

        return (won_opportunities / total_opportunities) * 100


class CrmCampaign(models.Model):
    """Marketing campaign model"""

    _name = 'crm.campaign'
    _description = 'Marketing Campaign'

    name = fields.Char(
        string='Campaign Name',
        required=True,
        translate=True
    )

    campaign_type = fields.Selection([
        ('email', 'Email'),
        ('social_media', 'Social Media'),
        ('advertising', 'Advertising'),
        ('event', 'Event'),
        ('referral', 'Referral'),
        ('other', 'Other'),
    ], string='Campaign Type', default='other')

    description = fields.Text(
        string='Description',
        help='Campaign description'
    )

    start_date = fields.Date(
        string='Start Date',
        help='Campaign start date'
    )

    end_date = fields.Date(
        string='End Date',
        help='Campaign end date'
    )

    budget = fields.Float(
        string='Budget',
        help='Campaign budget'
    )

    spent_budget = fields.Float(
        string='Spent Budget',
        compute='_compute_spent_budget'
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft')

    # Statistics
    lead_count = fields.Integer(
        string='Leads Generated',
        compute='_compute_lead_count'
    )

    opportunity_count = fields.Integer(
        string='Opportunities Created',
        compute='_compute_opportunity_count'
    )

    revenue_generated = fields.Float(
        string='Revenue Generated',
        compute='_compute_revenue_generated'
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    @api.depends('lead_ids')
    def _compute_lead_count(self):
        """Compute number of leads generated"""
        for campaign in self:
            campaign.lead_count = len(campaign.lead_ids)

    @api.depends('opportunity_ids')
    def _compute_opportunity_count(self):
        """Compute number of opportunities created"""
        for campaign in self:
            campaign.opportunity_count = len(campaign.opportunity_ids)

    @api.depends('opportunity_ids.planned_revenue')
    def _compute_revenue_generated(self):
        """Compute revenue generated from campaign"""
        for campaign in self:
            total_revenue = sum(opp.planned_revenue for opp in campaign.opportunity_ids if opp.stage_id.is_won)
            campaign.revenue_generated = total_revenue

    def action_start_campaign(self):
        """Start campaign"""
        self.write({'state': 'running'})

    def action_stop_campaign(self):
        """Stop campaign"""
        self.write({'state': 'done'})

    def action_cancel_campaign(self):
        """Cancel campaign"""
        self.write({'state': 'cancelled'})