# -*- coding: utf-8 -*-
"""
Base Model for MyTriv ERP

This module provides the BaseModel class that all other models inherit from.
It contains common functionality and utilities used across the ERP system.
"""

import logging
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class BaseModel(models.AbstractModel):
    """Base class for all MyTriv ERP models"""

    _name = 'base'
    _description = 'Base Model'

    # Common fields that many models might need
    create_date = fields.Datetime(
        string='Created on',
        readonly=True,
        default=lambda self: datetime.now()
    )

    create_uid = fields.Many2one(
        'res.users',
        string='Created by',
        readonly=True,
        default=lambda self: self.env.uid
    )

    write_date = fields.Datetime(
        string='Last Updated on',
        readonly=True,
        default=lambda self: datetime.now()
    )

    write_uid = fields.Many2one(
        'res.users',
        string='Last Updated by',
        readonly=True,
        default=lambda self: self.env.uid
    )

    @api.model
    def create(self, vals):
        """Override create to set create_date and create_uid"""
        if 'create_date' not in vals:
            vals['create_date'] = datetime.now()
        if 'create_uid' not in vals:
            vals['create_uid'] = self.env.uid
        return super(BaseModel, self).create(vals)

    def write(self, vals):
        """Override write to set write_date and write_uid"""
        if 'write_date' not in vals:
            vals['write_date'] = datetime.now()
        if 'write_uid' not in vals:
            vals['write_uid'] = self.env.uid
        return super(BaseModel, self).write(vals)

    @api.model
    def _get_default_company(self):
        """Get default company for the current user"""
        return self.env.company

    def _check_company(self):
        """Check if records belong to the same company"""
        if len(self.company_id) > 1:
            companies = self.company_id
            if len(companies) != 1:
                raise ValidationError(_("All records must belong to the same company"))

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        """Override search_read to add common filters"""
        if domain is None:
            domain = []

        # Add active filter if model has active field and not explicitly filtered
        if hasattr(self._fields, 'active') and not any(d[0] == 'active' for d in domain):
            domain = [('active', '=', True)] + domain

        return super(BaseModel, self).search_read(domain, fields, offset, limit, order)


class BaseModelWithActive(models.AbstractModel):
    """Base class for models that have an active field"""

    _name = 'base.with.active'
    _description = 'Base Model with Active Field'

    active = fields.Boolean(
        string='Active',
        default=True,
        help='If unchecked, this record will be archived'
    )

    def toggle_active(self):
        """Toggle the active state of records"""
        for record in self:
            record.active = not record.active


class BaseModelWithCompany(models.AbstractModel):
    """Base class for models that belong to a company"""

    _name = 'base.with.company'
    _description = 'Base Model with Company'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    @api.constrains('company_id')
    def _check_company_id(self):
        """Ensure company_id is set"""
        for record in self:
            if not record.company_id:
                raise ValidationError(_("Company is required"))