# -*- coding: utf-8 -*-
"""
Custom Customer Model

This module extends customer/partner functionality with enhanced
tracking and relationship management.
"""

from odoo import models, fields, api


class CustomerCustom(models.Model):
    """Extended Customer/Partner model with custom fields and functionality."""

    _name = 'res.partner.custom'
    _description = 'Custom Customer Extensions'
    _inherit = ['res.partner']

    # Additional custom fields for enhanced customer management
    customer_segment = fields.Selection([
        ('individual', 'Individual'),
        ('small_business', 'Small Business'),
        ('medium_enterprise', 'Medium Enterprise'),
        ('large_enterprise', 'Large Enterprise'),
        ('government', 'Government'),
        ('non_profit', 'Non-profit')
    ], string='Customer Segment', help='Customer business segment classification')

    industry = fields.Selection([
        ('technology', 'Technology'),
        ('healthcare', 'Healthcare'),
        ('finance', 'Finance'),
        ('education', 'Education'),
        ('retail', 'Retail'),
        ('manufacturing', 'Manufacturing'),
        ('construction', 'Construction'),
        ('hospitality', 'Hospitality'),
        ('other', 'Other')
    ], string='Industry', help='Industry classification')

    customer_status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('prospect', 'Prospect'),
        ('suspended', 'Suspended'),
        ('vip', 'VIP')
    ], string='Customer Status', default='active', help='Current status of customer relationship')

    credit_limit = fields.Monetary(
        string='Credit Limit',
        currency_field='currency_id',
        help='Maximum credit allowed for this customer'
    )

    current_credit = fields.Monetary(
        string='Current Credit Used',
        currency_field='currency_id',
        compute='_compute_current_credit',
        store=True,
        help='Current credit utilization'
    )

    available_credit = fields.Monetary(
        string='Available Credit',
        currency_field='currency_id',
        compute='_compute_available_credit',
        store=True,
        help='Remaining available credit'
    )

    # Relationship tracking
    relationship_manager = fields.Many2one(
        'res.users',
        string='Relationship Manager',
        help='User responsible for managing this customer relationship'
    )

    last_contact_date = fields.Date(
        string='Last Contact Date',
        help='Date of last interaction with customer'
    )

    next_follow_up_date = fields.Date(
        string='Next Follow-up Date',
        help='Scheduled date for next customer interaction'
    )

    total_orders_value = fields.Monetary(
        string='Total Orders Value',
        currency_field='currency_id',
        compute='_compute_total_orders_value',
        store=True,
        help='Total value of all orders from this customer'
    )

    average_order_value = fields.Monetary(
        string='Average Order Value',
        currency_field='currency_id',
        compute='_compute_average_order_value',
        store=True,
        help='Average value per order'
    )

    # Communication preferences
    preferred_contact_method = fields.Selection([
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('sms', 'SMS'),
        ('mail', 'Physical Mail')
    ], string='Preferred Contact Method', help='Customer preferred communication method')

    newsletter_subscribed = fields.Boolean(
        string='Newsletter Subscribed',
        default=False,
        help='Whether customer is subscribed to newsletter'
    )

    marketing_opt_in = fields.Boolean(
        string='Marketing Opt-in',
        default=True,
        help='Whether customer has opted in for marketing communications'
    )

    @api.depends('sale_order_ids.amount_total', 'sale_order_ids.state')
    def _compute_total_orders_value(self):
        """Compute total value of confirmed orders."""
        for partner in self:
            confirmed_orders = partner.sale_order_ids.filtered(lambda o: o.state in ['sale', 'done'])
            partner.total_orders_value = sum(confirmed_orders.mapped('amount_total'))

    @api.depends('total_orders_value', 'sale_order_ids')
    def _compute_average_order_value(self):
        """Compute average order value."""
        for partner in self:
            confirmed_orders = partner.sale_order_ids.filtered(lambda o: o.state in ['sale', 'done'])
            if confirmed_orders:
                partner.average_order_value = partner.total_orders_value / len(confirmed_orders)
            else:
                partner.average_order_value = 0.0

    @api.depends('credit_limit', 'current_credit')
    def _compute_available_credit(self):
        """Compute available credit."""
        for partner in self:
            partner.available_credit = partner.credit_limit - partner.current_credit

    def _compute_current_credit(self):
        """Compute current credit utilization."""
        for partner in self:
            # This would typically involve complex calculations based on unpaid invoices
            # For now, using a simplified approach
            unpaid_invoices = self.env['account.move'].search([
                ('partner_id', '=', partner.id),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', 'in', ['not_paid', 'partial'])
            ])
            partner.current_credit = sum(unpaid_invoices.mapped('amount_residual'))

    def action_update_last_contact(self):
        """Update last contact date to today."""
        self.write({'last_contact_date': fields.Date.today()})

    def action_schedule_follow_up(self, days=30):
        """Schedule a follow-up action."""
        follow_up_date = fields.Date.today() + timedelta(days=days)
        self.write({'next_follow_up_date': follow_up_date})

    def action_upgrade_to_vip(self):
        """Upgrade customer to VIP status."""
        self.write({'customer_status': 'vip'})

    def action_suspend_customer(self):
        """Suspend customer relationship."""
        self.write({'customer_status': 'suspended'})

    def get_customer_summary(self):
        """Get comprehensive customer summary."""
        self.ensure_one()
        return {
            'customer_name': self.name,
            'customer_segment': self.customer_segment,
            'industry': self.industry,
            'customer_status': self.customer_status,
            'credit_limit': self.credit_limit,
            'current_credit': self.current_credit,
            'available_credit': self.available_credit,
            'total_orders_value': self.total_orders_value,
            'average_order_value': self.average_order_value,
            'relationship_manager': self.relationship_manager.name if self.relationship_manager else None,
            'last_contact_date': self.last_contact_date,
            'next_follow_up_date': self.next_follow_up_date,
            'preferred_contact_method': self.preferred_contact_method,
            'customer_rank': self.customer_rank
        }

    @api.model
    def get_customers_by_segment(self, segment):
        """Get all customers in specific segment."""
        return self.search([('customer_segment', '=', segment)])

    @api.model
    def get_vip_customers(self):
        """Get all VIP customers."""
        return self.search([('customer_status', '=', 'vip')])

    @api.model
    def get_customers_needing_follow_up(self):
        """Get customers that need follow-up."""
        today = fields.Date.today()
        return self.search([
            ('next_follow_up_date', '<=', today),
            ('customer_status', 'in', ['active', 'vip'])
        ])

    @api.model
    def get_credit_limit_exceeded(self):
        """Get customers who have exceeded credit limit."""
        return self.search([
            ('available_credit', '<', 0),
            ('customer_status', 'in', ['active', 'vip'])
        ])