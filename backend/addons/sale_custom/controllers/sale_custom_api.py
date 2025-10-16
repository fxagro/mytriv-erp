# -*- coding: utf-8 -*-
"""
Sale Custom API Controller

This module provides REST API endpoints for sale custom functionality,
extending the base REST API with sales-specific operations.
"""

import json
from odoo import http
from odoo.http import request
from datetime import datetime


class SaleCustomAPI(http.Controller):
    """REST API controller for sale custom operations."""

    @http.route('/api/v1/sale/orders', type='json', auth='user', methods=['GET'], csrf=False)
    def get_sale_orders(self, **kwargs):
        """Get sale orders with optional filtering."""
        try:
            # Get query parameters
            priority = kwargs.get('priority')
            source = kwargs.get('source')
            customer_id = kwargs.get('customer_id')
            state = kwargs.get('state')
            limit = int(kwargs.get('limit', 100))
            offset = int(kwargs.get('offset', 0))

            # Build domain for filtering
            domain = []
            if priority:
                domain.append(('order_priority', '=', priority))
            if source:
                domain.append(('order_source', '=', source))
            if customer_id:
                domain.append(('partner_id', '=', int(customer_id)))
            if state:
                domain.append(('state', '=', state))

            # Search sale orders
            orders = request.env['sale.order'].sudo().search(
                domain,
                limit=limit,
                offset=offset
            )

            # Format response data
            data = []
            for order in orders:
                order_data = {
                    'id': order.id,
                    'name': order.name,
                    'partner_name': order.partner_id.name if order.partner_id else None,
                    'order_priority': order.order_priority,
                    'order_source': order.order_source,
                    'customer_rating': order.customer_rating,
                    'amount_total': order.amount_total,
                    'estimated_cost': order.estimated_cost,
                    'actual_cost': order.actual_cost,
                    'profit_margin': order.profit_margin,
                    'order_confirmation_date': order.order_confirmation_date.isoformat() if order.order_confirmation_date else None,
                    'expected_delivery_date': order.expected_delivery_date.isoformat() if order.expected_delivery_date else None,
                    'actual_delivery_date': order.actual_delivery_date.isoformat() if order.actual_delivery_date else None,
                    'customer_type': order.customer_type,
                    'state': order.state
                }
                data.append(order_data)

            return {
                'orders': data,
                'count': len(data),
                'total': len(request.env['sale.order'].sudo().search(domain))
            }

        except Exception as e:
            return {'error': str(e)}

    @http.route('/api/v1/sale/customers', type='json', auth='user', methods=['GET'], csrf=False)
    def get_customers(self, **kwargs):
        """Get customers with optional filtering."""
        try:
            # Get query parameters
            segment = kwargs.get('segment')
            industry = kwargs.get('industry')
            status = kwargs.get('status')
            limit = int(kwargs.get('limit', 100))
            offset = int(kwargs.get('offset', 0))

            # Build domain for filtering
            domain = [('customer_rank', '>', 0)]  # Only customers
            if segment:
                domain.append(('customer_segment', '=', segment))
            if industry:
                domain.append(('industry', '=', industry))
            if status:
                domain.append(('customer_status', '=', status))

            # Search customers
            customers = request.env['res.partner'].sudo().search(
                domain,
                limit=limit,
                offset=offset
            )

            # Format response data
            data = []
            for customer in customers:
                customer_data = {
                    'id': customer.id,
                    'name': customer.name,
                    'email': customer.email,
                    'phone': customer.phone,
                    'customer_segment': customer.customer_segment,
                    'industry': customer.industry,
                    'customer_status': customer.customer_status,
                    'credit_limit': customer.credit_limit,
                    'current_credit': customer.current_credit,
                    'available_credit': customer.available_credit,
                    'total_orders_value': customer.total_orders_value,
                    'average_order_value': customer.average_order_value,
                    'relationship_manager': customer.relationship_manager.name if customer.relationship_manager else None,
                    'last_contact_date': customer.last_contact_date.isoformat() if customer.last_contact_date else None,
                    'next_follow_up_date': customer.next_follow_up_date.isoformat() if customer.next_follow_up_date else None,
                    'customer_rank': customer.customer_rank
                }
                data.append(customer_data)

            return {
                'customers': data,
                'count': len(data),
                'total': len(request.env['res.partner'].sudo().search(domain))
            }

        except Exception as e:
            return {'error': str(e)}

    @http.route('/api/v1/sale/dashboard', type='json', auth='user', methods=['GET'], csrf=False)
    def get_sale_dashboard(self):
        """Get sales dashboard data."""
        try:
            # Get pending orders
            pending_orders = request.env['sale.order'].sudo().get_pending_orders()

            # Get overdue orders
            overdue_orders = request.env['sale.order'].sudo().get_overdue_orders()

            # Get customers needing follow-up
            follow_up_customers = request.env['res.partner'].sudo().get_customers_needing_follow_up()

            # Get credit limit exceeded
            credit_exceeded_customers = request.env['res.partner'].sudo().get_credit_limit_exceeded()

            # Get VIP customers
            vip_customers = request.env['res.partner'].sudo().get_vip_customers()

            dashboard_data = {
                'pending_orders_count': len(pending_orders),
                'overdue_orders_count': len(overdue_orders),
                'follow_up_customers_count': len(follow_up_customers),
                'credit_exceeded_customers_count': len(credit_exceeded_customers),
                'vip_customers_count': len(vip_customers),
                'generated_at': datetime.now().isoformat()
            }

            return {'dashboard': dashboard_data}

        except Exception as e:
            return {'error': str(e)}