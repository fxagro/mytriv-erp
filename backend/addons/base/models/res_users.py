# -*- coding: utf-8 -*-
"""
User Management Model for MyTriv ERP

This module handles user authentication, groups, and permissions.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    """User model for MyTriv ERP"""

    _name = 'res.users'
    _description = 'Users'
    _inherits = {'res.partner': 'partner_id'}

    # Relations
    partner_id = fields.Many2one(
        'res.partner',
        string='Related Partner',
        required=True,
        ondelete='cascade',
        help='Partner-related data of the user'
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    company_ids = fields.Many2many(
        'res.company',
        string='Allowed Companies',
        default=lambda self: [self.env.company.id]
    )

    # Authentication fields
    login = fields.Char(
        string='Login',
        required=True,
        help='Used to log into the system'
    )

    password = fields.Char(
        string='Password',
        help='Encrypted password for the user'
    )

    new_password = fields.Char(
        string='New Password',
        help='Use to change password'
    )

    # User status
    active = fields.Boolean(
        string='Active',
        default=True,
        help='If unchecked, this user will not be able to log in'
    )

    share = fields.Boolean(
        string='Share User',
        default=False,
        help='External user with limited access'
    )

    # Groups and permissions
    groups_id = fields.Many2many(
        'res.groups',
        'res_groups_users_rel',
        'uid',
        'gid',
        string='Groups'
    )

    # User preferences
    lang = fields.Selection(
        string='Language',
        selection=lambda self: self._get_lang_options(),
        default=lambda self: self.env.lang or 'en_US'
    )

    tz = fields.Selection(
        string='Timezone',
        selection=lambda self: self._get_tz_options(),
        default='UTC'
    )

    # Notification preferences
    notification_type = fields.Selection([
        ('email', 'Handle by Emails'),
        ('inbox', 'Handle in Odoo'),
    ], string='Notification Management', default='email')

    @api.model
    def _get_lang_options(self):
        """Get available language options"""
        return [
            ('en_US', 'English (US)'),
            ('id_ID', 'Indonesian'),
            ('es_ES', 'Spanish'),
            ('fr_FR', 'French'),
            ('de_DE', 'German'),
            ('zh_CN', 'Chinese (Simplified)'),
            ('ja_JP', 'Japanese'),
        ]

    @api.model
    def _get_tz_options(self):
        """Get available timezone options"""
        return [
            ('UTC', 'UTC'),
            ('Asia/Jakarta', 'Asia/Jakarta'),
            ('America/New_York', 'Eastern Time (US & Canada)'),
            ('America/Chicago', 'Central Time (US & Canada)'),
            ('America/Denver', 'Mountain Time (US & Canada)'),
            ('America/Los_Angeles', 'Pacific Time (US & Canada)'),
            ('Europe/London', 'GMT (Greenwich Mean Time)'),
            ('Europe/Paris', 'Central European Time'),
            ('Asia/Tokyo', 'Japan Standard Time'),
            ('Australia/Sydney', 'Australian Eastern Time'),
        ]

    @api.model
    def create(self, vals):
        """Create user and related partner"""
        # Create partner first if not provided
        if 'partner_id' not in vals:
            partner_vals = {
                'name': vals.get('name', vals.get('login', 'User')),
                'email': vals.get('email', vals.get('login')),
                'is_company': False,
                'type': 'contact',
            }
            partner = self.env['res.partner'].create(partner_vals)
            vals['partner_id'] = partner.id

        return super(ResUsers, self).create(vals)

    def write(self, vals):
        """Update user and sync with partner"""
        # Sync email with partner if changed
        if 'email' in vals:
            for user in self:
                if user.partner_id:
                    user.partner_id.email = vals['email']

        return super(ResUsers, self).write(vals)

    def _check_credentials(self, password):
        """Check user credentials"""
        self.ensure_one()
        # In a real implementation, this would check encrypted passwords
        return self.password == password

    def action_reset_password(self):
        """Reset user password"""
        self.ensure_one()
        # Generate temporary password
        temp_password = self._generate_temp_password()
        self.password = temp_password
        # Send notification email
        self._send_password_reset_email(temp_password)

    def _generate_temp_password(self):
        """Generate temporary password"""
        import random
        import string
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(12))

    def _send_password_reset_email(self, temp_password):
        """Send password reset email"""
        # Email template would be implemented here
        _logger.info(f"Password reset for {self.login}: {temp_password}")

    @api.model
    def authenticate(self, login, password):
        """Authenticate user"""
        user = self.search([('login', '=', login), ('active', '=', True)])
        if user and user._check_credentials(password):
            return user
        return False

    def action_toggle_active(self):
        """Toggle user active status"""
        for user in self:
            user.active = not user.active