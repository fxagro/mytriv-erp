# -*- coding: utf-8 -*-
"""
Sales Team Management Model for MyTriv ERP

This module handles sales team management and performance tracking.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class CrmTeam(models.Model):
    """Sales team model for MyTriv ERP"""

    _name = 'crm.team'
    _description = 'Sales Team'

    name = fields.Char(
        string='Sales Team',
        required=True,
        translate=True,
        help='Name of the sales team'
    )

    # Team Members
    user_id = fields.Many2one(
        'res.users',
        string='Team Leader',
        help='Leader of the sales team'
    )

    member_ids = fields.Many2many(
        'res.users',
        'crm_team_users_rel',
        'team_id',
        'user_id',
        string='Team Members',
        help='Members of the sales team'
    )

    # Team Settings
    color = fields.Integer(
        string='Color Index',
        help='Color for team in UI'
    )

    # Statistics
    lead_count = fields.Integer(
        string='Leads',
        compute='_compute_lead_count'
    )

    opportunity_count = fields.Integer(
        string='Opportunities',
        compute='_compute_opportunity_count'
    )

    won_opportunity_count = fields.Integer(
        string='Won Opportunities',
        compute='_compute_won_opportunity_count'
    )

    revenue_won = fields.Float(
        string='Revenue Won',
        compute='_compute_revenue_won'
    )

    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    @api.depends('member_ids')
    def _compute_lead_count(self):
        """Compute number of leads for team"""
        for team in self:
            team.lead_count = self.env['crm.lead'].search_count([
                ('team_id', '=', team.id)
            ])

    @api.depends('member_ids')
    def _compute_opportunity_count(self):
        """Compute number of opportunities for team"""
        for team in self:
            team.opportunity_count = self.env['crm.opportunity'].search_count([
                ('team_id', '=', team.id)
            ])

    @api.depends('member_ids')
    def _compute_won_opportunity_count(self):
        """Compute number of won opportunities for team"""
        for team in self:
            team.won_opportunity_count = self.env['crm.opportunity'].search_count([
                ('team_id', '=', team.id),
                ('stage_id.is_won', '=', True)
            ])

    @api.depends('member_ids')
    def _compute_revenue_won(self):
        """Compute revenue from won opportunities"""
        for team in self:
            opportunities = self.env['crm.opportunity'].search([
                ('team_id', '=', team.id),
                ('stage_id.is_won', '=', True)
            ])
            team.revenue_won = sum(opp.planned_revenue for opp in opportunities)

    def action_view_leads(self):
        """View leads for this team"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Team Leads'),
            'res_model': 'crm.lead',
            'view_mode': 'tree,form',
            'domain': [('team_id', '=', self.id)],
            'context': {'default_team_id': self.id}
        }

    def action_view_opportunities(self):
        """View opportunities for this team"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Team Opportunities'),
            'res_model': 'crm.opportunity',
            'view_mode': 'tree,form',
            'domain': [('team_id', '=', self.id)],
            'context': {'default_team_id': self.id}
        }