# -*- coding: utf-8 -*-
"""
Base models for MyTriv ERP

This module contains core models that are fundamental to the ERP system:
- res.users: User management
- res.partner: Partners (customers, suppliers, etc.)
- res.company: Company configuration
- ir.model: Model registry
- ir.attachment: File attachments
"""

from . import res_users
from . import res_partner
from . import res_company
from . import ir_model
from . import ir_attachment
from . import base_model