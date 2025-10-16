# -*- coding: utf-8 -*-
"""
Pipeline Stage Management Model for MyTriv ERP

This module handles sales pipeline stage management.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class CrmStage(models.Model):
    """Pipeline stage model for MyTriv ERP"""

    _name = 'crm.stage'
    _description = 'Sales Stage'
    _order = 'sequence'

    name = fields.Char(
        string='Stage Name',
        required=True,
        translate=True,
        help='Name of the sales stage'
    )

    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of the stage in pipeline'
    )

    # Stage Properties
    is_won = fields.Boolean(
        string='Is Won Stage',
        help='This stage represents a won opportunity'
    )

    is_default = fields.Boolean(
        string='Is Default',
        help='Default stage for new leads/opportunities'
    )

    # Requirements
    requirements = fields.Text(
        string='Requirements',
        help='Requirements for reaching this stage'
    )

    # Probability
    probability = fields.Float(
        string='Probability (%)',
        default=0.0,
        help='Default probability for this stage'
    )

    # Color for UI
    color = fields.Integer(
        string='Color Index',
        help='Color for stage in UI'
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

    @api.depends('lead_ids')
    def _compute_lead_count(self):
        """Compute number of leads in this stage"""
        for stage in self:
            stage.lead_count = len(stage.lead_ids)

    @api.depends('opportunity_ids')
    def _compute_opportunity_count(self):
        """Compute number of opportunities in this stage"""
        for stage in self:
            stage.opportunity_count = len(stage.opportunity_ids)

    def action_view_leads(self):
        """View leads in this stage"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Stage Leads'),
            'res_model': 'crm.lead',
            'view_mode': 'tree,form',
            'domain': [('stage_id', '=', self.id)],
            'context': {'default_stage_id': self.id}
        }

    def action_view_opportunities(self):
        """View opportunities in this stage"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Stage Opportunities'),
            'res_model': 'crm.opportunity',
            'view_mode': 'tree,form',
            'domain': [('stage_id', '=', self.id)],
            'context': {'default_stage_id': self.id}
        }