# -*- coding: utf-8 -*-
"""
Company Management Model for MyTriv ERP

This module handles company configuration and multi-company setup.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    """Company model for MyTriv ERP"""

    _name = 'res.company'
    _description = 'Companies'

    # Basic information
    name = fields.Char(
        string='Company Name',
        required=True,
        translate=True,
        help='Name of the company'
    )

    # Contact information
    email = fields.Char(
        string='Email',
        help='Company email address'
    )

    phone = fields.Char(
        string='Phone',
        help='Company phone number'
    )

    website = fields.Char(
        string='Website',
        help='Company website'
    )

    # Address information
    street = fields.Char(
        string='Street',
        help='Company street address'
    )

    street2 = fields.Char(
        string='Street 2',
        help='Additional street address'
    )

    city = fields.Char(
        string='City',
        help='Company city'
    )

    state_id = fields.Many2one(
        'res.country.state',
        string='State',
        domain="[('country_id', '=', country_id)]",
        help='Company state or province'
    )

    zip = fields.Char(
        string='ZIP',
        help='Company ZIP or postal code'
    )

    country_id = fields.Many2one(
        'res.country',
        string='Country',
        help='Company country'
    )

    # Business information
    vat = fields.Char(
        string='VAT',
        help='Company VAT number'
    )

    company_registry = fields.Char(
        string='Company Registry',
        help='Company registration number'
    )

    # Logo and branding
    logo = fields.Binary(
        string='Company Logo',
        help='Company logo for reports and branding'
    )

    # Currency and language
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.ref('base.IDR', raise_if_not_found=False) or
                           self.env.ref('base.USD', raise_if_not_found=False) or
                           self.env['res.currency'].search([('active', '=', True)], limit=1)
    )

    # Financial settings
    fiscalyear_last_day = fields.Integer(
        string='Fiscal Year Last Day',
        default=31,
        help='Last day of the fiscal year (1-31)'
    )

    fiscalyear_last_month = fields.Selection([
        (1, 'January'),
        (2, 'February'),
        (3, 'March'),
        (4, 'April'),
        (5, 'May'),
        (6, 'June'),
        (7, 'July'),
        (8, 'August'),
        (9, 'September'),
        (10, 'October'),
        (11, 'November'),
        (12, 'December'),
    ], string='Fiscal Year Last Month', default=12)

    # Chart of accounts
    chart_template_id = fields.Many2one(
        'account.chart.template',
        string='Chart Template',
        help='Chart of accounts template for this company'
    )

    # Bank accounts
    bank_ids = fields.One2many(
        'res.partner.bank',
        'company_id',
        string='Company Bank Accounts'
    )

    # Users in this company
    user_ids = fields.Many2many(
        'res.users',
        'res_company_users_rel',
        'cid',
        'user_id',
        string='Accepted Users'
    )

    # Status
    active = fields.Boolean(
        string='Active',
        default=True,
        help='If unchecked, this company will be archived'
    )

    @api.model
    def create(self, vals):
        """Create company with proper defaults"""
        # Set default currency if not provided
        if 'currency_id' not in vals:
            vals['currency_id'] = self.env.ref('base.IDR', raise_if_not_found=False) or \
                                self.env.ref('base.USD', raise_if_not_found=False) or \
                                self.env['res.currency'].search([('active', '=', True)], limit=1).id

        return super(ResCompany, self).create(vals)

    @api.constrains('name')
    def _check_company_name(self):
        """Ensure company name is unique"""
        for company in self:
            if self.search_count([('name', '=', company.name), ('id', '!=', company.id)]) > 0:
                raise ValidationError(_("Company name must be unique"))

    def action_company_setup(self):
        """Open company setup wizard"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Company Setup'),
            'res_model': 'res.company.setup',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_company_id': self.id}
        }

    def action_view_users(self):
        """View users in this company"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Company Users'),
            'res_model': 'res.users',
            'view_mode': 'tree,form',
            'domain': [('company_ids', 'in', self.id)],
            'context': {'default_company_id': self.id}
        }

    def toggle_active(self):
        """Toggle company active status"""
        for company in self:
            company.active = not company.active

    @api.model
    def _get_main_company(self):
        """Get the main company"""
        return self.env.ref('base.main_company', raise_if_not_found=False) or self.search([('active', '=', True)], limit=1)


class ResCountry(models.Model):
    """Country model for MyTriv ERP"""

    _name = 'res.country'
    _description = 'Countries'

    name = fields.Char(
        string='Country Name',
        required=True,
        translate=True
    )

    code = fields.Char(
        string='Country Code',
        size=2,
        required=True,
        help='ISO 3166-1 alpha-2 country code'
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )


class ResCountryState(models.Model):
    """State/Province model for MyTriv ERP"""

    _name = 'res.country.state'
    _description = 'States/Provinces'

    name = fields.Char(
        string='State Name',
        required=True,
        translate=True
    )

    code = fields.Char(
        string='State Code',
        size=3,
        required=True,
        help='ISO 3166-2 state code'
    )

    country_id = fields.Many2one(
        'res.country',
        string='Country',
        required=True
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )


class ResCurrency(models.Model):
    """Currency model for MyTriv ERP"""

    _name = 'res.currency'
    _description = 'Currencies'

    name = fields.Char(
        string='Currency',
        required=True,
        translate=True
    )

    symbol = fields.Char(
        string='Symbol',
        required=True,
        help='Currency symbol (e.g. $)'
    )

    code = fields.Char(
        string='Code',
        size=3,
        required=True,
        help='ISO 4217 currency code'
    )

    rate = fields.Float(
        string='Rate',
        default=1.0,
        help='Exchange rate to base currency'
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    position = fields.Selection([
        ('before', 'Before Amount'),
        ('after', 'After Amount'),
    ], string='Symbol Position', default='before')