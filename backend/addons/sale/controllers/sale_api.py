# -*- coding: utf-8 -*-
"""
Sale API Controller for MyTriv ERP

This module provides REST API endpoints for sales functionality.
"""

import json
import logging
from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SaleApiController(http.Controller):
    """Sale API Controller"""

    @http.route('/api/sale/orders', type='json', auth='user', methods=['GET'])
    def get_orders(self, **kwargs):
        """Get sales orders list"""
        orders = request.env['sale.order'].search_read(
            domain=[('state', 'in', ['sale', 'done'])],
            fields=['id', 'name', 'order_id', 'partner_id', 'date_order', 'amount_total', 'state']
        )
        return {
            'success': True,
            'data': orders
        }

    @http.route('/api/sale/orders/<int:order_id>', type='json', auth='user', methods=['GET'])
    def get_order(self, order_id, **kwargs):
        """Get specific sales order"""
        order = request.env['sale.order'].browse(order_id)
        if not order.exists():
            return {
                'success': False,
                'error': 'Order not found'
            }

        return {
            'success': True,
            'data': {
                'id': order.id,
                'name': order.name,
                'order_id': order.order_id,
                'partner_id': order.partner_id.id if order.partner_id else None,
                'date_order': order.date_order.isoformat() if order.date_order else None,
                'amount_untaxed': order.amount_untaxed,
                'amount_tax': order.amount_tax,
                'amount_total': order.amount_total,
                'state': order.state,
                'order_lines': [{
                    'id': line.id,
                    'product_id': line.product_id.id if line.product_id else None,
                    'product_name': line.product_id.name if line.product_id else '',
                    'quantity': line.product_uom_qty,
                    'price_unit': line.price_unit,
                    'price_subtotal': line.price_subtotal,
                } for line in order.order_line]
            }
        }

    @http.route('/api/sale/orders', type='json', auth='user', methods=['POST'])
    def create_order(self, **kwargs):
        """Create new sales order"""
        try:
            # Create order lines
            order_lines = []
            for line_data in kwargs.get('order_lines', []):
                order_lines.append((0, 0, {
                    'product_id': line_data.get('product_id'),
                    'product_uom_qty': line_data.get('quantity', 1),
                    'price_unit': line_data.get('price_unit', 0),
                }))

            order = request.env['sale.order'].create({
                'partner_id': kwargs.get('partner_id'),
                'date_order': kwargs.get('date_order'),
                'order_line': order_lines,
            })

            return {
                'success': True,
                'data': {'id': order.id}
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @http.route('/api/sale/products', type='json', auth='user', methods=['GET'])
    def get_products(self, **kwargs):
        """Get products list"""
        products = request.env['product.product'].search_read(
            domain=[('active', '=', True), ('sale_ok', '=', True)],
            fields=['id', 'name', 'default_code', 'list_price', 'categ_id', 'type']
        )
        return {
            'success': True,
            'data': products
        }

    @http.route('/api/sale/products/<int:product_id>', type='json', auth='user', methods=['GET'])
    def get_product(self, product_id, **kwargs):
        """Get specific product"""
        product = request.env['product.product'].browse(product_id)
        if not product.exists():
            return {
                'success': False,
                'error': 'Product not found'
            }

        return {
            'success': True,
            'data': {
                'id': product.id,
                'name': product.name,
                'default_code': product.default_code,
                'barcode': product.barcode,
                'list_price': product.list_price,
                'standard_price': product.standard_price,
                'categ_id': product.categ_id.id if product.categ_id else None,
                'type': product.type,
                'description': product.description,
                'qty_available': product.qty_available,
            }
        }

    @http.route('/api/sale/customers', type='json', auth='user', methods=['GET'])
    def get_customers(self, **kwargs):
        """Get customers list"""
        customers = request.env['res.partner'].search_read(
            domain=[('active', '=', True), ('customer_rank', '>', 0)],
            fields=['id', 'name', 'email', 'phone', 'city', 'country_id']
        )
        return {
            'success': True,
            'data': customers
        }

    @http.route('/api/sale/invoices', type='json', auth='user', methods=['GET'])
    def get_invoices(self, **kwargs):
        """Get invoices list"""
        invoices = request.env['account.move'].search_read(
            domain=[('move_type', '=', 'out_invoice'), ('state', '=', 'posted')],
            fields=['id', 'name', 'partner_id', 'invoice_date', 'invoice_date_due', 'amount_total', 'payment_state']
        )
        return {
            'success': True,
            'data': invoices
        }

    @http.route('/api/sale/dashboard', type='json', auth='user', methods=['GET'])
    def get_sale_dashboard(self, **kwargs):
        """Get sales dashboard data"""
        try:
            # Sales statistics
            total_orders = request.env['sale.order'].search_count([
                ('state', 'in', ['sale', 'done'])
            ])

            total_revenue = sum(request.env['sale.order'].search([
                ('state', 'in', ['sale', 'done'])
            ]).mapped('amount_total'))

            # Monthly sales
            current_month_orders = request.env['sale.order'].search_count([
                ('state', 'in', ['sale', 'done']),
                ('date_order', '>=', datetime.now().replace(day=1))
            ])

            current_month_revenue = sum(request.env['sale.order'].search([
                ('state', 'in', ['sale', 'done']),
                ('date_order', '>=', datetime.now().replace(day=1))
            ]).mapped('amount_total'))

            # Product statistics
            total_products = request.env['product.product'].search_count([
                ('active', '=', True)
            ])

            low_stock_products = request.env['product.product'].search_count([
                ('active', '=', True),
                ('qty_available', '<', 10)
            ])

            # Customer statistics
            total_customers = request.env['res.partner'].search_count([
                ('active', '=', True),
                ('customer_rank', '>', 0)
            ])

            return {
                'success': True,
                'data': {
                    'total_orders': total_orders,
                    'total_revenue': total_revenue,
                    'current_month_orders': current_month_orders,
                    'current_month_revenue': current_month_revenue,
                    'total_products': total_products,
                    'low_stock_products': low_stock_products,
                    'total_customers': total_customers,
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }