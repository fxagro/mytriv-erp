# -*- coding: utf-8 -*-
"""
Sale models for MyTriv ERP

This module contains sales-related models:
- sale.order: Sales order management
- sale.quotation: Quotation management
- product.product: Product catalog
- product.category: Product categories
- sale.delivery: Delivery management
- sale.invoice: Invoice management
- res.partner: Customer management
"""

from . import sale_order
from . import sale_quotation
from . import product
from . import product_category
from . import sale_delivery
from . import sale_invoice
from . import customer