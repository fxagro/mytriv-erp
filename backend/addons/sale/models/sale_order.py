# -*- coding: utf-8 -*-
"""
Sales Order Management Model for MyTriv ERP

This module handles sales order processing and management.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    """Sales order model for MyTriv ERP"""

    _name = 'sale.order'
    _description = 'Sales Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Basic Information
    name = fields.Char(
        string='Order Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )

    order_id = fields.Char(
        string='Order ID',
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
        help='Customer for this order'
    )

    partner_shipping_id = fields.Many2one(
        'res.partner',
        string='Shipping Address',
        help='Shipping address for this order'
    )

    partner_invoice_id = fields.Many2one(
        'res.partner',
        string='Invoice Address',
        help='Invoice address for this order'
    )

    # Order Details
    date_order = fields.Datetime(
        string='Order Date',
        required=True,
        default=lambda self: datetime.now(),
        help='Date when order was created'
    )

    validity_date = fields.Date(
        string='Expiration Date',
        help='Date until quotation is valid'
    )

    # Order Lines
    order_line = fields.One2many(
        'sale.order.line',
        'order_id',
        string='Order Lines',
        help='Products in this order'
    )

    # Pricing
    amount_untaxed = fields.Float(
        string='Untaxed Amount',
        compute='_compute_amount',
        store=True,
        help='Total amount before taxes'
    )

    amount_tax = fields.Float(
        string='Taxes',
        compute='_compute_amount',
        store=True,
        help='Total tax amount'
    )

    amount_total = fields.Float(
        string='Total',
        compute='_compute_amount',
        store=True,
        help='Total amount including taxes'
    )

    # Payment
    payment_term_id = fields.Many2one(
        'account.payment.term',
        string='Payment Terms',
        help='Payment terms for this order'
    )

    # Sales Team
    team_id = fields.Many2one(
        'crm.team',
        string='Sales Team',
        help='Sales team responsible for this order'
    )

    user_id = fields.Many2one(
        'res.users',
        string='Salesperson',
        default=lambda self: self.env.user,
        help='Salesperson responsible for this order'
    )

    # Status
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', track_visibility='onchange')

    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    # Notes
    note = fields.Text(
        string='Terms and Conditions',
        help='Terms and conditions for this order'
    )

    @api.model
    def create(self, vals):
        """Create sales order with auto-generated IDs"""
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self._generate_order_name()

        if vals.get('order_id', _('New')) == _('New'):
            vals['order_id'] = self._generate_order_id()

        return super(SaleOrder, self).create(vals)

    def _generate_order_name(self):
        """Generate order name"""
        return self.env['ir.sequence'].next_by_code('sale.order') or _('New')

    def _generate_order_id(self):
        """Generate unique order ID"""
        sequence = self.env['ir.sequence'].search([
            ('code', '=', 'sale.order.id')
        ], limit=1)

        if sequence:
            return sequence.next_by_id()
        else:
            last_order = self.search([], order='id desc', limit=1)
            return f'SO{(last_order.id + 1):04d}' if last_order else 'SO0001'

    @api.depends('order_line.price_subtotal', 'order_line.price_tax')
    def _compute_amount(self):
        """Compute order totals"""
        for order in self:
            amount_untaxed = sum(line.price_subtotal for line in order.order_line)
            amount_tax = sum(line.price_tax for line in order.order_line)

            order.amount_untaxed = amount_untaxed
            order.amount_tax = amount_tax
            order.amount_total = amount_untaxed + amount_tax

    def action_confirm(self):
        """Confirm sales order"""
        self.write({'state': 'sale'})

    def action_quotation_send(self):
        """Send quotation to customer"""
        self.write({'state': 'sent'})

    def action_cancel(self):
        """Cancel sales order"""
        self.write({'state': 'cancel'})

    def action_done(self):
        """Mark order as done"""
        self.write({'state': 'done'})

    def action_view_invoice(self):
        """View invoice for this order"""
        self.ensure_one()
        invoices = self.env['account.move'].search([
            ('sale_order_id', '=', self.id)
        ])

        if invoices:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Invoices'),
                'res_model': 'account.move',
                'view_mode': 'tree,form',
                'domain': [('sale_order_id', '=', self.id)],
            }
        return False

    def action_view_delivery(self):
        """View delivery for this order"""
        self.ensure_one()
        deliveries = self.env['stock.picking'].search([
            ('sale_order_id', '=', self.id)
        ])

        if deliveries:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Deliveries'),
                'res_model': 'stock.picking',
                'view_mode': 'tree,form',
                'domain': [('sale_order_id', '=', self.id)],
            }
        return False

    @api.model
    def get_sales_summary(self, start_date=None, end_date=None):
        """Get sales summary for date range"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()

        orders = self.search([
            ('date_order', '>=', start_date),
            ('date_order', '<=', end_date),
            ('state', 'in', ['sale', 'done'])
        ])

        total_orders = len(orders)
        total_amount = sum(order.amount_total for order in orders)

        return {
            'total_orders': total_orders,
            'total_amount': total_amount,
            'average_order_value': total_amount / total_orders if total_orders > 0 else 0,
        }


class SaleOrderLine(models.Model):
    """Sales order line model"""

    _name = 'sale.order.line'
    _description = 'Sales Order Line'

    order_id = fields.Many2one(
        'sale.order',
        string='Order',
        required=True,
        ondelete='cascade'
    )

    # Product Information
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        help='Product being sold'
    )

    product_uom = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        help='Unit of measure for this product'
    )

    product_uom_qty = fields.Float(
        string='Quantity',
        required=True,
        default=1,
        help='Quantity of product'
    )

    # Pricing
    price_unit = fields.Float(
        string='Unit Price',
        required=True,
        help='Price per unit'
    )

    price_subtotal = fields.Float(
        string='Subtotal',
        compute='_compute_amount',
        store=True,
        help='Subtotal before taxes'
    )

    price_tax = fields.Float(
        string='Tax',
        compute='_compute_amount',
        store=True,
        help='Tax amount'
    )

    price_total = fields.Float(
        string='Total',
        compute='_compute_amount',
        store=True,
        help='Total including taxes'
    )

    # Discounts
    discount = fields.Float(
        string='Discount (%)',
        default=0.0,
        help='Discount percentage'
    )

    discount_amount = fields.Float(
        string='Discount Amount',
        compute='_compute_discount_amount',
        store=True,
        help='Discount amount'
    )

    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='order_id.company_id',
        store=True
    )

    @api.depends('product_uom_qty', 'price_unit', 'discount')
    def _compute_amount(self):
        """Compute line amounts"""
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            subtotal = price * line.product_uom_qty

            line.price_subtotal = subtotal
            line.price_total = subtotal * (1 + (line.tax_rate or 0.0) / 100.0)
            line.price_tax = line.price_total - subtotal

    @api.depends('price_subtotal', 'discount')
    def _compute_discount_amount(self):
        """Compute discount amount"""
        for line in self:
            if line.discount:
                line.discount_amount = line.price_subtotal * (line.discount / 100)
            else:
                line.discount_amount = 0.0

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Update fields when product changes"""
        if self.product_id:
            self.price_unit = self.product_id.list_price
            self.product_uom = self.product_id.uom_id
            self.name = self.product_id.name

    def action_view_product(self):
        """View product details"""
        self.ensure_one()
        if self.product_id:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Product'),
                'res_model': 'product.product',
                'view_mode': 'form',
                'res_id': self.product_id.id
            }
        return False