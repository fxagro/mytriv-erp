# -*- coding: utf-8 -*-
"""
Invoice Management Model for MyTriv ERP

This module handles invoice creation and management.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    """Invoice model for MyTriv ERP"""

    _name = 'account.move'
    _description = 'Invoice'

    name = fields.Char(
        string='Invoice Reference',
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
        help='Customer for this invoice'
    )

    # Invoice Details
    invoice_date = fields.Date(
        string='Invoice Date',
        required=True,
        default=lambda self: datetime.now().date(),
        help='Date when invoice was created'
    )

    invoice_date_due = fields.Date(
        string='Due Date',
        required=True,
        help='Date when invoice is due'
    )

    # Invoice Lines
    invoice_line_ids = fields.One2many(
        'account.move.line',
        'move_id',
        string='Invoice Lines',
        help='Products and services in this invoice'
    )

    # Amounts
    amount_untaxed = fields.Float(
        string='Untaxed Amount',
        compute='_compute_amount',
        store=True,
        help='Total amount before taxes'
    )

    amount_tax = fields.Float(
        string='Tax Amount',
        compute='_compute_amount',
        store=True,
        help='Total tax amount'
    )

    amount_total = fields.Float(
        string='Total Amount',
        compute='_compute_amount',
        store=True,
        help='Total amount including taxes'
    )

    # Payment
    payment_state = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('reversed', 'Reversed'),
        ('invoicing_legacy', 'Invoicing App Legacy'),
    ], string='Payment Status', default='not_paid')

    payment_date = fields.Date(
        string='Payment Date',
        help='Date when invoice was paid'
    )

    # Invoice Type
    move_type = fields.Selection([
        ('out_invoice', 'Customer Invoice'),
        ('in_invoice', 'Vendor Bill'),
        ('out_refund', 'Customer Credit Note'),
        ('in_refund', 'Vendor Credit Note'),
    ], string='Type', required=True, default='out_invoice')

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', track_visibility='onchange')

    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    @api.depends('invoice_line_ids.price_subtotal', 'invoice_line_ids.price_tax')
    def _compute_amount(self):
        """Compute invoice totals"""
        for invoice in self:
            amount_untaxed = sum(line.price_subtotal for line in invoice.invoice_line_ids)
            amount_tax = sum(line.price_tax for line in invoice.invoice_line_ids)

            invoice.amount_untaxed = amount_untaxed
            invoice.amount_tax = amount_tax
            invoice.amount_total = amount_untaxed + amount_tax

    def action_post(self):
        """Post invoice"""
        self.write({'state': 'posted'})

    def action_cancel(self):
        """Cancel invoice"""
        self.write({'state': 'cancel'})

    def action_register_payment(self):
        """Register payment for invoice"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Register Payment'),
            'res_model': 'account.payment',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_invoice_id': self.id}
        }

    def action_view_payments(self):
        """View payments for this invoice"""
        self.ensure_one()
        payments = self.env['account.payment'].search([
            ('invoice_ids', 'in', self.id)
        ])

        if payments:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Payments'),
                'res_model': 'account.payment',
                'view_mode': 'tree,form',
                'domain': [('invoice_ids', 'in', self.id)],
            }
        return False


class AccountMoveLine(models.Model):
    """Invoice line model"""

    _name = 'account.move.line'
    _description = 'Invoice Line'

    move_id = fields.Many2one(
        'account.move',
        string='Invoice',
        required=True,
        ondelete='cascade'
    )

    # Product Information
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        help='Product being invoiced'
    )

    name = fields.Char(
        string='Description',
        required=True,
        help='Description of the line item'
    )

    quantity = fields.Float(
        string='Quantity',
        required=True,
        default=1,
        help='Quantity of product'
    )

    price_unit = fields.Float(
        string='Unit Price',
        required=True,
        help='Price per unit'
    )

    # Amounts
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

    # Tax Information
    tax_ids = fields.Many2many(
        'account.tax',
        string='Taxes',
        help='Taxes applied to this line'
    )

    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='move_id.company_id',
        store=True
    )

    @api.depends('quantity', 'price_unit', 'tax_ids')
    def _compute_amount(self):
        """Compute line amounts"""
        for line in self:
            price_subtotal = line.quantity * line.price_unit

            # Calculate tax
            tax_amount = 0.0
            if line.tax_ids:
                tax_amount = price_subtotal * (line.tax_ids[0].amount / 100)  # Simplified

            line.price_subtotal = price_subtotal
            line.price_tax = tax_amount
            line.price_total = price_subtotal + tax_amount


class AccountPayment(models.Model):
    """Payment model"""

    _name = 'account.payment'
    _description = 'Payment'

    name = fields.Char(
        string='Payment Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )

    # Related Records
    invoice_ids = fields.Many2many(
        'account.move',
        string='Invoices',
        help='Invoices being paid'
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        help='Customer making the payment'
    )

    # Payment Details
    amount = fields.Float(
        string='Amount',
        required=True,
        help='Payment amount'
    )

    payment_date = fields.Date(
        string='Payment Date',
        required=True,
        default=lambda self: datetime.now().date(),
        help='Date when payment was made'
    )

    # Payment Method
    payment_method_id = fields.Many2one(
        'account.payment.method',
        string='Payment Method',
        required=True,
        help='Method of payment'
    )

    journal_id = fields.Many2one(
        'account.journal',
        string='Payment Journal',
        required=True,
        help='Journal for recording payment'
    )

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('sent', 'Sent'),
        ('reconciled', 'Reconciled'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft')

    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    def action_post(self):
        """Post payment"""
        self.write({'state': 'posted'})

    def action_cancel(self):
        """Cancel payment"""
        self.write({'state': 'cancelled'})


class AccountPaymentTerm(models.Model):
    """Payment terms model"""

    _name = 'account.payment.term'
    _description = 'Payment Terms'

    name = fields.Char(
        string='Payment Terms',
        required=True,
        translate=True
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )


class AccountTax(models.Model):
    """Tax model"""

    _name = 'account.tax'
    _description = 'Tax'

    name = fields.Char(
        string='Tax Name',
        required=True,
        translate=True
    )

    amount = fields.Float(
        string='Amount',
        required=True,
        help='Tax percentage'
    )

    type_tax_use = fields.Selection([
        ('sale', 'Sales'),
        ('purchase', 'Purchases'),
        ('none', 'None'),
    ], string='Tax Scope', default='sale')

    active = fields.Boolean(
        string='Active',
        default=True
    )


class AccountJournal(models.Model):
    """Journal model"""

    _name = 'account.journal'
    _description = 'Journal'

    name = fields.Char(
        string='Journal Name',
        required=True,
        translate=True
    )

    code = fields.Char(
        string='Code',
        required=True,
        help='Journal code'
    )

    type = fields.Selection([
        ('sale', 'Sales'),
        ('purchase', 'Purchase'),
        ('cash', 'Cash'),
        ('bank', 'Bank'),
        ('general', 'Miscellaneous'),
    ], string='Type', default='general')

    active = fields.Boolean(
        string='Active',
        default=True
    )