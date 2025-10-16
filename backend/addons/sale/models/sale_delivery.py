# -*- coding: utf-8 -*-
"""
Delivery Management Model for MyTriv ERP

This module handles delivery and shipping management.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    """Delivery/Picking model for MyTriv ERP"""

    _name = 'stock.picking'
    _description = 'Delivery'

    name = fields.Char(
        string='Delivery Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )

    # Related Records
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sales Order',
        help='Related sales order'
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        help='Customer for this delivery'
    )

    # Delivery Details
    scheduled_date = fields.Datetime(
        string='Scheduled Date',
        default=lambda self: datetime.now() + timedelta(days=1),
        help='Scheduled delivery date'
    )

    date_done = fields.Datetime(
        string='Effective Date',
        help='Date when delivery was completed'
    )

    # Picking Type
    picking_type_id = fields.Many2one(
        'stock.picking.type',
        string='Operation Type',
        required=True,
        help='Type of picking operation'
    )

    # Location
    location_id = fields.Many2one(
        'stock.location',
        string='Source Location',
        required=True,
        help='Source location for picking'
    )

    location_dest_id = fields.Many2one(
        'stock.location',
        string='Destination Location',
        required=True,
        help='Destination location for picking'
    )

    # Products
    move_lines = fields.One2many(
        'stock.move',
        'picking_id',
        string='Stock Moves',
        help='Products to be moved'
    )

    # Package Information
    package_ids = fields.One2many(
        'stock.quant.package',
        'picking_id',
        string='Packages',
        help='Packages for this delivery'
    )

    # Carrier Information
    carrier_id = fields.Many2one(
        'delivery.carrier',
        string='Carrier',
        help='Shipping carrier'
    )

    carrier_tracking_ref = fields.Char(
        string='Tracking Reference',
        help='Carrier tracking reference'
    )

    # Weight and Volume
    weight = fields.Float(
        string='Weight',
        compute='_compute_weight',
        help='Total weight of delivery'
    )

    volume = fields.Float(
        string='Volume',
        compute='_compute_volume',
        help='Total volume of delivery'
    )

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting Availability'),
        ('assigned', 'Ready to Transfer'),
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

    @api.depends('move_lines.product_qty', 'move_lines.product_id.weight')
    def _compute_weight(self):
        """Compute total weight"""
        for picking in self:
            weight = 0.0
            for move in picking.move_lines:
                if move.product_id.weight:
                    weight += move.product_qty * move.product_id.weight
            picking.weight = weight

    @api.depends('move_lines.product_qty', 'move_lines.product_id.volume')
    def _compute_volume(self):
        """Compute total volume"""
        for picking in self:
            volume = 0.0
            for move in picking.move_lines:
                if move.product_id.volume:
                    volume += move.product_qty * move.product_id.volume
            picking.volume = volume

    def action_confirm(self):
        """Confirm delivery"""
        self.write({'state': 'confirmed'})

    def action_assign(self):
        """Assign products to delivery"""
        self.write({'state': 'assigned'})

    def action_done(self):
        """Mark delivery as done"""
        self.write({
            'state': 'done',
            'date_done': datetime.now()
        })

    def action_cancel(self):
        """Cancel delivery"""
        self.write({'state': 'cancel'})

    def action_view_stock_moves(self):
        """View stock moves"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Stock Moves'),
            'res_model': 'stock.move',
            'view_mode': 'tree,form',
            'domain': [('picking_id', '=', self.id)],
        }


class StockMove(models.Model):
    """Stock move model"""

    _name = 'stock.move'
    _description = 'Stock Move'

    name = fields.Char(
        string='Description',
        required=True,
        help='Move description'
    )

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        help='Product being moved'
    )

    product_uom_qty = fields.Float(
        string='Quantity',
        required=True,
        help='Quantity to move'
    )

    product_uom = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        required=True,
        help='Unit of measure'
    )

    location_id = fields.Many2one(
        'stock.location',
        string='Source Location',
        required=True
    )

    location_dest_id = fields.Many2one(
        'stock.location',
        string='Destination Location',
        required=True
    )

    picking_id = fields.Many2one(
        'stock.picking',
        string='Delivery',
        help='Related delivery'
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('assigned', 'Assigned'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft')

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )


class StockLocation(models.Model):
    """Stock location model"""

    _name = 'stock.location'
    _description = 'Stock Location'

    name = fields.Char(
        string='Location Name',
        required=True
    )

    location_id = fields.Many2one(
        'stock.location',
        string='Parent Location'
    )

    usage = fields.Selection([
        ('supplier', 'Supplier Location'),
        ('view', 'View'),
        ('internal', 'Internal Location'),
        ('customer', 'Customer Location'),
        ('inventory', 'Inventory Loss'),
        ('production', 'Production'),
        ('transit', 'Transit Location'),
    ], string='Location Type', default='internal')

    active = fields.Boolean(
        string='Active',
        default=True
    )


class DeliveryCarrier(models.Model):
    """Delivery carrier model"""

    _name = 'delivery.carrier'
    _description = 'Delivery Carrier'

    name = fields.Char(
        string='Carrier Name',
        required=True,
        translate=True
    )

    carrier_type = fields.Selection([
        ('fixed', 'Fixed Price'),
        ('base_on_rule', 'Based on Rules'),
    ], string='Carrier Type', default='fixed')

    fixed_price = fields.Float(
        string='Fixed Price',
        help='Fixed shipping price'
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )