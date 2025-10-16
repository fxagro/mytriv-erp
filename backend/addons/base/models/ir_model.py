# -*- coding: utf-8 -*-
"""
Model Registry for MyTriv ERP

This module handles the model registry and metadata.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class IrModel(models.Model):
    """Model registry for MyTriv ERP"""

    _name = 'ir.model'
    _description = 'Models'

    name = fields.Char(
        string='Model Name',
        required=True,
        index=True,
        help='Technical name of the model'
    )

    model = fields.Char(
        string='Model',
        required=True,
        index=True,
        help='Technical model name (e.g. res.partner)'
    )

    info = fields.Text(
        string='Information',
        help='Description of the model'
    )

    state = fields.Selection([
        ('manual', 'Custom Object'),
        ('base', 'Base Object'),
    ], string='Type', default='manual', required=True)

    field_id = fields.One2many(
        'ir.model.fields',
        'model_id',
        string='Fields',
        help='Fields of this model'
    )

    access_ids = fields.One2many(
        'ir.model.access',
        'model_id',
        string='Access',
        help='Access rights for this model'
    )

    view_ids = fields.One2many(
        'ir.ui.view',
        'model',
        string='Views',
        help='Views for this model'
    )

    transient = fields.Boolean(
        string='Transient',
        default=False,
        help='If true, the model is transient (wizard-like)'
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    @api.model
    def register_model(self, model_name, model_class):
        """Register a new model in the registry"""
        # Check if model already exists
        existing = self.search([('model', '=', model_name)])
        if existing:
            return existing[0]

        # Create new model entry
        model_info = {
            'name': model_class._name,
            'model': model_name,
            'info': getattr(model_class, '_description', ''),
            'state': 'manual',
            'transient': getattr(model_class, '_transient', False)
        }

        return self.create(model_info)

    def action_view_fields(self):
        """View fields of this model"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Fields'),
            'res_model': 'ir.model.fields',
            'view_mode': 'tree,form',
            'domain': [('model_id', '=', self.id)],
            'context': {'default_model_id': self.id}
        }

    def action_view_access(self):
        """View access rights for this model"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Access Rights'),
            'res_model': 'ir.model.access',
            'view_mode': 'tree,form',
            'domain': [('model_id', '=', self.id)],
            'context': {'default_model_id': self.id}
        }


class IrModelFields(models.Model):
    """Model fields registry for MyTriv ERP"""

    _name = 'ir.model.fields'
    _description = 'Fields'

    name = fields.Char(
        string='Field Name',
        required=True,
        help='Technical name of the field'
    )

    field_description = fields.Char(
        string='Field Label',
        required=True,
        translate=True,
        help='Label of the field'
    )

    model_id = fields.Many2one(
        'ir.model',
        string='Model',
        required=True,
        ondelete='cascade',
        help='Model this field belongs to'
    )

    model = fields.Char(
        string='Model Name',
        related='model_id.model',
        store=True,
        help='Technical model name'
    )

    ttype = fields.Selection([
        ('char', 'Char'),
        ('text', 'Text'),
        ('html', 'HTML'),
        ('integer', 'Integer'),
        ('float', 'Float'),
        ('monetary', 'Monetary'),
        ('date', 'Date'),
        ('datetime', 'DateTime'),
        ('boolean', 'Boolean'),
        ('selection', 'Selection'),
        ('many2one', 'Many2One'),
        ('one2many', 'One2Many'),
        ('many2many', 'Many2Many'),
        ('binary', 'Binary'),
        ('reference', 'Reference'),
    ], string='Field Type', required=True)

    required = fields.Boolean(
        string='Required',
        default=False,
        help='If true, the field is required'
    )

    readonly = fields.Boolean(
        string='Readonly',
        default=False,
        help='If true, the field is readonly'
    )

    help = fields.Text(
        string='Help',
        translate=True,
        help='Help text for the field'
    )

    relation = fields.Char(
        string='Related Model',
        help='For relational fields, the related model'
    )

    selection = fields.Char(
        string='Selection Options',
        help='For selection fields, the options'
    )

    state = fields.Selection([
        ('manual', 'Custom Field'),
        ('base', 'Base Field'),
    ], string='Type', default='manual', required=True)

    active = fields.Boolean(
        string='Active',
        default=True
    )


class IrModelAccess(models.Model):
    """Model access rights for MyTriv ERP"""

    _name = 'ir.model.access'
    _description = 'Access Rights'

    name = fields.Char(
        string='Name',
        required=True,
        help='Name of the access right'
    )

    model_id = fields.Many2one(
        'ir.model',
        string='Model',
        required=True,
        ondelete='cascade',
        help='Model this access applies to'
    )

    group_id = fields.Many2one(
        'res.groups',
        string='Group',
        help='Group this access applies to'
    )

    perm_read = fields.Boolean(
        string='Read Access',
        default=True,
        help='If true, the group can read records'
    )

    perm_write = fields.Boolean(
        string='Write Access',
        default=False,
        help='If true, the group can modify records'
    )

    perm_create = fields.Boolean(
        string='Create Access',
        default=False,
        help='If true, the group can create records'
    )

    perm_unlink = fields.Boolean(
        string='Delete Access',
        default=False,
        help='If true, the group can delete records'
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )


class ResGroups(models.Model):
    """User groups for MyTriv ERP"""

    _name = 'res.groups'
    _description = 'Groups'

    name = fields.Char(
        string='Group Name',
        required=True,
        translate=True,
        help='Name of the group'
    )

    users = fields.Many2many(
        'res.users',
        'res_groups_users_rel',
        'gid',
        'uid',
        string='Users'
    )

    model_access = fields.One2many(
        'ir.model.access',
        'group_id',
        string='Access Rights'
    )

    menu_access = fields.Many2many(
        'ir.ui.menu',
        'ir_ui_menu_group_rel',
        'gid',
        'menu_id',
        string='Menu Access'
    )

    rule_groups = fields.Many2many(
        'ir.rule',
        'ir_rule_group_rel',
        'group_id',
        'rule_group_id',
        string='Rules'
    )

    comment = fields.Text(
        string='Comment',
        translate=True,
        help='Description of the group'
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )