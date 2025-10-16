# -*- coding: utf-8 -*-
"""
Custom CRM Lead Model

This module extends the base CRM lead functionality with additional fields
and methods for enhanced lead management and tracking.
"""

from odoo import models, fields, api
from datetime import datetime, timedelta


class CrmLeadCustom(models.Model):
    """Extended CRM Lead model with custom fields and functionality."""

    _name = 'crm.lead.custom'
    _description = 'Custom CRM Lead Extensions'
    _inherit = ['crm.lead']

    # Additional custom fields for enhanced lead management
    lead_source_detail = fields.Char(
        string='Lead Source Detail',
        help='Detailed information about how the lead was acquired'
    )

    lead_priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], string='Priority', default='medium', help='Priority level of the lead')

    expected_revenue = fields.Monetary(
        string='Expected Revenue',
        currency_field='company_currency',
        help='Estimated revenue expected from this lead'
    )

    conversion_probability = fields.Float(
        string='Conversion Probability (%)',
        default=0.0,
        help='Probability of converting this lead to a customer'
    )

    last_contact_date = fields.Datetime(
        string='Last Contact Date',
        help='Date and time of last contact with this lead'
    )

    next_follow_up_date = fields.Datetime(
        string='Next Follow-up Date',
        help='Scheduled date for next follow-up action'
    )

    lead_qualification_status = fields.Selection([
        ('new', 'New'),
        ('qualified', 'Qualified'),
        ('unqualified', 'Unqualified'),
        ('nurturing', 'Nurturing')
    ], string='Qualification Status', default='new')

    assigned_user_id = fields.Many2one(
        'res.users',
        string='Assigned User',
        help='User responsible for managing this lead'
    )

    # Computed fields for analytics
    days_since_creation = fields.Integer(
        string='Days Since Creation',
        compute='_compute_days_since_creation',
        store=True
    )

    is_overdue = fields.Boolean(
        string='Is Overdue',
        compute='_compute_is_overdue',
        store=True,
        help='True if the lead is past its expected close date'
    )

    @api.depends('create_date')
    def _compute_days_since_creation(self):
        """Compute the number of days since lead creation."""
        for lead in self:
            if lead.create_date:
                delta = datetime.now() - lead.create_date
                lead.days_since_creation = delta.days
            else:
                lead.days_since_creation = 0

    @api.depends('date_deadline')
    def _compute_is_overdue(self):
        """Compute if the lead is overdue."""
        for lead in self:
            lead.is_overdue = False
            if lead.date_deadline and lead.date_deadline < datetime.now():
                lead.is_overdue = True

    def action_set_qualified(self):
        """Mark lead as qualified."""
        self.write({'lead_qualification_status': 'qualified'})

    def action_set_unqualified(self):
        """Mark lead as unqualified."""
        self.write({'lead_qualification_status': 'unqualified'})

    def action_schedule_follow_up(self, days=7):
        """Schedule a follow-up action."""
        follow_up_date = datetime.now() + timedelta(days=days)
        self.write({'next_follow_up_date': follow_up_date})

    def action_update_last_contact(self):
        """Update the last contact date to now."""
        self.write({'last_contact_date': datetime.now()})

    @api.model
    def get_leads_by_priority(self, priority):
        """Get leads filtered by priority."""
        return self.search([('lead_priority', '=', priority)])

    @api.model
    def get_overdue_leads(self):
        """Get all overdue leads."""
        return self.search([('is_overdue', '=', True)])

    @api.model
    def get_leads_needing_follow_up(self):
        """Get leads that need follow-up today."""
        today = datetime.now().date()
        return self.search([
            ('next_follow_up_date', '<=', today),
            ('lead_qualification_status', '!=', 'unqualified')
        ])