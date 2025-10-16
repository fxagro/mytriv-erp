# -*- coding: utf-8 -*-
"""
Custom Journal Entry Model

This module extends journal entry functionality with automation
and enhanced tracking capabilities.
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class JournalEntryCustom(models.Model):
    """Extended Journal Entry model with custom fields and automation."""

    _name = 'account.move.custom'
    _description = 'Custom Journal Entry Extensions'
    _inherit = ['account.move']

    # Additional custom fields for enhanced journal management
    entry_type = fields.Selection([
        ('manual', 'Manual Entry'),
        ('automated', 'Automated Entry'),
        ('recurring', 'Recurring Entry'),
        ('adjustment', 'Adjustment Entry'),
        ('reversal', 'Reversal Entry')
    ], string='Entry Type', default='manual', help='Type classification for the journal entry')

    is_recurring = fields.Boolean(
        string='Is Recurring',
        default=False,
        help='Whether this is a recurring journal entry'
    )

    recurring_period = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly')
    ], string='Recurring Period', help='Frequency of recurring entries')

    next_recurring_date = fields.Date(
        string='Next Recurring Date',
        help='Next date for recurring entry generation'
    )

    auto_reversal = fields.Boolean(
        string='Auto Reversal',
        default=False,
        help='Whether this entry should be automatically reversed'
    )

    reversal_date = fields.Date(
        string='Reversal Date',
        help='Date when this entry should be reversed'
    )

    approval_status = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Approval Status', default='draft', help='Approval status of the journal entry')

    approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
        help='User who approved this journal entry'
    )

    approval_date = fields.Datetime(
        string='Approval Date',
        help='Date and time when entry was approved'
    )

    reference_document = fields.Char(
        string='Reference Document',
        help='Reference to external document or transaction'
    )

    notes = fields.Text(
        string='Notes',
        help='Additional notes or comments about this entry'
    )

    # Computed fields for analytics
    total_debit = fields.Monetary(
        string='Total Debit',
        currency_field='company_currency',
        compute='_compute_totals',
        store=True,
        help='Total debit amount of the entry'
    )

    total_credit = fields.Monetary(
        string='Total Credit',
        currency_field='company_currency',
        compute='_compute_totals',
        store=True,
        help='Total credit amount of the entry'
    )

    is_balanced = fields.Boolean(
        string='Is Balanced',
        compute='_compute_is_balanced',
        store=True,
        help='Whether debit equals credit in this entry'
    )

    @api.depends('line_ids.debit', 'line_ids.credit')
    def _compute_totals(self):
        """Compute total debit and credit amounts."""
        for move in self:
            move.total_debit = sum(line.debit for line in move.line_ids)
            move.total_credit = sum(line.credit for line in move.line_ids)

    @api.depends('total_debit', 'total_credit')
    def _compute_is_balanced(self):
        """Check if the entry is balanced (debit = credit)."""
        for move in self:
            # Allow for small rounding differences
            tolerance = 0.01
            move.is_balanced = abs(move.total_debit - move.total_credit) <= tolerance

    @api.constrains('is_balanced')
    def _check_balance(self):
        """Ensure journal entry is balanced before posting."""
        for move in self:
            if move.state == 'posted' and not move.is_balanced:
                raise ValidationError("Journal entry must be balanced (debit must equal credit) before posting.")

    def action_approve_entry(self):
        """Approve the journal entry."""
        for move in self:
            if move.approval_status == 'pending':
                move.write({
                    'approval_status': 'approved',
                    'approved_by': self.env.user.id,
                    'approval_date': datetime.now()
                })

    def action_reject_entry(self):
        """Reject the journal entry."""
        for move in self:
            if move.approval_status in ['pending', 'approved']:
                move.write({
                    'approval_status': 'rejected',
                    'approved_by': self.env.user.id,
                    'approval_date': datetime.now()
                })

    def action_submit_for_approval(self):
        """Submit entry for approval."""
        for move in self:
            if move.approval_status == 'draft':
                move.write({'approval_status': 'pending'})

    def action_create_recurring_entries(self):
        """Create recurring entries based on this template."""
        for move in self:
            if move.is_recurring and move.next_recurring_date:
                if move.next_recurring_date <= fields.Date.today():
                    self._create_next_recurring_entry()

    def _create_next_recurring_entry(self):
        """Create the next recurring entry."""
        self.ensure_one()

        # Calculate next recurring date
        next_date = self._calculate_next_recurring_date()

        if next_date:
            # Create new move by copying current one
            new_move_data = {
                'date': next_date,
                'ref': f"{self.ref} - {next_date}" if self.ref else f"Recurring - {next_date}",
                'entry_type': 'recurring',
                'is_recurring': False,  # Don't make the copy recurring
                'next_recurring_date': None,
            }

            # Copy move lines with updated date
            new_lines = []
            for line in self.line_ids:
                new_line_data = {
                    'account_id': line.account_id.id,
                    'name': line.name,
                    'debit': line.debit,
                    'credit': line.credit,
                    'date_maturity': next_date if line.date_maturity else None,
                }
                new_lines.append((0, 0, new_line_data))

            new_move_data['line_ids'] = new_lines

            # Create the new move
            new_move = self.create(new_move_data)

            # Update next recurring date on original
            self.write({'next_recurring_date': next_date})

            return new_move

        return False

    def _calculate_next_recurring_date(self):
        """Calculate the next recurring date based on period."""
        self.ensure_one()

        if not self.next_recurring_date:
            return False

        current_date = self.next_recurring_date

        if self.recurring_period == 'daily':
            return current_date + timedelta(days=1)
        elif self.recurring_period == 'weekly':
            return current_date + timedelta(weeks=1)
        elif self.recurring_period == 'monthly':
            # Add one month
            if current_date.month == 12:
                return current_date.replace(year=current_date.year + 1, month=1)
            else:
                return current_date.replace(month=current_date.month + 1)
        elif self.recurring_period == 'quarterly':
            # Add three months
            new_month = current_date.month + 3
            new_year = current_date.year
            if new_month > 12:
                new_year += new_month // 12
                new_month = new_month % 12

            return current_date.replace(year=new_year, month=new_month)
        elif self.recurring_period == 'yearly':
            return current_date.replace(year=current_date.year + 1)

        return False

    def action_reverse_entry(self):
        """Create a reversal entry."""
        self.ensure_one()

        if not self.auto_reversal or not self.reversal_date:
            return False

        if self.reversal_date <= fields.Date.today():
            # Create reversal move
            reversal_data = {
                'date': self.reversal_date,
                'ref': f"Reversal of {self.name}",
                'entry_type': 'reversal',
                'journal_id': self.journal_id.id,
            }

            # Create reversal lines (swap debits and credits)
            reversal_lines = []
            for line in self.line_ids:
                reversal_line_data = {
                    'account_id': line.account_id.id,
                    'name': f"Reversal: {line.name}",
                    'debit': line.credit,  # Swap debit and credit
                    'credit': line.debit,
                    'date_maturity': self.reversal_date,
                }
                reversal_lines.append((0, 0, reversal_line_data))

            reversal_data['line_ids'] = reversal_lines

            reversal_move = self.create(reversal_data)

            # Mark original as reversed
            self.write({
                'auto_reversal': False,
                'reversal_date': None
            })

            return reversal_move

        return False

    @api.model
    def get_pending_approvals(self):
        """Get journal entries pending approval."""
        return self.search([('approval_status', '=', 'pending')])

    @api.model
    def get_recurring_entries_due(self):
        """Get recurring entries that are due."""
        return self.search([
            ('is_recurring', '=', True),
            ('next_recurring_date', '<=', fields.Date.today())
        ])

    @api.model
    def process_recurring_entries(self):
        """Process all recurring entries that are due."""
        due_entries = self.get_recurring_entries_due()

        created_moves = []
        for entry in due_entries:
            new_move = entry._create_next_recurring_entry()
            if new_move:
                created_moves.append(new_move)

        return created_moves