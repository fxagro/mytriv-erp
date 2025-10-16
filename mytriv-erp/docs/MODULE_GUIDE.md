# MyTriv ERP Module Development Guide

## Overview

This guide provides comprehensive instructions for developing custom modules for MyTriv ERP. It covers module structure, development best practices, and integration with the existing system.

## Module Structure

### Standard Odoo Module Layout

```
custom_module/
├── __init__.py              # Module initialization
├── __manifest__.py          # Module manifest
├── controllers/             # HTTP controllers
│   ├── __init__.py
│   └── controllers.py
├── models/                  # Odoo models
│   ├── __init__.py
│   └── models.py
├── views/                   # XML views
│   ├── __init__.py
│   └── views.xml
├── security/                # Security files
│   └── ir.model.access.csv
├── data/                    # Data files
│   └── data.xml
└── README.md               # Module documentation
```

## Creating a New Module

### 1. Module Initialization

**`__init__.py`:**
```python
# -*- coding: utf-8 -*-

from . import controllers
from . import models
```

### 2. Module Manifest

**`__manifest__.py`:**
```python
# -*- coding: utf-8 -*-
{
    'name': 'Your Module Name',
    'version': '17.0.1.0.0',
    'category': 'Custom',
    'summary': 'Brief description of your module',
    'description': """
        Detailed description of what your module does.
        Explain the purpose and functionality.
    """,
    'author': 'Your Name',
    'website': 'https://github.com/your-username/mytriv-erp',
    'license': 'LGPL-3',
    'depends': ['base', 'web'],  # List dependencies
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'data/data.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
```

### 3. Models

**`models/models.py`:**
```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api

class YourModel(models.Model):
    _name = 'your.model'
    _description = 'Your Model Description'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def create(self, vals):
        # Custom logic before creation
        return super(YourModel, self).create(vals)

    def write(self, vals):
        # Custom logic before update
        return super(YourModel, self).write(vals)
```

### 4. Controllers

**`controllers/controllers.py`:**
```python
# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class YourController(http.Controller):

    @http.route('/your/route', type='http', auth='user', website=True)
    def your_endpoint(self):
        # Your controller logic
        return request.render('your_module.your_template')
```

### 5. Views

**`views/views.xml`:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <!-- Your views here -->
        <record id="your_model_view_form" model="ir.ui.view">
            <field name="name">your.model.form</field>
            <field name="model">your.model</field>
            <field name="arch" type="xml">
                <form string="Your Model">
                    <sheet>
                        <group>
                            <field name="name"/>
                            <field name="description"/>
                        </group>
                    </sheet>
                </form>
            </field>
        </record>
    </data>
</odoo>
```

### 6. Security

**`security/ir.model.access.csv`:**
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_your_model_user,Your Model User Access,model_your_model,base.group_user,1,1,1,0
```

## API Integration

### Using the REST API

The `base_rest_api` module provides REST endpoints for all Odoo models:

#### Get All Records
```bash
GET /api/models/hr.employee
```

#### Get Specific Record
```bash
GET /api/models/hr.employee/1
```

#### Create Record
```bash
POST /api/models/hr.employee
Content-Type: application/json

{
    "name": "John Doe",
    "work_email": "john@example.com"
}
```

#### Update Record
```bash
PUT /api/models/hr.employee/1
Content-Type: application/json

{
    "work_phone": "+1234567890"
}
```

#### Delete Record
```bash
DELETE /api/models/hr.employee/1
```

### Frontend API Client

**`lib/api.ts`:**
```typescript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  withCredentials: true, // For session management
});

// Request interceptor for authentication
apiClient.interceptors.request.use((config) => {
  // Add auth headers if needed
  return config;
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

**`services/employeeService.ts`:**
```typescript
import apiClient from '@/lib/api';

export interface Employee {
  id: number;
  name: string;
  work_email: string;
  work_phone?: string;
}

