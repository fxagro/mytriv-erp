# -*- coding: utf-8 -*-
"""
Recruitment Management Model for MyTriv ERP

This module handles recruitment and applicant tracking.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class HrRecruitment(models.Model):
    """Recruitment model for MyTriv ERP"""

    _name = 'hr.recruitment'
    _description = 'Recruitment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Job Position',
        required=True,
        help='Job position being recruited for'
    )

    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        help='Department for the position'
    )

    job_id = fields.Many2one(
        'hr.job',
        string='Related Job',
        help='Related job position'
    )

    # Recruitment Details
    no_of_recruitment = fields.Integer(
        string='Expected New Employees',
        default=1,
        help='Number of positions to fill'
    )

    description = fields.Html(
        string='Job Description',
        help='Detailed job description'
    )

    requirements = fields.Html(
        string='Requirements',
        help='Job requirements and qualifications'
    )

    # Dates
    start_date = fields.Date(
        string='Start Date',
        help='Recruitment start date'
    )

    end_date = fields.Date(
        string='End Date',
        help='Recruitment end date'
    )

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft')

    # Statistics
    applicant_count = fields.Integer(
        string='Number of Applicants',
        compute='_compute_applicant_count'
    )

    hired_count = fields.Integer(
        string='Number Hired',
        compute='_compute_hired_count'
    )

    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    @api.depends('applicant_ids')
    def _compute_applicant_count(self):
        """Compute number of applicants"""
        for recruitment in self:
            recruitment.applicant_count = len(recruitment.applicant_ids)

    @api.depends('applicant_ids.stage_id')
    def _compute_hired_count(self):
        """Compute number of hired applicants"""
        for recruitment in self:
            hired = recruitment.applicant_ids.filtered(lambda a: a.stage_id.name == 'Hired')
            recruitment.hired_count = len(hired)

    def action_open(self):
        """Open recruitment"""
        self.write({'state': 'open'})

    def action_close(self):
        """Close recruitment"""
        self.write({'state': 'closed'})

    def action_cancel(self):
        """Cancel recruitment"""
        self.write({'state': 'cancelled'})


class HrApplicant(models.Model):
    """Applicant model for MyTriv ERP"""

    _name = 'hr.applicant'
    _description = 'Applicant'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Applicant Name',
        required=True,
        help='Name of the applicant'
    )

    partner_name = fields.Char(
        string='Contact Name',
        help='Contact person name'
    )

    email = fields.Char(
        string='Email',
        required=True,
        help='Applicant email address'
    )

    phone = fields.Char(
        string='Phone',
        help='Applicant phone number'
    )

    mobile = fields.Char(
        string='Mobile',
        help='Applicant mobile number'
    )

    # Application Details
    recruitment_id = fields.Many2one(
        'hr.recruitment',
        string='Recruitment',
        help='Recruitment this application is for'
    )

    department_id = fields.Many2one(
        'hr.department',
        string='Applied Department',
        related='recruitment_id.department_id',
        store=True
    )

    job_id = fields.Many2one(
        'hr.job',
        string='Applied Position',
        related='recruitment_id.job_id',
        store=True
    )

    # Personal Information
    birth_date = fields.Date(
        string='Date of Birth',
        help='Applicant date of birth'
    )

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string='Gender')

    address = fields.Text(
        string='Address',
        help='Applicant address'
    )

    # Education
    education_level = fields.Selection([
        ('high_school', 'High School'),
        ('diploma', 'Diploma'),
        ('bachelor', 'Bachelor Degree'),
        ('master', 'Master Degree'),
        ('doctorate', 'Doctorate'),
    ], string='Education Level')

    institution = fields.Char(
        string='Institution',
        help='Educational institution'
    )

    graduation_year = fields.Integer(
        string='Graduation Year'
    )

    # Experience
    experience_years = fields.Integer(
        string='Years of Experience',
        help='Years of work experience'
    )

    current_salary = fields.Float(
        string='Current Salary',
        help='Current salary expectation'
    )

    expected_salary = fields.Float(
        string='Expected Salary',
        help='Expected salary'
    )

    # Application Process
    stage_id = fields.Many2one(
        'hr.recruitment.stage',
        string='Stage',
        default=lambda self: self._get_default_stage(),
        track_visibility='onchange',
        help='Current stage in recruitment process'
    )

    source_id = fields.Many2one(
        'hr.recruitment.source',
        string='Source',
        help='Source of the application'
    )

    # Documents
    resume = fields.Binary(
        string='Resume',
        help='Applicant resume/CV'
    )

    cover_letter = fields.Text(
        string='Cover Letter',
        help='Applicant cover letter'
    )

    # Interview Details
    interview_date = fields.Datetime(
        string='Interview Date',
        help='Scheduled interview date'
    )

    interviewer_id = fields.Many2one(
        'hr.employee',
        string='Interviewer',
        help='Employee conducting the interview'
    )

    interview_notes = fields.Text(
        string='Interview Notes',
        help='Notes from interview'
    )

    # Status
    active = fields.Boolean(
        string='Active',
        default=True
    )

    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    @api.model
    def _get_default_stage(self):
        """Get default recruitment stage"""
        return self.env['hr.recruitment.stage'].search([
            ('is_default', '=', True)
        ], limit=1)

    def action_schedule_interview(self):
        """Schedule interview for applicant"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Schedule Interview'),
            'res_model': 'hr.applicant.interview',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_applicant_id': self.id}
        }

    def action_hire_applicant(self):
        """Hire the applicant"""
        self.write({'stage_id': self._get_hired_stage()})

    def _get_hired_stage(self):
        """Get hired stage"""
        return self.env['hr.recruitment.stage'].search([
            ('name', '=', 'Hired')
        ], limit=1)

    def action_reject_applicant(self):
        """Reject the applicant"""
        self.write({'active': False})


class HrRecruitmentStage(models.Model):
    """Recruitment stage model"""

    _name = 'hr.recruitment.stage'
    _description = 'Recruitment Stage'
    _order = 'sequence'

    name = fields.Char(
        string='Stage Name',
        required=True,
        translate=True
    )

    sequence = fields.Integer(
        string='Sequence',
        default=10
    )

    is_default = fields.Boolean(
        string='Is Default',
        default=False
    )

    requirements = fields.Text(
        string='Requirements',
        help='Requirements for this stage'
    )

    template_id = fields.Many2one(
        'mail.template',
        string='Email Template',
        help='Email template for this stage'
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )


class HrRecruitmentSource(models.Model):
    """Recruitment source model"""

    _name = 'hr.recruitment.source'
    _description = 'Recruitment Source'

    name = fields.Char(
        string='Source Name',
        required=True,
        translate=True
    )

    source_type = fields.Selection([
        ('website', 'Website'),
        ('referral', 'Referral'),
        ('job_board', 'Job Board'),
        ('social_media', 'Social Media'),
        ('agency', 'Agency'),
        ('walk_in', 'Walk In'),
        ('other', 'Other'),
    ], string='Source Type', default='other')

    active = fields.Boolean(
        string='Active',
        default=True
    )