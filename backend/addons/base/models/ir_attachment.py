# -*- coding: utf-8 -*-
"""
Attachment Management for MyTriv ERP

This module handles file attachments and document management.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
import base64
import mimetypes
from datetime import datetime

_logger = logging.getLogger(__name__)


class IrAttachment(models.Model):
    """Attachment model for MyTriv ERP"""

    _name = 'ir.attachment'
    _description = 'Attachment'

    # Basic information
    name = fields.Char(
        string='Attachment Name',
        required=True,
        help='Name of the attachment'
    )

    description = fields.Text(
        string='Description',
        help='Description of the attachment'
    )

    # File data
    datas = fields.Binary(
        string='File Content',
        help='File content encoded in base64'
    )

    file_size = fields.Integer(
        string='File Size',
        compute='_compute_file_size',
        store=True,
        help='Size of the file in bytes'
    )

    # File metadata
    mimetype = fields.Char(
        string='MIME Type',
        compute='_compute_mimetype',
        store=True,
        help='MIME type of the file'
    )

    file_type = fields.Char(
        string='File Type',
        compute='_compute_file_type',
        store=True,
        help='Type of file (e.g. image, document)'
    )

    # Storage information
    store_fname = fields.Char(
        string='Stored Filename',
        help='Filename used for storage'
    )

    db_datas = fields.Binary(
        string='Database Data',
        help='File content stored in database'
    )

    # Relations
    res_model = fields.Char(
        string='Resource Model',
        index=True,
        help='Model of the related record'
    )

    res_id = fields.Integer(
        string='Resource ID',
        index=True,
        help='ID of the related record'
    )

    res_field = fields.Char(
        string='Resource Field',
        help='Field of the related record'
    )

    # Organization
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )

    user_id = fields.Many2one(
        'res.users',
        string='Owner',
        default=lambda self: self.env.user,
        help='Owner of the attachment'
    )

    # Status
    public = fields.Boolean(
        string='Public',
        default=False,
        help='If true, the attachment is public'
    )

    active = fields.Boolean(
        string='Active',
        default=True,
        help='If unchecked, this attachment will be archived'
    )

    # Access information
    access_token = fields.Char(
        string='Access Token',
        help='Token for public access'
    )

    # URL for web access
    url = fields.Char(
        string='URL',
        compute='_compute_url',
        help='URL for accessing the attachment'
    )

    @api.depends('datas')
    def _compute_file_size(self):
        """Compute file size from datas"""
        for attachment in self:
            if attachment.datas:
                attachment.file_size = len(attachment.datas.decode('utf-8')) if isinstance(attachment.datas, str) else len(attachment.datas)
            else:
                attachment.file_size = 0

    @api.depends('name')
    def _compute_mimetype(self):
        """Compute MIME type from filename"""
        for attachment in self:
            if attachment.name:
                attachment.mimetype = mimetypes.guess_type(attachment.name)[0] or 'application/octet-stream'
            else:
                attachment.mimetype = 'application/octet-stream'

    @api.depends('mimetype')
    def _compute_file_type(self):
        """Compute file type from MIME type"""
        for attachment in self:
            if attachment.mimetype:
                if attachment.mimetype.startswith('image/'):
                    attachment.file_type = 'image'
                elif attachment.mimetype.startswith('video/'):
                    attachment.file_type = 'video'
                elif attachment.mimetype.startswith('audio/'):
                    attachment.file_type = 'audio'
                elif attachment.mimetype in ['application/pdf']:
                    attachment.file_type = 'pdf'
                elif attachment.mimetype in ['application/msword',
                                           'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
                    attachment.file_type = 'document'
                elif attachment.mimetype in ['application/vnd.ms-excel',
                                           'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
                    attachment.file_type = 'spreadsheet'
                else:
                    attachment.file_type = 'other'
            else:
                attachment.file_type = 'unknown'

    @api.depends('id', 'access_token')
    def _compute_url(self):
        """Compute URL for attachment access"""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for attachment in self:
            if attachment.public and attachment.access_token:
                attachment.url = f"{base_url}/web/content/{attachment.id}?access_token={attachment.access_token}"
            else:
                attachment.url = f"{base_url}/web/content/{attachment.id}"

    @api.model
    def create(self, vals):
        """Create attachment with proper defaults"""
        if 'name' not in vals:
            vals['name'] = 'Attachment'

        if 'user_id' not in vals:
            vals['user_id'] = self.env.user.id

        if 'company_id' not in vals:
            vals['company_id'] = self.env.company.id

        # Generate access token for public attachments
        if vals.get('public', False) and 'access_token' not in vals:
            vals['access_token'] = self._generate_access_token()

        return super(IrAttachment, self).create(vals)

    def _generate_access_token(self):
        """Generate access token for public attachments"""
        import secrets
        return secrets.token_urlsafe(32)

    def action_download(self):
        """Download the attachment"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{self.id}',
            'target': 'self'
        }

    def action_preview(self):
        """Preview the attachment"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.name,
            'res_model': 'ir.attachment',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new'
        }

    def unlink(self):
        """Delete attachment and clean up files"""
        # Clean up physical files if stored on filesystem
        for attachment in self:
            if attachment.store_fname:
                # Remove from filesystem
                pass

        return super(IrAttachment, self).unlink()

    @api.model
    def create_from_data(self, name, data, res_model=None, res_id=None, mimetype=None):
        """Create attachment from binary data"""
        if isinstance(data, str):
            data = data.encode('utf-8')

        vals = {
            'name': name,
            'datas': base64.b64encode(data).decode('utf-8'),
        }

        if res_model:
            vals['res_model'] = res_model
        if res_id:
            vals['res_id'] = res_id
        if mimetype:
            vals['mimetype'] = mimetype

        return self.create(vals)

    def get_base64_data(self):
        """Get attachment data as base64"""
        self.ensure_one()
        if self.datas:
            return self.datas
        return False

    def get_binary_data(self):
        """Get attachment data as binary"""
        self.ensure_one()
        if self.datas:
            return base64.b64decode(self.datas)
        return False

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        """Override search_read to respect access rights"""
        if domain is None:
            domain = []

        # Add access control for non-admin users
        if not self.env.user._is_admin():
            domain = ['|', ('public', '=', True), ('user_id', '=', self.env.user.id)] + domain

        return super(IrAttachment, self).search_read(domain, fields, offset, limit, order)


class IrConfigParameter(models.Model):
    """Configuration parameters for MyTriv ERP"""

    _name = 'ir.config_parameter'
    _description = 'Configuration Parameters'

    key = fields.Char(
        string='Key',
        required=True,
        index=True,
        help='Configuration key'
    )

    value = fields.Text(
        string='Value',
        required=True,
        help='Configuration value'
    )

    @api.model
    def get_param(self, key, default=False):
        """Get configuration parameter value"""
        param = self.search([('key', '=', key)], limit=1)
        if param:
            return param.value
        return default

    @api.model
    def set_param(self, key, value):
        """Set configuration parameter value"""
        param = self.search([('key', '=', key)], limit=1)
        if param:
            param.value = str(value)
        else:
            self.create({'key': key, 'value': str(value)})

    @api.model
    def get_bool_param(self, key, default=False):
        """Get boolean configuration parameter"""
        value = self.get_param(key, default)
        return value in ('True', 'true', '1', True)