export const employeeService = {
  async getEmployees() {
    const response = await apiClient.get('/models/hr.employee');
    return response.data.records as Employee[];
  },

  async getEmployee(id: number) {
    const response = await apiClient.get(`/models/hr.employee/${id}`);
    return response.data.record as Employee;
  },

  async createEmployee(employee: Omit<Employee, 'id'>) {
    const response = await apiClient.post('/models/hr.employee', employee);
    return response.data.record as Employee;
  },

  async updateEmployee(id: number, employee: Partial<Employee>) {
    const response = await apiClient.put(`/models/hr.employee/${id}`, employee);
    return response.data.record as Employee;
  },

  async deleteEmployee(id: number) {
    await apiClient.delete(`/models/hr.employee/${id}`);
  }
};
```

## Best Practices

### Module Development

#### Naming Conventions
- **Model names**: Use snake_case (e.g., `hr.employee`)
- **Field names**: Use snake_case (e.g., `work_email`)
- **Method names**: Use snake_case (e.g., `compute_total`)
- **XML IDs**: Use descriptive names (e.g., `employee_form_view`)

#### Code Organization
- **Separate concerns**: Keep models, views, and controllers separate
- **Reusable code**: Create utility functions for common operations
- **Error handling**: Implement proper error handling and logging

### Database Design

#### Field Types
```python
# Char fields
name = fields.Char(string='Name', size=100, required=True)

# Text fields
description = fields.Text(string='Description')

# Integer fields
count = fields.Integer(string='Count', default=0)

# Float fields
price = fields.Float(string='Price', digits=(10, 2))

# Boolean fields
active = fields.Boolean(string='Active', default=True)

# Date fields
date = fields.Date(string='Date')
start_date = fields.Datetime(string='Start Date')

# Selection fields
status = fields.Selection([
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed'),
    ('done', 'Done')
], string='Status', default='draft')

# Many2one fields
department_id = fields.Many2one('hr.department', string='Department')

# One2many fields
employee_ids = fields.One2many('hr.employee', 'department_id', string='Employees')

