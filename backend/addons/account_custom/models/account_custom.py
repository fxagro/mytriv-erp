# -*- coding: utf-8 -*-
"""
Custom Account Model

This module extends the base account functionality with additional fields
and methods for enhanced chart of accounts management.
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountCustom(models.Model):
    """Extended Account model with custom fields and functionality."""

    _name = 'account.account.custom'
    _description = 'Custom Account Extensions'
    _inherit = ['account.account']

    # Additional custom fields for enhanced account management
    account_category = fields.Selection([
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('equity', 'Equity'),
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('other', 'Other')
    ], string='Account Category', help='Category classification for the account')

    account_subcategory = fields.Char(
        string='Account Subcategory',
        help='Detailed subcategory for better organization'
    )

    is_budgeted = fields.Boolean(
        string='Is Budgeted',
        default=False,
        help='Whether this account is included in budgeting'
    )

    budget_amount = fields.Monetary(
        string='Budget Amount',
        currency_field='company_currency',
        help='Budgeted amount for this account'
    )

    is_reconciliation_account = fields.Boolean(
        string='Reconciliation Account',
        default=False,
        help='Whether this account is used for bank reconciliation'
    )

    last_reconciliation_date = fields.Date(
        string='Last Reconciliation Date',
        help='Date of last reconciliation for this account'
    )

    account_manager = fields.Many2one(
        'res.users',
        string='Account Manager',
        help='User responsible for managing this account'
    )

    notes = fields.Text(
        string='Notes',
        help='Additional notes or comments about this account'
    )

    # Computed fields for analytics
    current_balance = fields.Monetary(
        string='Current Balance',
        currency_field='company_currency',
        compute='_compute_current_balance',
        store=True,
        help='Current balance of the account'
    )

    ytd_debit = fields.Monetary(
        string='YTD Debit',
        currency_field='company_currency',
        compute='_compute_ytd_amounts',
        store=True,
        help='Year-to-date debit total'
    )

    ytd_credit = fields.Monetary(
        string='YTD Credit',
        currency_field='company_currency',
        compute='_compute_ytd_amounts',
        store=True,
        help='Year-to-date credit total'
    )

    @api.depends('code', 'company_id')
    def _compute_current_balance(self):
        """Compute current balance for the account."""
        for account in self:
            if account.company_id:
                # Get account move lines for current year
                current_year = fields.Date.today().year
                move_lines = self.env['account.move.line'].search([
                    ('account_id', '=', account.id),
                    ('date', '>=', f'{current_year}-01-01'),
                    ('date', '<=', fields.Date.today()),
                    ('move_id.state', '=', 'posted')
                ])

                debit = sum(move_lines.mapped('debit'))
                credit = sum(move_lines.mapped('credit'))

                if account.account_type in ['asset', 'expense']:
                    account.current_balance = debit - credit
                else:
                    account.current_balance = credit - debit
            else:
                account.current_balance = 0.0

    @api.depends('code', 'company_id')
    def _compute_ytd_amounts(self):
        """Compute year-to-date debit and credit amounts."""
        for account in self:
            if account.company_id:
                current_year = fields.Date.today().year
                move_lines = self.env['account.move.line'].search([
                    ('account_id', '=', account.id),
                    ('date', '>=', f'{current_year}-01-01'),
                    ('date', '<=', fields.Date.today()),
                    ('move_id.state', '=', 'posted')
                ])

                account.ytd_debit = sum(move_lines.mapped('debit'))
                account.ytd_credit = sum(move_lines.mapped('credit'))
            else:
                account.ytd_debit = 0.0
                account.ytd_credit = 0.0

    @api.constrains('code', 'company_id')
    def _check_account_code_uniqueness(self):
        """Ensure account codes are unique within a company."""
        for account in self:
            if account.code and account.company_id:
                existing = self.search([
                    ('code', '=', account.code),
                    ('company_id', '=', account.company_id.id),
                    ('id', '!=', account.id)
                ])
                if existing:
                    raise ValidationError(f"Account code '{account.code}' already exists in company '{account.company_id.name}'")

    def action_view_account_moves(self):
        """Open account move lines for this account."""
        self.ensure_one()
        return {
            'name': f'Account Moves: {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move.line',
            'view_mode': 'tree,form',
            'domain': [('account_id', '=', self.id)],
            'context': {'default_account_id': self.id}
        }

    def action_reconcile_account(self):
        """Mark account for reconciliation."""
        self.ensure_one()
        self.write({
            'is_reconciliation_account': True,
            'last_reconciliation_date': fields.Date.today()
        })

    def get_account_summary(self):
        """Get comprehensive account summary."""
        self.ensure_one()
        return {
            'account_name': self.name,
            'account_code': self.code,
            'account_type': self.account_type,
            'account_category': self.account_category,
            'current_balance': self.current_balance,
            'ytd_debit': self.ytd_debit,
            'ytd_credit': self.ytd_credit,
            'is_budgeted': self.is_budgeted,
            'budget_amount': self.budget_amount,
            'is_reconciliation_account': self.is_reconciliation_account,
            'last_reconciliation_date': self.last_reconciliation_date
        }

    @api.model
    def get_accounts_by_category(self, category):
        """Get all accounts in a specific category."""
        return self.search([('account_category', '=', category)])

    @api.model
    def get_reconciliation_accounts(self):
        """Get all accounts marked for reconciliation."""
        return self.search([('is_reconciliation_account', '=', True)])

    @api.model
    def get_budgeted_accounts(self):
        """Get all accounts included in budgeting."""
        return self.search([('is_budgeted', '=', True)])

    def action_update_budget(self, budget_amount):
        """Update budget amount for the account."""
        self.ensure_one()
        self.write({
            'is_budgeted': True,
            'budget_amount': budget_amount
        })

    def action_remove_budget(self):
        """Remove account from budgeting."""
        self.write({
            'is_budgeted': False,
            'budget_amount': 0.0
        })