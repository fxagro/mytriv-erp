# -*- coding: utf-8 -*-
"""
Reconciliation Helper Model

This module provides automated reconciliation functionality and
helpers for bank statement reconciliation.
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class ReconciliationHelper(models.Model):
    """Reconciliation Helper model for automated bank reconciliation."""

    _name = 'account.reconciliation.helper'
    _description = 'Bank Reconciliation Helper'
    _rec_name = 'statement_date'

    # Basic fields
    statement_date = fields.Date(
        string='Statement Date',
        required=True,
        help='Date of the bank statement'
    )

    statement_number = fields.Char(
        string='Statement Number',
        help='Bank statement reference number'
    )

    account_id = fields.Many2one(
        'account.account',
        string='Bank Account',
        required=True,
        domain=[('is_reconciliation_account', '=', True)],
        help='Bank account to reconcile'
    )

    starting_balance = fields.Monetary(
        string='Starting Balance',
        currency_field='company_currency',
        required=True,
        help='Account balance at start of statement period'
    )

    ending_balance = fields.Monetary(
        string='Ending Balance',
        currency_field='company_currency',
        required=True,
        help='Account balance at end of statement period'
    )

    # Reconciliation status
    status = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ], string='Status', default='draft', help='Reconciliation status')

    # Transaction counts
    total_transactions = fields.Integer(
        string='Total Transactions',
        default=0,
        help='Total number of transactions in statement'
    )

    matched_transactions = fields.Integer(
        string='Matched Transactions',
        default=0,
        help='Number of matched transactions'
    )

    unmatched_transactions = fields.Integer(
        string='Unmatched Transactions',
        default=0,
        help='Number of unmatched transactions'
    )

    # Amount totals
    total_debits = fields.Monetary(
        string='Total Debits',
        currency_field='company_currency',
        default=0.0,
        help='Total debit amount in statement'
    )

    total_credits = fields.Monetary(
        string='Total Credits',
        currency_field='company_currency',
        default=0.0,
        help='Total credit amount in statement'
    )

    # Reconciliation results
    reconciled_balance = fields.Monetary(
        string='Reconciled Balance',
        currency_field='company_currency',
        compute='_compute_reconciled_balance',
        store=True,
        help='Calculated reconciled balance'
    )

    difference = fields.Monetary(
        string='Difference',
        currency_field='company_currency',
        compute='_compute_difference',
        store=True,
        help='Difference between ending balance and reconciled balance'
    )

    # Notes and attachments
    notes = fields.Text(
        string='Reconciliation Notes',
        help='Notes about the reconciliation process'
    )

    attachment_ids = fields.Many2many(
        'ir.attachment',
        string='Attachments',
        help='Supporting documents for reconciliation'
    )

    @api.depends('starting_balance', 'total_debits', 'total_credits')
    def _compute_reconciled_balance(self):
        """Compute the reconciled balance."""
        for record in self:
            record.reconciled_balance = record.starting_balance + record.total_credits - record.total_debits

    @api.depends('ending_balance', 'reconciled_balance')
    def _compute_difference(self):
        """Compute the difference between balances."""
        for record in self:
            record.difference = record.ending_balance - record.reconciled_balance

    def action_start_reconciliation(self):
        """Start the reconciliation process."""
        self.write({'status': 'in_progress'})

    def action_complete_reconciliation(self):
        """Mark reconciliation as completed."""
        for record in self:
            if record.difference == 0:
                record.write({'status': 'completed'})
            else:
                raise ValidationError("Cannot complete reconciliation with outstanding differences.")

    def action_fail_reconciliation(self):
        """Mark reconciliation as failed."""
        self.write({'status': 'failed'})

    def action_import_statement(self, statement_data):
        """Import bank statement data."""
        self.ensure_one()

        if not statement_data:
            raise ValidationError("No statement data provided.")

        # Process statement data
        transactions = statement_data.get('transactions', [])
        self.total_transactions = len(transactions)

        # Calculate totals
        total_debits = 0.0
        total_credits = 0.0

        for transaction in transactions:
            if transaction.get('type') == 'debit':
                total_debits += transaction.get('amount', 0.0)
            else:
                total_credits += transaction.get('amount', 0.0)

        self.total_debits = total_debits
        self.total_credits = total_credits

        # Update status
        self.status = 'draft'

        return True

    def action_auto_match_transactions(self):
        """Automatically match transactions with accounting entries."""
        self.ensure_one()

        if self.status != 'in_progress':
            raise ValidationError("Reconciliation must be in progress to auto-match.")

        # Get unmatched bank transactions (this would typically come from imported data)
        # For now, we'll simulate the matching process

        # Find corresponding account move lines
        move_lines = self.env['account.move.line'].search([
            ('account_id', '=', self.account_id.id),
            ('date', '>=', self.statement_date),
            ('date', '<=', self.statement_date + timedelta(days=30)),
            ('reconciled', '=', False)
        ])

        matched_count = 0

        # Simple matching logic (in real implementation, this would be more sophisticated)
        for line in move_lines:
            # Try to match by amount and date proximity
            if abs(line.debit - self.total_debits) < 0.01 or abs(line.credit - self.total_credits) < 0.01:
                line.write({'reconciled': True})
                matched_count += 1

        self.matched_transactions = matched_count
        self.unmatched_transactions = self.total_transactions - matched_count

        return matched_count

    def action_manual_match(self, transaction_id, move_line_id):
        """Manually match a transaction with an accounting entry."""
        self.ensure_one()

        if self.status != 'in_progress':
            raise ValidationError("Reconciliation must be in progress to manually match.")

        # Get the move line
        move_line = self.env['account.move.line'].browse(move_line_id)

        if not move_line.exists():
            raise ValidationError("Account move line not found.")

        # Mark as reconciled
        move_line.write({'reconciled': True})

        # Update counters
        self.matched_transactions += 1
        self.unmatched_transactions -= 1

        return True

    def get_reconciliation_report(self):
        """Generate reconciliation report."""
        self.ensure_one()

        return {
            'statement_date': self.statement_date,
            'statement_number': self.statement_number,
            'account_name': self.account_id.name,
            'starting_balance': self.starting_balance,
            'ending_balance': self.ending_balance,
            'reconciled_balance': self.reconciled_balance,
            'difference': self.difference,
            'total_transactions': self.total_transactions,
            'matched_transactions': self.matched_transactions,
            'unmatched_transactions': self.unmatched_transactions,
            'status': self.status,
            'notes': self.notes
        }

    @api.model
    def get_reconciliation_summary(self, days=30):
        """Get reconciliation summary for the last N days."""
        start_date = datetime.now().date() - timedelta(days=days)

        reconciliations = self.search([
            ('statement_date', '>=', start_date)
        ])

        summary = {
            'total_reconciliations': len(reconciliations),
            'completed_reconciliations': len(reconciliations.filtered(lambda r: r.status == 'completed')),
            'failed_reconciliations': len(reconciliations.filtered(lambda r: r.status == 'failed')),
            'total_difference': sum(reconciliations.mapped('difference')),
            'accounts_reconciled': len(reconciliations.mapped('account_id'))
        }

        return summary

    def action_create_adjustment_entry(self, adjustment_amount, description):
        """Create adjustment entry for reconciliation differences."""
        self.ensure_one()

        if abs(self.difference) < 0.01:
            raise ValidationError("No difference to adjust.")

        # Create adjustment move
        adjustment_move = self.env['account.move'].create({
            'date': self.statement_date,
            'ref': f'Reconciliation Adjustment - {self.statement_number}',
            'journal_id': self.account_id.company_id.bank_journal_id.id,
            'line_ids': [
                (0, 0, {
                    'account_id': self.account_id.id,
                    'name': description,
                    'debit': adjustment_amount if adjustment_amount > 0 else 0.0,
                    'credit': abs(adjustment_amount) if adjustment_amount < 0 else 0.0,
                }),
                (0, 0, {
                    'account_id': self.account_id.company_id.expense_reconciliation_account_id.id,
                    'name': description,
                    'debit': abs(adjustment_amount) if adjustment_amount < 0 else 0.0,
                    'credit': adjustment_amount if adjustment_amount > 0 else 0.0,
                })
            ]
        })

        # Update reconciliation
        self.write({
            'difference': 0.0,
            'notes': (self.notes or '') + f'\nAdjustment entry created: {adjustment_move.name}'
        })

        return adjustment_move