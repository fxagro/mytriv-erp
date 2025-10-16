# -*- coding: utf-8 -*-
"""
CRM Funnel Analytics Model

This module provides analytics and reporting functionality for CRM sales funnels,
tracking conversion rates, lead progression, and sales performance metrics.
"""

from odoo import models, fields, api
from datetime import datetime, timedelta
from collections import defaultdict


class CrmFunnelAnalytics(models.Model):
    """CRM Funnel Analytics model for tracking sales performance."""

    _name = 'crm.funnel.analytics'
    _description = 'CRM Funnel Analytics and Reporting'
    _rec_name = 'period_name'

    # Basic fields
    period_name = fields.Char(
        string='Period',
        required=True,
        help='Name/identifier for the analytics period'
    )

    period_start = fields.Date(
        string='Period Start',
        required=True,
        help='Start date of the analytics period'
    )

    period_end = fields.Date(
        string='Period End',
        required=True,
        help='End date of the analytics period'
    )

    # Analytics fields
    total_leads = fields.Integer(
        string='Total Leads',
        default=0,
        help='Total number of leads in the period'
    )

    qualified_leads = fields.Integer(
        string='Qualified Leads',
        default=0,
        help='Number of qualified leads'
    )

    converted_leads = fields.Integer(
        string='Converted Leads',
        default=0,
        help='Number of leads converted to customers'
    )

    lost_leads = fields.Integer(
        string='Lost Leads',
        default=0,
        help='Number of lost leads'
    )

    # Conversion rates
    qualification_rate = fields.Float(
        string='Qualification Rate (%)',
        compute='_compute_conversion_rates',
        store=True,
        help='Percentage of leads that become qualified'
    )

    conversion_rate = fields.Float(
        string='Conversion Rate (%)',
        compute='_compute_conversion_rates',
        store=True,
        help='Percentage of qualified leads that convert to customers'
    )

    overall_conversion_rate = fields.Float(
        string='Overall Conversion Rate (%)',
        compute='_compute_conversion_rates',
        store=True,
        help='Overall conversion rate from lead to customer'
    )

    # Revenue metrics
    total_expected_revenue = fields.Monetary(
        string='Total Expected Revenue',
        currency_field='company_currency',
        default=0.0,
        help='Total expected revenue from all leads'
    )

    total_actual_revenue = fields.Monetary(
        string='Total Actual Revenue',
        currency_field='company_currency',
        default=0.0,
        help='Total actual revenue from converted leads'
    )

    average_deal_size = fields.Monetary(
        string='Average Deal Size',
        currency_field='company_currency',
        compute='_compute_average_deal_size',
        store=True,
        help='Average value of converted deals'
    )

    # Time-based metrics
    average_time_to_qualification = fields.Float(
        string='Avg. Time to Qualification (days)',
        default=0.0,
        help='Average time from lead creation to qualification'
    )

    average_time_to_conversion = fields.Float(
        string='Avg. Time to Conversion (days)',
        default=0.0,
        help='Average time from qualification to conversion'
    )

    average_sales_cycle = fields.Float(
        string='Average Sales Cycle (days)',
        compute='_compute_average_sales_cycle',
        store=True,
        help='Average time from lead creation to conversion'
    )

    @api.depends('qualified_leads', 'total_leads', 'converted_leads')
    def _compute_conversion_rates(self):
        """Compute various conversion rates."""
        for record in self:
            # Qualification rate
            if record.total_leads > 0:
                record.qualification_rate = (record.qualified_leads / record.total_leads) * 100
            else:
                record.qualification_rate = 0.0

            # Conversion rate (qualified to converted)
            if record.qualified_leads > 0:
                record.conversion_rate = (record.converted_leads / record.qualified_leads) * 100
            else:
                record.conversion_rate = 0.0

            # Overall conversion rate (lead to customer)
            if record.total_leads > 0:
                record.overall_conversion_rate = (record.converted_leads / record.total_leads) * 100
            else:
                record.overall_conversion_rate = 0.0

    @api.depends('total_actual_revenue', 'converted_leads')
    def _compute_average_deal_size(self):
        """Compute average deal size."""
        for record in self:
            if record.converted_leads > 0:
                record.average_deal_size = record.total_actual_revenue / record.converted_leads
            else:
                record.average_deal_size = 0.0

    @api.depends('average_time_to_qualification', 'average_time_to_conversion')
    def _compute_average_sales_cycle(self):
        """Compute average sales cycle time."""
        for record in self:
            record.average_sales_cycle = (
                record.average_time_to_qualification + record.average_time_to_conversion
            )

    def action_refresh_analytics(self):
        """Refresh analytics data from CRM leads."""
        self.ensure_one()
        self._compute_analytics_data()

    def _compute_analytics_data(self):
        """Compute analytics data from actual CRM leads."""
        self.ensure_one()

        # Get leads within the period
        leads = self.env['crm.lead'].search([
            ('create_date', '>=', self.period_start),
            ('create_date', '<=', self.period_end)
        ])

        # Basic counts
        self.total_leads = len(leads)
        self.qualified_leads = len(leads.filtered(lambda l: l.lead_qualification_status == 'qualified'))
        self.converted_leads = len(leads.filtered(lambda l: l.probability == 100))
        self.lost_leads = len(leads.filtered(lambda l: l.active == False and l.probability == 0))

        # Revenue calculations
        self.total_expected_revenue = sum(leads.mapped('expected_revenue'))
        converted_leads = leads.filtered(lambda l: l.probability == 100)
        self.total_actual_revenue = sum(converted_leads.mapped('expected_revenue'))

    @api.model
    def create_monthly_analytics(self, year=None, month=None):
        """Create monthly analytics record for the specified period."""
        if not year or not month:
            today = datetime.now()
            year = today.year
            month = today.month

        # Calculate period dates
        period_start = datetime(year, month, 1).date()
        if month == 12:
            period_end = datetime(year + 1, 1, 1).date() - timedelta(days=1)
        else:
            period_end = datetime(year, month + 1, 1).date() - timedelta(days=1)

        period_name = f"{year}-{month:02d}"

        # Check if analytics already exists
        existing = self.search([
            ('period_name', '=', period_name)
        ])

        if existing:
            return existing

        # Create new analytics record
        analytics = self.create({
            'period_name': period_name,
            'period_start': period_start,
            'period_end': period_end
        })

        # Compute analytics data
        analytics._compute_analytics_data()

        return analytics

    @api.model
    def get_funnel_overview(self, days=30):
        """Get funnel overview for the last N days."""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        # Get or create analytics for the period
        analytics = self.search([
            ('period_start', '>=', start_date),
            ('period_end', '<=', end_date)
        ], limit=1)

        if not analytics:
            analytics = self.create({
                'period_name': f'Last {days} days',
                'period_start': start_date,
                'period_end': end_date
            })
            analytics._compute_analytics_data()

        return {
            'period': analytics.period_name,
            'total_leads': analytics.total_leads,
            'qualified_leads': analytics.qualified_leads,
            'converted_leads': analytics.converted_leads,
            'qualification_rate': analytics.qualification_rate,
            'conversion_rate': analytics.conversion_rate,
            'overall_conversion_rate': analytics.overall_conversion_rate,
            'total_expected_revenue': analytics.total_expected_revenue,
            'total_actual_revenue': analytics.total_actual_revenue,
            'average_deal_size': analytics.average_deal_size,
            'average_sales_cycle': analytics.average_sales_cycle
        }