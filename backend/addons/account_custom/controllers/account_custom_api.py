# -*- coding: utf-8 -*-
"""
Account Custom API Controller

This module provides REST API endpoints for account custom functionality,
extending the base REST API with accounting-specific operations.
"""

import json
from odoo import http
from odoo.http import request
from datetime import datetime


class AccountCustomAPI(http.Controller):
    """REST API controller for account custom operations."""

    @http.route('/api/v1/account/accounts', type='json', auth='user', methods=['GET'], csrf=False)
    def get_accounts(self, **kwargs):
        """Get accounts with optional filtering."""
        try:
            # Get query parameters
            account_type = kwargs.get('account_type')
            category = kwargs.get('category')
            is_budgeted = kwargs.get('is_budgeted')
            is_reconciliation = kwargs.get('is_reconciliation')
            limit = int(kwargs.get('limit', 100))
            offset = int(kwargs.get('offset', 0))

            # Build domain for filtering
            domain = []
            if account_type:
                domain.append(('account_type', '=', account_type))
            if category:
                domain.append(('account_category', '=', category))
            if is_budgeted == 'true':
                domain.append(('is_budgeted', '=', True))
            if is_reconciliation == 'true':
                domain.append(('is_reconciliation_account', '=', True))

            # Search accounts
            accounts = request.env['account.account'].sudo().search(
                domain,
                limit=limit,
                offset=offset
            )

            # Format response data
            data = []
            for account in accounts:
                account_data = {
                    'id': account.id,
                    'code': account.code,
                    'name': account.name,
                    'account_type': account.account_type,
                    'account_category': account.account_category,
                    'account_subcategory': account.account_subcategory,
                    'is_budgeted': account.is_budgeted,
                    'budget_amount': account.budget_amount,
                    'is_reconciliation_account': account.is_reconciliation_account,
                    'current_balance': account.current_balance,
                    'ytd_debit': account.ytd_debit,
                    'ytd_credit': account.ytd_credit,
                    'company_id': account.company_id.id if account.company_id else None,
                    'company_name': account.company_id.name if account.company_id else None
                }
                data.append(account_data)

            return {
                'accounts': data,
                'count': len(data),
                'total': len(request.env['account.account'].sudo().search(domain))
            }

        except Exception as e:
            return {'error': str(e)}

    @http.route('/api/v1/account/accounts/<int:account_id>', type='json', auth='user', methods=['GET'], csrf=False)
    def get_account(self, account_id):
        """Get a specific account by ID."""
        try:
            account = request.env['account.account'].sudo().browse(account_id)

            if not account.exists():
                return {'error': 'Account not found'}

            account_data = {
                'id': account.id,
                'code': account.code,
                'name': account.name,
                'account_type': account.account_type,
                'account_category': account.account_category,
                'account_subcategory': account.account_subcategory,
                'is_budgeted': account.is_budgeted,
                'budget_amount': account.budget_amount,
                'is_reconciliation_account': account.is_reconciliation_account,
                'last_reconciliation_date': account.last_reconciliation_date.isoformat() if account.last_reconciliation_date else None,
                'current_balance': account.current_balance,
                'ytd_debit': account.ytd_debit,
                'ytd_credit': account.ytd_credit,
                'notes': account.notes,
                'company_id': account.company_id.id if account.company_id else None
            }

            return {'account': account_data}

        except Exception as e:
            return {'error': str(e)}

    @http.route('/api/v1/account/journal-entries', type='json', auth='user', methods=['GET'], csrf=False)
    def get_journal_entries(self, **kwargs):
        """Get journal entries with optional filtering."""
        try:
            # Get query parameters
            journal_id = kwargs.get('journal_id')
            entry_type = kwargs.get('entry_type')
            approval_status = kwargs.get('approval_status')
            date_from = kwargs.get('date_from')
            date_to = kwargs.get('date_to')
            limit = int(kwargs.get('limit', 100))
            offset = int(kwargs.get('offset', 0))

            # Build domain for filtering
            domain = []
            if journal_id:
                domain.append(('journal_id', '=', int(journal_id)))
            if entry_type:
                domain.append(('entry_type', '=', entry_type))
            if approval_status:
                domain.append(('approval_status', '=', approval_status))
            if date_from:
                domain.append(('date', '>=', date_from))
            if date_to:
                domain.append(('date', '<=', date_to))

            # Search journal entries
            entries = request.env['account.move'].sudo().search(
                domain,
                limit=limit,
                offset=offset,
                order='date desc'
            )

            # Format response data
            data = []
            for entry in entries:
                entry_data = {
                    'id': entry.id,
                    'name': entry.name,
                    'ref': entry.ref,
                    'date': entry.date.isoformat() if entry.date else None,
                    'journal_id': entry.journal_id.id if entry.journal_id else None,
                    'journal_name': entry.journal_id.name if entry.journal_id else None,
                    'entry_type': entry.entry_type,
                    'is_recurring': entry.is_recurring,
                    'approval_status': entry.approval_status,
                    'total_debit': entry.total_debit,
                    'total_credit': entry.total_credit,
                    'is_balanced': entry.is_balanced,
                    'state': entry.state
                }
                data.append(entry_data)

            return {
                'entries': data,
                'count': len(data),
                'total': len(request.env['account.move'].sudo().search(domain))
            }

        except Exception as e:
            return {'error': str(e)}

    @http.route('/api/v1/account/reconciliation', type='json', auth='user', methods=['GET'], csrf=False)
    def get_reconciliation_summary(self, **kwargs):
        """Get reconciliation summary."""
        try:
            days = int(kwargs.get('days', 30))

            # Get reconciliation summary
            summary = request.env['account.reconciliation.helper'].sudo().get_reconciliation_summary(days)

            return {'summary': summary}

        except Exception as e:
            return {'error': str(e)}

    @http.route('/api/v1/account/reconciliation', type='json', auth='user', methods=['POST'], csrf=False)
    def create_reconciliation(self, **kwargs):
        """Create a new reconciliation record."""
        try:
            # Extract reconciliation data
            reconciliation_data = {
                'statement_date': kwargs.get('statement_date'),
                'statement_number': kwargs.get('statement_number'),
                'account_id': int(kwargs.get('account_id')),
                'starting_balance': float(kwargs.get('starting_balance', 0.0)),
                'ending_balance': float(kwargs.get('ending_balance', 0.0)),
                'notes': kwargs.get('notes')
            }

            # Create reconciliation record
            reconciliation = request.env['account.reconciliation.helper'].sudo().create(reconciliation_data)

            return {
                'id': reconciliation.id,
                'message': 'Reconciliation record created successfully'
            }

        except Exception as e:
            return {'error': str(e)}

    @http.route('/api/v1/account/dashboard', type='json', auth='user', methods=['GET'], csrf=False)
    def get_account_dashboard(self):
        """Get accounting dashboard data."""
        try:
            # Get pending approvals
            pending_approvals = request.env['account.move'].sudo().get_pending_approvals()

            # Get reconciliation accounts
            reconciliation_accounts = request.env['account.account'].sudo().get_reconciliation_accounts()

            # Get budgeted accounts
            budgeted_accounts = request.env['account.account'].sudo().get_budgeted_accounts()

            # Get recurring entries due
            recurring_due = request.env['account.move'].sudo().get_recurring_entries_due()

            # Get reconciliation summary
            reconciliation_summary = request.env['account.reconciliation.helper'].sudo().get_reconciliation_summary()

            dashboard_data = {
                'pending_approvals_count': len(pending_approvals),
                'reconciliation_accounts_count': len(reconciliation_accounts),
                'budgeted_accounts_count': len(budgeted_accounts),
                'recurring_entries_due_count': len(recurring_due),
                'reconciliation_summary': reconciliation_summary,
                'generated_at': datetime.now().isoformat()
            }

            return {'dashboard': dashboard_data}

        except Exception as e:
            return {'error': str(e)}

    @http.route('/api/v1/account/accounts/<int:account_id>/budget', type='json', auth='user', methods=['POST'], csrf=False)
    def update_account_budget(self, account_id, **kwargs):
        """Update budget for a specific account."""
        try:
            account = request.env['account.account'].sudo().browse(account_id)

            if not account.exists():
                return {'error': 'Account not found'}

            budget_amount = float(kwargs.get('budget_amount', 0.0))

            if budget_amount > 0:
                account.action_update_budget(budget_amount)
                message = f'Budget updated to {budget_amount}'
            else:
                account.action_remove_budget()
                message = 'Account removed from budgeting'

            return {
                'id': account.id,
                'message': message,
                'is_budgeted': account.is_budgeted,
                'budget_amount': account.budget_amount
            }

        except Exception as e:
            return {'error': str(e)}

    @http.route('/api/v1/account/process-recurring', type='json', auth='user', methods=['POST'], csrf=False)
    def process_recurring_entries(self):
        """Process recurring journal entries that are due."""
        try:
            # Process recurring entries
            created_moves = request.env['account.move'].sudo().process_recurring_entries()

            return {
                'message': f'Processed {len(created_moves)} recurring entries',
                'created_moves_count': len(created_moves)
            }

        except Exception as e:
            return {'error': str(e)}