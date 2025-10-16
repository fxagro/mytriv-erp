# -*- coding: utf-8 -*-
"""
Custom Sale Order Model

This module extends the base sale order functionality with additional fields
and methods for enhanced sales order management.
"""

from odoo import models, fields, api


class SaleOrderCustom(models.Model):
    """Extended Sale Order model with custom fields and functionality."""

    _name = 'sale.order.custom'
    _description = 'Custom Sale Order Extensions'
    _inherit = ['sale.order']

    # Additional custom fields for enhanced sales order management
    order_priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], string='Order Priority', default='medium', help='Priority level of the sales order')

    order_source = fields.Selection([
        ('web', 'Website'),
        ('phone', 'Phone'),
        ('email', 'Email'),
        ('walk_in', 'Walk-in'),
        ('referral', 'Referral'),
        ('campaign', 'Marketing Campaign')
    ], string='Order Source', help='Source channel for the order')

    customer_rating = fields.Selection([
        ('1', 'Very Poor'),
        ('2', 'Poor'),
        ('3', 'Average'),
        ('4', 'Good'),
        ('5', 'Excellent')
    ], string='Customer Rating', help='Customer satisfaction rating')

    delivery_preference = fields.Selection([
        ('standard', 'Standard Delivery'),
        ('express', 'Express Delivery'),
        ('pickup', 'Customer Pickup'),
        ('scheduled', 'Scheduled Delivery')
    ], string='Delivery Preference', help='Customer preferred delivery method')

    special_instructions = fields.Text(
        string='Special Instructions',
        help='Special handling or delivery instructions'
    )

    internal_notes = fields.Text(
        string='Internal Notes',
        help='Internal notes for order processing'
    )

    # Financial tracking
    estimated_cost = fields.Monetary(
        string='Estimated Cost',
        currency_field='currency_id',
        help='Estimated cost to fulfill the order'
    )

    actual_cost = fields.Monetary(
        string='Actual Cost',
        currency_field='currency_id',
        compute='_compute_actual_cost',
        store=True,
        help='Actual cost incurred to fulfill the order'
    )

    profit_margin = fields.Monetary(
        string='Profit Margin',
        currency_field='currency_id',
        compute='_compute_profit_margin',
        store=True,
        help='Profit margin for the order'
    )

    # Dates and tracking
    order_confirmation_date = fields.Datetime(
        string='Order Confirmation Date',
        help='Date when order was confirmed'
    )

    expected_delivery_date = fields.Date(
        string='Expected Delivery Date',
        help='Expected date for order delivery'
    )

    actual_delivery_date = fields.Date(
        string='Actual Delivery Date',
        help='Actual date when order was delivered'
    )

    # Customer relationship
    customer_type = fields.Selection([
        ('new', 'New Customer'),
        ('returning', 'Returning Customer'),
        ('vip', 'VIP Customer'),
        ('enterprise', 'Enterprise Customer')
    ], string='Customer Type', help='Classification of customer relationship')

    referral_source = fields.Char(
        string='Referral Source',
        help='Source of customer referral if applicable'
    )

    @api.depends('order_line.product_id', 'order_line.product_uom_qty')
    def _compute_actual_cost(self):
        """Compute actual cost based on product costs."""
        for order in self:
            total_cost = 0.0
            for line in order.order_line:
                if line.product_id and line.product_id.standard_price:
                    total_cost += line.product_id.standard_price * line.product_uom_qty
            order.actual_cost = total_cost

    @api.depends('amount_total', 'actual_cost')
    def _compute_profit_margin(self):
        """Compute profit margin."""
        for order in self:
            if order.amount_total > 0:
                order.profit_margin = order.amount_total - order.actual_cost
            else:
                order.profit_margin = 0.0

    def action_confirm_order(self):
        """Confirm the sales order."""
        self.write({
            'state': 'sale',
            'order_confirmation_date': fields.Datetime.now()
        })

    def action_mark_delivered(self):
        """Mark order as delivered."""
        self.write({
            'actual_delivery_date': fields.Date.today()
        })

    def get_order_summary(self):
        """Get comprehensive order summary."""
        self.ensure_one()
        return {
            'order_name': self.name,
            'partner_name': self.partner_id.name if self.partner_id else None,
            'order_priority': self.order_priority,
            'order_source': self.order_source,
            'customer_rating': self.customer_rating,
            'amount_total': self.amount_total,
            'estimated_cost': self.estimated_cost,
            'actual_cost': self.actual_cost,
            'profit_margin': self.profit_margin,
            'order_confirmation_date': self.order_confirmation_date,
            'expected_delivery_date': self.expected_delivery_date,
            'actual_delivery_date': self.actual_delivery_date,
            'customer_type': self.customer_type,
            'state': self.state
        }

    @api.model
    def get_orders_by_priority(self, priority):
        """Get all orders with specific priority."""
        return self.search([('order_priority', '=', priority)])

    @api.model
    def get_orders_by_source(self, source):
        """Get all orders from specific source."""
        return self.search([('order_source', '=', source)])

    @api.model
    def get_pending_orders(self):
        """Get all pending orders."""
        return self.search([('state', 'in', ['draft', 'sent'])])

    @api.model
    def get_overdue_orders(self):
        """Get orders past expected delivery date."""
        return self.search([
            ('expected_delivery_date', '<', fields.Date.today()),
            ('actual_delivery_date', '=', False)
        ])