# Many2many fields
tag_ids = fields.Many2many('hr.employee.tag', string='Tags')
```

### Security

#### Access Rights
- **Public access**: For data accessible to all users
- **User access**: For authenticated users
- **Manager access**: For users with specific permissions
- **Admin access**: For system administrators

#### Record Rules
```xml
<record id="employee_department_rule" model="ir.rule">
    <field name="name">Employees in same department</field>
    <field name="model_id" ref="model_hr_employee"/>
    <field name="domain_force">[('department_id', 'in', user.employee_ids.department_id.ids)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

## Testing

### Unit Tests

**`tests/test_your_model.py`:**
```python
# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase

class TestYourModel(TransactionCase):

    def setUp(self):
        super(TestYourModel, self).setUp()
        self.model = self.env['your.model']

    def test_create_record(self):
        record = self.model.create({
            'name': 'Test Record',
            'description': 'Test Description'
        })
        self.assertEqual(record.name, 'Test Record')

    def test_compute_method(self):
        # Test your computed methods
        pass
```

### Integration Tests

**`tests/test_api_integration.py`:**
```python
# -*- coding: utf-8 -*-
import requests
from odoo.tests.common import HttpCase

class TestAPIIntegration(HttpCase):

    def test_api_endpoint(self):
        # Test your API endpoints
        response = self.url_open('/api/models/your.model')
        self.assertEqual(response.status_code, 200)
```

## Deployment

### Adding Module to Docker

1. **Copy module to backend/addons:**
   ```bash
   cp -r custom_module backend/addons/
   ```

2. **Update Dockerfile if needed:**
   ```dockerfile
   # Install additional Python packages if required
   RUN pip install additional-package
   ```

3. **Rebuild and restart:**
   ```bash
   docker-compose down
   docker-compose up --build
   ```

### Module Installation

1. **Access Odoo backend:** http://localhost:8069
2. **Go to Apps menu**
3. **Update Apps List**
4. **Search for your module**
5. **Install the module**

## Debugging

### Common Issues

#### Module Not Loading
- Check `__init__.py` files are properly importing
- Verify `__manifest__.py` syntax
- Check Odoo logs for import errors

#### API Not Working
- Verify `base_rest_api` module is installed
- Check API endpoint URLs
- Verify authentication/session management

#### Frontend Issues
- Check browser console for errors
- Verify API URL configuration
- Check CORS settings

### Logging

**Enable debug logging in Odoo:**
```python
import logging
_logger = logging.getLogger(__name__)

# In your methods
_logger.info("Debug message")
_logger.error("Error message")
```

## Performance Optimization

### Database Optimization
- **Add database indexes** for frequently queried fields
- **Use proper field types** (e.g., Char vs Text)
- **Implement pagination** for large datasets

### API Optimization
- **Limit fields** in API responses
- **Implement caching** for frequently accessed data
- **Use database views** for complex queries

### Frontend Optimization
- **Implement lazy loading** for components
- **Use React.memo** for expensive components
- **Optimize bundle size** with code splitting

## Module Examples

### 📋 **Employee Management Module**

See the existing codebase for examples of:
- Model definitions with relationships
- API integration patterns
- Frontend components using shadcn/ui
- Form handling and validation

**Key Files:**
- `models/hr_employee.py` - Employee model with custom fields
- `views/employee_views.xml` - Form and tree views
- `security/ir.model.access.csv` - Access rights

### 🏭 **HR Custom Module Example**

Here's how to create a custom HR module:

#### **1. Manifest (`__manifest__.py`)**
```python
{
    'name': 'HR Custom Features',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'depends': ['hr', 'base_rest_api'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_custom_views.xml',
        'data/hr_custom_data.xml',
    ],
}
```

#### **2. Custom Model (`models/models.py`)**
```python
from odoo import models, fields, api

class HrCustomEmployee(models.Model):
    _name = 'hr.custom.employee'
    _inherit = 'hr.employee'

    # Custom fields
    emergency_contact = fields.Char(string='Emergency Contact')
    blood_type = fields.Selection([
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-')
    ], string='Blood Type')

    # Computed field
    age = fields.Integer(string='Age', compute='_compute_age')

    @api.depends('birthday')
    def _compute_age(self):
        for rec in self:
            if rec.birthday:
                rec.age = (fields.Date.today() - rec.birthday).days // 365
            else:
                rec.age = 0
```

#### **3. Views (`views/hr_custom_views.xml`)**
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="hr_custom_employee_form" model="ir.ui.view">
        <field name="name">hr.custom.employee.form</field>
        <field name="model">hr.employee</field>
        <field name="inherit_id" ref="hr.view_employee_form"/>
        <field name="arch" type="xml">
            <xpath expr="//field[@name='work_email']" position="after">
                <field name="emergency_contact"/>
                <field name="blood_type"/>
                <field name="age"/>
            </xpath>
        </field>
    </record>
</odoo>
```

#### **4. Security (`security/ir.model.access.csv`)**
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_hr_custom_employee,HR Custom Employee,model_hr_employee,hr.group_hr_manager,1,1,1,1
```

### 📊 **Custom Reports Module**

Example structure for report modules:
- Models for report data
- Controllers for report generation
- Views for report display
- Export functionality (PDF, Excel)

#### **Report Model Example**
```python
class HrReport(models.Model):
    _name = 'hr.custom.report'

    name = fields.Char(string='Report Name', required=True)
    date_from = fields.Date(string='From Date', required=True)
    date_to = fields.Date(string='To Date', required=True)
    report_data = fields.Text(string='Report Data')  # JSON data

    def generate_report(self):
        # Custom report generation logic
        employees = self.env['hr.employee'].search([
            ('create_date', '>=', self.date_from),
            ('create_date', '<=', self.date_to)
        ])

        # Process and store report data
        self.report_data = json.dumps({
            'total_employees': len(employees),
            'department_breakdown': self._get_department_stats(employees)
        })
```

### 🔌 **API Integration Example**

#### **Custom API Controller**
```python
class HrCustomController(http.Controller):

    @http.route('/api/hr/employees/stats', type='http', auth='user', methods=['GET'])
    def get_employee_stats(self):
        stats = {
            'total': len(self.env['hr.employee'].search([])),
            'active': len(self.env['hr.employee'].search([('active', '=', True)])),
            'departments': self._get_department_count()
        }
        return Response(json.dumps(stats), content_type='application/json')
```

### 🚀 **Module Installation Steps**

1. **Copy module to addons directory**
2. **Update module list in Odoo** (Developer mode → Apps → Update Apps List)
3. **Install the module** (Search and install)
4. **Configure access rights** (Settings → Users & Companies → Users)
5. **Test functionality** in the interface

### ✅ **Best Practices Summary**

- **Naming**: Use descriptive, lowercase names with underscores
- **Inheritance**: Prefer inheritance over replacement when possible
- **Security**: Always define proper access rights
- **Performance**: Use proper database indexing
- **Testing**: Write tests for custom business logic
- **Documentation**: Document complex features

## Support

For module development support:
- Check existing documentation
- Review similar modules in the codebase
- Ask questions in GitHub issues
- Join community discussions

## Contributing Modules

When contributing modules back to the project:
- Follow the contribution guidelines
- Include comprehensive documentation
- Add unit and integration tests
- Update this guide if needed