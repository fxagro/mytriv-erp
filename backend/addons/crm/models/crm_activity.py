# -*- coding: utf-8 -*-
"""
Activity Management Model for MyTriv ERP

This module handles activity tracking and management.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class CrmActivity(models.Model):
    """Activity model for MyTriv ERP"""

    _name = 'crm.activity'
    _description = 'CRM Activity'

    name = fields.Char(
        string='Activity Name',
        required=True,
        help='Name of the activity'
    )

    activity_type = fields.Selection([
        ('call', 'Phone Call'),
        ('meeting', 'Meeting'),
        ('email', 'Email'),
        ('demo', 'Demo'),
        ('proposal', 'Proposal'),
        ('quotation', 'Quotation'),
        ('negotiation', 'Negotiation'),
        ('closing', 'Closing'),
        ('other', 'Other'),
    ], string='Activity Type', required=True)

    description = fields.Text(
        string='Description',
        help='Description of the activity'
    )

    # Related Records
    lead_id = fields.Many2one(
        'crm.lead',
        string='Lead',
        help='Related lead'
    )

    opportunity_id = fields.Many2one(
        'crm.opportunity',
        string='Opportunity',
        help='Related opportunity'
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        help='Related customer'
    )

    # Scheduling
    date_deadline = fields.Date(
        string='Deadline',
        help='Deadline for completing this activity'
    )

    date_done = fields.Date(
        string='Done Date',
        help='Date when activity was completed'
    )

    # Assignment
    user_id = fields.Many2one(
        'res.users',
        string='Assigned To',
        default=lambda self: self.env.user,
        help='User assigned to this activity'
    )

    # Status
    state = fields.Selection([
        ('planned', 'Planned'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='planned')

    # Priority
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
    ], string='Priority', default='1')

    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    def action_done(self):
        """Mark activity as done"""
        self.write({
            'state': 'done',
            'date_done': datetime.now().date()
        })

    def action_cancel(self):
        """Cancel activity"""
        self.write({'state': 'cancelled'})

    @api.model
    def get_upcoming_activities(self, user_id=None, limit=10):
        """Get upcoming activities"""
        domain = [
            ('state', '=', 'planned'),
            ('date_deadline', '>=', datetime.now().date())
        ]

        if user_id:
            domain.append(('user_id', '=', user_id))

        activities = self.search(domain, limit=limit, order='date_deadline')
        return activities

    @api.model
    def get_overdue_activities(self, user_id=None, limit=10):
        """Get overdue activities"""
        domain = [
            ('state', '=', 'planned'),
            ('date_deadline', '<', datetime.now().date())
        ]

        if user_id:
            domain.append(('user_id', '=', user_id))

        activities = self.search(domain, limit=limit, order='date_deadline desc')
        return activities


class CrmMeeting(models.Model):
    """Meeting model for MyTriv ERP"""

    _name = 'crm.meeting'
    _description = 'Meeting'

    name = fields.Char(
        string='Meeting Subject',
        required=True,
        help='Subject of the meeting'
    )

    description = fields.Text(
        string='Description',
        help='Meeting description'
    )

    # Related Records
    lead_id = fields.Many2one(
        'crm.lead',
        string='Lead',
        help='Related lead'
    )

    opportunity_id = fields.Many2one(
        'crm.opportunity',
        string='Opportunity',
        help='Related opportunity'
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        help='Related customer'
    )

    # Meeting Details
    start_datetime = fields.Datetime(
        string='Start Date',
        required=True,
        help='Meeting start date and time'
    )

    end_datetime = fields.Datetime(
        string='End Date',
        required=True,
        help='Meeting end date and time'
    )

    duration = fields.Float(
        string='Duration (hours)',
        compute='_compute_duration',
        store=True,
        help='Meeting duration in hours'
    )

    location = fields.Char(
        string='Location',
        help='Meeting location'
    )

    meeting_type = fields.Selection([
        ('in_person', 'In Person'),
        ('video_call', 'Video Call'),
        ('phone_call', 'Phone Call'),
        ('webinar', 'Webinar'),
    ], string='Meeting Type', default='in_person')

    # Attendees
    attendee_ids = fields.Many2many(
        'res.partner',
        'crm_meeting_attendees_rel',
        'meeting_id',
        'partner_id',
        string='Attendees',
        help='Meeting attendees'
    )

    # Assignment
    user_id = fields.Many2one(
        'res.users',
        string='Organized By',
        default=lambda self: self.env.user,
        help='User who organized the meeting'
    )

    # Status
    state = fields.Selection([
        ('planned', 'Planned'),
        ('held', 'Held'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='planned')

    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    @api.depends('start_datetime', 'end_datetime')
    def _compute_duration(self):
        """Compute meeting duration"""
        for meeting in self:
            if meeting.start_datetime and meeting.end_datetime:
                delta = meeting.end_datetime - meeting.start_datetime
                meeting.duration = delta.total_seconds() / 3600
            else:
                meeting.duration = 0.0

    @api.constrains('start_datetime', 'end_datetime')
    def _check_dates(self):
        """Validate meeting dates"""
        for meeting in self:
            if meeting.end_datetime <= meeting.start_datetime:
                raise ValidationError(_("End date must be after start date"))

    def action_held(self):
        """Mark meeting as held"""
        self.write({'state': 'held'})

    def action_cancel(self):
        """Cancel meeting"""
        self.write({'state': 'cancelled'})


class CrmPhonecall(models.Model):
    """Phone call model for MyTriv ERP"""

    _name = 'crm.phonecall'
    _description = 'Phone Call'

    name = fields.Char(
        string='Call Summary',
        required=True,
        help='Summary of the phone call'
    )

    description = fields.Text(
        string='Description',
        help='Call description and notes'
    )

    # Related Records
    lead_id = fields.Many2one(
        'crm.lead',
        string='Lead',
        help='Related lead'
    )

    opportunity_id = fields.Many2one(
        'crm.opportunity',
        string='Opportunity',
        help='Related opportunity'
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        help='Related customer'
    )

    # Call Details
    call_date = fields.Datetime(
        string='Call Date',
        default=lambda self: datetime.now(),
        help='Date and time of the call'
    )

    duration = fields.Float(
        string='Duration (minutes)',
        help='Call duration in minutes'
    )

    call_type = fields.Selection([
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
    ], string='Call Type', default='outbound')

    call_purpose = fields.Selection([
        ('prospecting', 'Prospecting'),
        ('qualification', 'Qualification'),
        ('negotiation', 'Negotiation'),
        ('closing', 'Closing'),
        ('support', 'Support'),
        ('other', 'Other'),
    ], string='Call Purpose', default='prospecting')

    # Call Result
    state = fields.Selection([
        ('planned', 'Planned'),
        ('held', 'Held'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='planned')

    call_result = fields.Selection([
        ('successful', 'Successful'),
        ('no_answer', 'No Answer'),
        ('busy', 'Busy'),
        ('wrong_number', 'Wrong Number'),
        ('callback', 'Call Back'),
    ], string='Call Result')

    # Assignment
    user_id = fields.Many2one(
        'res.users',
        string='Called By',
        default=lambda self: self.env.user,
        help='User who made the call'
    )

    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    def action_held(self):
        """Mark call as held"""
        self.write({'state': 'held'})

    def action_cancel(self):
        """Cancel call"""
        self.write({'state': 'cancelled'})