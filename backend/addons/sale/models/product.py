# -*- coding: utf-8 -*-
"""
Product Management Model for MyTriv ERP

This module handles product catalog and inventory management.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    """Product model for MyTriv ERP"""

    _name = 'product.product'
    _description = 'Product'

    name = fields.Char(
        string='Product Name',
        required=True,
        translate=True,
        help='Name of the product'
    )

    # Product Code
    default_code = fields.Char(
        string='Internal Reference',
        help='Internal product reference'
    )

    barcode = fields.Char(
        string='Barcode',
        help='Product barcode'
    )

    # Product Type
    type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'),
        ('product', 'Storable Product'),
    ], string='Product Type', default='product', required=True)

    # Categories
    categ_id = fields.Many2one(
        'product.category',
        string='Product Category',
        help='Product category'
    )

    # Description
    description = fields.Text(
        string='Description',
        translate=True,
        help='Product description'
    )

    description_sale = fields.Text(
        string='Sales Description',
        translate=True,
        help='Description for sales'
    )

    # Pricing
    list_price = fields.Float(
        string='Sales Price',
        default=0.0,
        help='Sales price of the product'
    )

    standard_price = fields.Float(
        string='Cost Price',
        default=0.0,
        help='Cost price of the product'
    )

    # Unit of Measure
    uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        required=True,
        help='Default unit of measure'
    )

    uom_po_id = fields.Many2one(
        'uom.uom',
        string='Purchase Unit of Measure',
        help='Unit of measure for purchases'
    )

    # Inventory
    qty_available = fields.Float(
        string='Available Quantity',
        compute='_compute_qty_available',
        help='Available quantity in stock'
    )

    virtual_available = fields.Float(
        string='Forecasted Quantity',
        compute='_compute_qty_available',
        help='Forecasted quantity'
    )

    incoming_qty = fields.Float(
        string='Incoming Quantity',
        compute='_compute_qty_available',
        help='Incoming quantity'
    )

    outgoing_qty = fields.Float(
        string='Outgoing Quantity',
        compute='_compute_qty_available',
        help='Outgoing quantity'
    )

    # Weight and Volume
    weight = fields.Float(
        string='Weight',
        help='Product weight'
    )

    volume = fields.Float(
        string='Volume',
        help='Product volume'
    )

    # Dimensions
    length = fields.Float(
        string='Length',
        help='Product length'
    )

    width = fields.Float(
        string='Width',
        help='Product width'
    )

    height = fields.Float(
        string='Height',
        help='Product height'
    )

    # Status
    active = fields.Boolean(
        string='Active',
        default=True,
        help='If unchecked, product will be archived'
    )

    sale_ok = fields.Boolean(
        string='Can be Sold',
        default=True,
        help='If checked, product can be sold'
    )

    purchase_ok = fields.Boolean(
        string='Can be Purchased',
        default=True,
        help='If checked, product can be purchased'
    )

    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    @api.depends('stock_move_ids.state', 'stock_move_ids.product_qty')
    def _compute_qty_available(self):
        """Compute available quantities"""
        for product in self:
            # Simplified calculation - in real implementation would use stock moves
            product.qty_available = 100  # Placeholder
            product.virtual_available = 100  # Placeholder
            product.incoming_qty = 0  # Placeholder
            product.outgoing_qty = 0  # Placeholder

    @api.constrains('list_price', 'standard_price')
    def _check_prices(self):
        """Validate prices"""
        for product in self:
            if product.list_price < 0:
                raise ValidationError(_("Sales price cannot be negative"))
            if product.standard_price < 0:
                raise ValidationError(_("Cost price cannot be negative"))

    def action_view_stock_moves(self):
        """View stock moves for this product"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Stock Moves'),
            'res_model': 'stock.move',
            'view_mode': 'tree,form',
            'domain': [('product_id', '=', self.id)],
            'context': {'default_product_id': self.id}
        }

    def action_update_quantity_on_hand(self):
        """Update quantity on hand"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Update Quantity'),
            'res_model': 'stock.change.product.qty',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_product_id': self.id}
        }

    def toggle_active(self):
        """Toggle product active status"""
        for product in self:
            product.active = not product.active


class UomUom(models.Model):
    """Unit of measure model"""

    _name = 'uom.uom'
    _description = 'Unit of Measure'

    name = fields.Char(
        string='Unit of Measure',
        required=True,
        translate=True
    )

    category_id = fields.Many2one(
        'uom.category',
        string='Category',
        required=True
    )

    factor = fields.Float(
        string='Ratio',
        default=1.0,
        help='Ratio to base unit of measure'
    )

    uom_type = fields.Selection([
        ('bigger', 'Bigger than reference Unit of Measure'),
        ('reference', 'Reference Unit of Measure'),
        ('smaller', 'Smaller than reference Unit of Measure'),
    ], string='Type', default='reference', required=True)

    active = fields.Boolean(
        string='Active',
        default=True
    )


class UomCategory(models.Model):
    """Unit of measure category model"""

    _name = 'uom.category'
    _description = 'Unit of Measure Category'

    name = fields.Char(
        string='Category Name',
        required=True,
        translate=True
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )