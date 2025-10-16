# -*- coding: utf-8 -*-
"""
Product Category Management Model for MyTriv ERP

This module handles product categorization and organization.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class ProductCategory(models.Model):
    """Product category model for MyTriv ERP"""

    _name = 'product.category'
    _description = 'Product Category'
    _parent_name = 'parent_id'
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'parent_id, name'

    name = fields.Char(
        string='Category Name',
        required=True,
        translate=True,
        help='Name of the product category'
    )

    complete_name = fields.Char(
        string='Complete Name',
        compute='_compute_complete_name',
        store=True,
        help='Complete category name with parent hierarchy'
    )

    # Hierarchy
    parent_id = fields.Many2one(
        'product.category',
        string='Parent Category',
        index=True,
        ondelete='cascade',
        help='Parent category'
    )

    child_id = fields.One2many(
        'product.category',
        'parent_id',
        string='Child Categories',
        help='Child categories'
    )

    # Description
    description = fields.Text(
        string='Description',
        translate=True,
        help='Category description'
    )

    # Statistics
    product_count = fields.Integer(
        string='Product Count',
        compute='_compute_product_count',
        help='Number of products in this category'
    )

    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    @api.depends('name', 'parent_id')
    def _compute_complete_name(self):
        """Compute complete category name with hierarchy"""
        for category in self:
            if category.parent_id:
                category.complete_name = f"{category.parent_id.complete_name} / {category.name}"
            else:
                category.complete_name = category.name

    @api.depends('product_ids')
    def _compute_product_count(self):
        """Compute number of products in category"""
        for category in self:
            category.product_count = len(category.product_ids)

    @api.constrains('parent_id')
    def _check_parent_id(self):
        """Prevent recursive hierarchy"""
        if not self._check_recursion():
            raise ValidationError(_("You cannot create recursive categories"))

    def name_get(self):
        """Get category name with hierarchy"""
        result = []
        for category in self:
            name = category.complete_name
            result.append((category.id, name))
        return result

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """Search categories by name"""
        if args is None:
            args = []

        domain = args + ['|', ('name', operator, name), ('complete_name', operator, name)]
        return self.search(domain, limit=limit).name_get()

    def action_view_products(self):
        """View products in this category"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Category Products'),
            'res_model': 'product.product',
            'view_mode': 'tree,form',
            'domain': [('categ_id', '=', self.id)],
            'context': {'default_categ_id': self.id}
        }

    def toggle_active(self):
        """Toggle category active status"""
        for category in self:
            category.active = not category.active