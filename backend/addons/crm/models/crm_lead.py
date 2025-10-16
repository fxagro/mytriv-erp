# -*- coding: utf-8 -*-
"""
Lead Management Model for MyTriv ERP

This module handles lead management and qualification.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    """Lead model for MyTriv ERP"""

    _name = 'crm.lead'
    _description = 'Lead'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Basic Information
    name = fields.Char(
        string='Lead Name',
        required=True,
        help='Name of the lead'
    )

    lead_id = fields.Char(
        string='Lead ID',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )

    # Contact Information
    contact_name = fields.Char(
        string='Contact Name',
        help='Primary contact person name'
    )

    title = fields.Char(
        string='Job Title',
        help='Job title of the contact person'
    )

    email_from = fields.Char(
        string='Email',
        help='Email address of the lead'
    )

    phone = fields.Char(
        string='Phone',
        help='Phone number of the lead'
    )

    mobile = fields.Char(
        string='Mobile',
        help='Mobile number of the lead'
    )

    # Company Information
    partner_name = fields.Char(
        string='Company',
        help='Company name'
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        help='Related partner record'
    )

    # Address Information
    street = fields.Char(
        string='Street',
        help='Street address'
    )

    street2 = fields.Char(
        string='Street 2',
        help='Additional street address'
    )

    city = fields.Char(
        string='City',
        help='City of the lead'
    )

    state_id = fields.Many2one(
        'res.country.state',
        string='State',
        domain="[('country_id', '=', country_id)]"
    )

    zip = fields.Char(
        string='ZIP',
        help='ZIP code'
    )

    country_id = fields.Many2one(
        'res.country',
        string='Country'
    )

    # Lead Details
    description = fields.Text(
        string='Description',
        help='Description of the lead'
    )

    priority = fields.Selection([
        ('0', 'Very Low'),
        ('1', 'Low'),
        ('2', 'Medium'),
        ('3', 'High'),
        ('4', 'Very High'),
    ], string='Priority', default='1')

    # Lead Source
    source_id = fields.Many2one(
        'crm.lead.source',
        string='Lead Source',
        help='Source of the lead'
    )

    # Campaign Information
    campaign_id = fields.Many2one(
        'crm.campaign',
        string='Campaign',
        help='Marketing campaign that generated this lead'
    )

    # Lead Status
    stage_id = fields.Many2one(
        'crm.stage',
        string='Stage',
        track_visibility='onchange',
        index=True,
        group_expand='_read_group_stage_ids',
        default=lambda self: self._get_default_stage_id()
    )

    # Sales Team
    team_id = fields.Many2one(
        'crm.team',
        string='Sales Team',
        default=lambda self: self._get_default_team_id()
    )

    user_id = fields.Many2one(
        'res.users',
        string='Salesperson',
        index=True,
        track_visibility='onchange',
        default=lambda self: self.env.user
    )

    # Lead Scoring
    score = fields.Integer(
        string='Score',
        help='Lead score for prioritization'
    )

    # Financial Information
    planned_revenue = fields.Float(
        string='Expected Revenue',
        track_visibility='onchange',
        help='Expected revenue from this lead'
    )

    probability = fields.Float(
        string='Probability (%)',
        help='Probability of conversion'
    )

    # Dates
    date_open = fields.Datetime(
        string='Opened',
        readonly=True,
        default=lambda self: datetime.now()
    )

    date_closed = fields.Datetime(
        string='Closed',
        readonly=True,
        help='Date when lead was closed'
    )

    date_last_stage_update = fields.Datetime(
        string='Last Stage Update',
        default=lambda self: datetime.now()
    )

    # Activity Information
    next_activity_id = fields.Many2one(
        'crm.activity',
        string='Next Activity'
    )

    date_action = fields.Date(
        string='Next Activity Date'
    )

    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    # Status
    active = fields.Boolean(
        string='Active',
        default=True
    )

    # Lost Reason
    lost_reason = fields.Many2one(
        'crm.lost.reason',
        string='Lost Reason'
    )

    @api.model
    def create(self, vals):
        """Create lead with auto-generated ID"""
        if vals.get('lead_id', _('New')) == _('New'):
            vals['lead_id'] = self._generate_lead_id()

        return super(CrmLead, self).create(vals)

    def _generate_lead_id(self):
        """Generate unique lead ID"""
        sequence = self.env['ir.sequence'].search([
            ('code', '=', 'crm.lead')
        ], limit=1)

        if sequence:
            return sequence.next_by_id()
        else:
            last_lead = self.search([], order='id desc', limit=1)
            return f'LEAD{(last_lead.id + 1):04d}' if last_lead else 'LEAD0001'

    @api.model
    def _get_default_stage_id(self):
        """Get default stage"""
        return self.env['crm.stage'].search([
            ('is_default', '=', True)
        ], limit=1)

    @api.model
    def _get_default_team_id(self):
        """Get default sales team"""
        return self.env['crm.team'].search([
            ('company_id', '=', self.env.company.id)
        ], limit=1)

    @api.depends('stage_id')
    def _compute_stage_name(self):
        """Compute stage name"""
        for lead in self:
            lead.stage_name = lead.stage_id.name if lead.stage_id else ''

    @api.constrains('email_from')
    def _check_email_format(self):
        """Validate email format"""
        for lead in self:
            if lead.email_from:
                if '@' not in lead.email_from or '.' not in lead.email_from:
                    raise ValidationError(_("Invalid email format"))

    def action_convert_to_opportunity(self):
        """Convert lead to opportunity"""
        self.ensure_one()
        if self.stage_id.is_won:
            raise UserError(_("Lead is already won"))

        # Create opportunity
        opportunity = self.env['crm.opportunity'].create({
            'name': self.name,
            'partner_id': self.partner_id.id,
            'email_from': self.email_from,
            'phone': self.phone,
            'planned_revenue': self.planned_revenue,
            'probability': self.probability,
            'team_id': self.team_id.id,
            'user_id': self.user_id.id,
            'company_id': self.company_id.id,
            'description': self.description,
        })

        # Mark lead as converted
        self.write({
            'stage_id': self.env['crm.stage'].search([('is_won', '=', True)], limit=1).id
        })

        return opportunity

    def action_schedule_meeting(self):
        """Schedule meeting for lead"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Schedule Meeting'),
            'res_model': 'crm.meeting',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_lead_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_email_from': self.email_from,
            }
        }

    def action_log_phone_call(self):
        """Log phone call for lead"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Log Phone Call'),
            'res_model': 'crm.phonecall',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_lead_id': self.id,
                'default_partner_id': self.partner_id.id,
            }
        }

    def action_mark_lost(self):
        """Mark lead as lost"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Mark as Lost'),
            'res_model': 'crm.lead.lost',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_lead_id': self.id}
        }

    def action_view_partner(self):
        """View related partner"""
        self.ensure_one()
        if self.partner_id:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Customer'),
                'res_model': 'res.partner',
                'view_mode': 'form',
                'res_id': self.partner_id.id
            }
        return False

    @api.model
    def get_leads_by_stage(self):
        """Get leads grouped by stage"""
        leads = self.read_group(
            domain=[('active', '=', True)],
            fields=['stage_id'],
            groupby=['stage_id']
        )

        result = {}
        for lead in leads:
            stage_name = self.env['crm.stage'].browse(lead['stage_id'][0]).name
            result[stage_name] = lead['stage_id_count']

        return result

    @api.model
    def get_lead_conversion_rate(self, start_date=None, end_date=None):
        """Get lead conversion rate"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()

        total_leads = self.search_count([
            ('date_open', '>=', start_date),
            ('date_open', '<=', end_date)
        ])

        converted_leads = self.search_count([
            ('date_open', '>=', start_date),
            ('date_open', '<=', end_date),
            ('stage_id.is_won', '=', True)
        ])

        if total_leads == 0:
            return 0.0

        return (converted_leads / total_leads) * 100


class CrmLeadSource(models.Model):
    """Lead source model"""

    _name = 'crm.lead.source'
    _description = 'Lead Source'

    name = fields.Char(
        string='Source Name',
        required=True,
        translate=True
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )


class CrmLostReason(models.Model):
    """Lost reason model"""

    _name = 'crm.lost.reason'
    _description = 'Lost Reason'

    name = fields.Char(
        string='Reason',
        required=True,
        translate=True
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )