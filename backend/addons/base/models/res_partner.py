# -*- coding: utf-8 -*-
"""
Partner Management Model for MyTriv ERP

This module handles partners including customers, suppliers, and contacts.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    """Partner model for MyTriv ERP"""

    _name = 'res.partner'
    _description = 'Contact'
    _inherits = {'res.company': 'company_id'}

    # Basic information
    name = fields.Char(
        string='Name',
        required=True,
        index=True,
        help='Name of the partner'
    )

    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True,
        index=True
    )

    # Contact information
    email = fields.Char(
        string='Email',
        help='Email address of the partner'
    )

    phone = fields.Char(
        string='Phone',
        help='Phone number of the partner'
    )

    mobile = fields.Char(
        string='Mobile',
        help='Mobile number of the partner'
    )

    website = fields.Char(
        string='Website',
        help='Website of the partner'
    )

    # Address information
    street = fields.Char(
        string='Street',
        help='Street address'
    )

    street2 = fields.Char(
        string='Street 2',
        help='Additional street address'
    )

    city = fields.Char(
        string='City',
        help='City of the partner'
    )

    state_id = fields.Many2one(
        'res.country.state',
        string='State',
        domain="[('country_id', '=', country_id)]",
        help='State or province'
    )

    zip = fields.Char(
        string='ZIP',
        help='ZIP or postal code'
    )

    country_id = fields.Many2one(
        'res.country',
        string='Country',
        help='Country of the partner'
    )

    # Partner type
    is_company = fields.Boolean(
        string='Is a Company',
        default=False,
        help='Check if the partner is a company'
    )

    type = fields.Selection([
        ('contact', 'Contact'),
        ('invoice', 'Invoice Address'),
        ('delivery', 'Shipping Address'),
        ('other', 'Other Address'),
    ], string='Address Type', default='contact')

    # Business information
    vat = fields.Char(
        string='VAT',
        help='VAT number of the partner'
    )

    company_registry = fields.Char(
        string='Company Registry',
        help='Company registration number'
    )

    # Banking information
    bank_ids = fields.One2many(
        'res.partner.bank',
        'partner_id',
        string='Banks'
    )

    # Categories and tags
    category_id = fields.Many2many(
        'res.partner.category',
        'res_partner_category_rel',
        'partner_id',
        'category_id',
        string='Tags'
    )

    # Status
    active = fields.Boolean(
        string='Active',
        default=True,
        help='If unchecked, this partner will be archived'
    )

    customer_rank = fields.Integer(
        string='Customer Rank',
        default=0,
        help='Customer level (0 = no customer, 1 = customer)'
    )

    supplier_rank = fields.Integer(
        string='Supplier Rank',
        default=0,
        help='Supplier level (0 = no supplier, 1 = supplier)'
    )

    # Company relation
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    # User relation
    user_ids = fields.One2many(
        'res.users',
        'partner_id',
        string='Users'
    )

    # Financial information
    credit_limit = fields.Float(
        string='Credit Limit',
        help='Credit limit for this partner'
    )

    payment_terms_id = fields.Many2one(
        'account.payment.term',
        string='Payment Terms',
        help='Default payment terms for this partner'
    )

    # Statistics
    sale_order_count = fields.Integer(
        string='Sale Order Count',
        compute='_compute_sale_order_count'
    )

    purchase_order_count = fields.Integer(
        string='Purchase Order Count',
        compute='_compute_purchase_order_count'
    )

    invoice_count = fields.Integer(
        string='Invoice Count',
        compute='_compute_invoice_count'
    )

    @api.depends('name', 'is_company')
    def _compute_display_name(self):
        """Compute display name based on partner type"""
        for partner in self:
            if partner.is_company:
                partner.display_name = partner.name
            else:
                # For individuals, could include parent company name
                partner.display_name = partner.name

    @api.model
    def create(self, vals):
        """Create partner with proper defaults"""
        if 'is_company' not in vals:
            vals['is_company'] = False

        if 'type' not in vals:
            vals['type'] = 'contact'

        return super(ResPartner, self).create(vals)

    @api.constrains('email')
    def _check_email(self):
        """Validate email format"""
        for partner in self:
            if partner.email:
                # Basic email validation
                if '@' not in partner.email or '.' not in partner.email:
                    raise ValidationError(_("Invalid email format"))

    def _compute_sale_order_count(self):
        """Compute number of sale orders for this partner"""
        for partner in self:
            partner.sale_order_count = self.env['sale.order'].search_count([
                ('partner_id', '=', partner.id)
            ])

    def _compute_purchase_order_count(self):
        """Compute number of purchase orders for this partner"""
        for partner in self:
            partner.purchase_order_count = self.env['purchase.order'].search_count([
                ('partner_id', '=', partner.id)
            ])

    def _compute_invoice_count(self):
        """Compute number of invoices for this partner"""
        for partner in self:
            partner.invoice_count = self.env['account.move'].search_count([
                ('partner_id', '=', partner.id)
            ])

    def action_view_sale_orders(self):
        """View sale orders for this partner"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sale Orders'),
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id}
        }

    def action_view_purchase_orders(self):
        """View purchase orders for this partner"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Purchase Orders'),
            'res_model': 'purchase.order',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id}
        }

    def action_view_invoices(self):
        """View invoices for this partner"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Invoices'),
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id}
        }

    def toggle_active(self):
        """Toggle active status"""
        for partner in self:
            partner.active = not partner.active

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """Search partners by name"""
        if args is None:
            args = []

        domain = args + ['|', ('name', operator, name), ('email', operator, name)]
        return self.search(domain, limit=limit).name_get()

    def name_get(self):
        """Get name for display"""
        result = []
        for partner in self:
            name = partner.name
            if partner.is_company:
                name = f"[Company] {name}"
            result.append((partner.id, name))
        return result