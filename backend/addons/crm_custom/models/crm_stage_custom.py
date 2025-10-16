# -*- coding: utf-8 -*-
"""
Custom CRM Stage Model

This module provides custom CRM stage functionality with additional
tracking and analytics capabilities.
"""

from odoo import models, fields, api


class CrmStageCustom(models.Model):
    """Custom CRM Stage model for enhanced stage management."""

    _name = 'crm.stage.custom'
    _description = 'Custom CRM Stage Extensions'
    _inherit = ['crm.stage']

    # Additional fields for custom stage management
    stage_color_code = fields.Char(
        string='Stage Color Code',
        help='Hex color code for stage visualization'
    )

    stage_order = fields.Integer(
        string='Stage Order',
        default=0,
        help='Order/sequence of the stage in the pipeline'
    )

    is_active = fields.Boolean(
        string='Is Active',
        default=True,
        help='Whether this stage is currently active'
    )

    average_conversion_time = fields.Float(
        string='Average Conversion Time (days)',
        compute='_compute_average_conversion_time',
        store=True,
        help='Average time leads spend in this stage before conversion'
    )

    success_rate = fields.Float(
        string='Success Rate (%)',
        compute='_compute_success_rate',
        store=True,
        help='Percentage of leads that successfully move from this stage'
    )

    lead_count = fields.Integer(
        string='Lead Count',
        compute='_compute_lead_count',
        store=True,
        help='Number of leads currently in this stage'
    )

    @api.depends('name')
    def _compute_lead_count(self):
        """Compute the number of leads in this stage."""
        for stage in self:
            leads = self.env['crm.lead'].search([
                ('stage_id', '=', stage.id)
            ])
            stage.lead_count = len(leads)

    @api.depends('name')
    def _compute_average_conversion_time(self):
        """Compute average conversion time for this stage."""
        for stage in self:
            # This would typically involve complex analytics queries
            # For now, setting a default value
            stage.average_conversion_time = 7.0  # 7 days average

    @api.depends('name')
    def _compute_success_rate(self):
        """Compute success rate for this stage."""
        for stage in self:
            # This would typically involve complex analytics queries
            # For now, setting a default value based on stage type
            if stage.name:
                stage_name_lower = stage.name.lower()
                if 'won' in stage_name_lower or 'closed' in stage_name_lower:
                    stage.success_rate = 100.0
                elif 'lost' in stage_name_lower:
                    stage.success_rate = 0.0
                else:
                    stage.success_rate = 75.0  # Default success rate
            else:
                stage.success_rate = 50.0

    def action_activate_stage(self):
        """Activate the stage."""
        self.write({'is_active': True})

    def action_deactivate_stage(self):
        """Deactivate the stage."""
        self.write({'is_active': False})

    def get_stage_statistics(self):
        """Get comprehensive statistics for this stage."""
        self.ensure_one()
        return {
            'stage_name': self.name,
            'lead_count': self.lead_count,
            'average_conversion_time': self.average_conversion_time,
            'success_rate': self.success_rate,
            'is_active': self.is_active,
            'stage_order': self.stage_order
        }

    @api.model
    def get_pipeline_overview(self):
        """Get overview of all active stages in the pipeline."""
        stages = self.search([('is_active', '=', True)], order='stage_order')
        overview = []

        for stage in stages:
            overview.append(stage.get_stage_statistics())

        return overview