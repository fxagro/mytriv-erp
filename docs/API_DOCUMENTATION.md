# MyTriv ERP API Documentation

## Overview

MyTriv ERP provides a comprehensive REST API that allows external applications to interact with Odoo models. The API is built on top of the `base_rest_api` module and provides:

- **Generic Model API**: Access any Odoo model via standardized REST endpoints
- **Specific Module APIs**: Dedicated controllers for HR, CRM, and other modules
- **Authentication**: Session-based authentication with dedicated auth endpoints
- **Mock Mode**: Development mode with realistic mock data
- **Graceful Degradation**: Clear error messages when modules are unavailable

## Base URL

```
http://localhost:8069/api/v1
```

## Authentication

The API uses Odoo's built-in session-based authentication with dedicated auth endpoints.

### Login Process

#### Option 1: Use Dedicated Auth Endpoints (Recommended)

```bash
POST http://localhost:8069/api/v1/auth/login
Content-Type: application/json

{
  "login": "your-email@example.com",
  "password": "your-password",
  "db": "mytriv_erp"
}
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "name": "John Doe",
    "login": "user@example.com",
    "partner_id": 1,
    "company_id": 1,
    "company_name": "My Company"
  },
  "session_id": "session123...",
  "message": "Login successful",
  "success": true
}
```

#### Option 2: Use Odoo Web Login (Legacy)

```bash
POST http://localhost:8069/web/login
Content-Type: application/json

{
  "login": "your-email@example.com",
  "password": "your-password",
  "db": "mytriv_erp"
}
```

### Session Management

Use session cookies for subsequent API calls. The API automatically handles session management.

### Get Current User

```bash
GET http://localhost:8069/api/v1/auth/me
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "name": "John Doe",
    "login": "user@example.com",
    "partner_id": 1,
    "company_id": 1,
    "company_name": "My Company"
  },
  "session_id": "session123...",
  "authenticated": true
}
```

### Logout

```bash
POST http://localhost:8069/api/v1/auth/logout
```

## API Endpoints

### 🔐 Authentication Endpoints

#### POST /api/v1/auth/login
Authenticate user and create session.

**Request Body:**
```json
{
  "login": "user@example.com",
  "password": "password123",
  "db": "mytriv_erp"
}
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "name": "John Doe",
    "login": "user@example.com",
    "partner_id": 1,
    "company_id": 1,
    "company_name": "My Company"
  },
  "session_id": "session123...",
  "message": "Login successful",
  "success": true
}
```

#### POST /api/v1/auth/logout
Logout user and destroy session.

**Response:**
```json
{
  "message": "Logout successful",
  "success": true
}
```

#### GET /api/v1/auth/me
Get current authenticated user information.

**Response:**
```json
{
  "user": {
    "id": 1,
    "name": "John Doe",
    "login": "user@example.com",
    "partner_id": 1,
    "company_id": 1,
    "company_name": "My Company"
  },
  "session_id": "session123...",
  "authenticated": true
}
```

### 👥 HR Module Endpoints

#### GET /api/v1/hr/employees
List HR employees with pagination and search support.

**Query Parameters:**
- `limit`: Number of records (default: 50, max: 1000)
- `offset`: Records to skip (default: 0)
- `search`: Text search across employee name fields
- `department_id`: Filter by department ID
- `active`: Filter by active status (true/false)

**Example:**
```bash
GET /api/v1/hr/employees?limit=10&search=john&department_id=1
```

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "John Doe",
      "job_title": "Software Engineer",
      "work_email": "john@example.com",
      "work_phone": "+1234567890",
      "department_id": [1, "Engineering"],
      "active": true
    }
  ],
  "total": 100,
  "limit": 10,
  "offset": 0,
  "model": "hr.employee",
  "endpoint": "hr/employees"
}
```

#### GET /api/v1/hr/employees/{id}
Get specific employee by ID.

#### POST /api/v1/hr/employees
Create new employee.

**Request Body:**
```json
{
  "name": "Alice Johnson",
  "job_title": "Product Manager",
  "work_email": "alice@example.com",
  "department_id": 1,
  "active": true
}
```

#### PUT /api/v1/hr/employees/{id}
Update existing employee.

#### DELETE /api/v1/hr/employees/{id}
Delete employee.

**HR Module Not Available Response:**
```json
{
  "error": "HR module not available. Model \"hr.employee\" not found.",
  "module": "hr",
  "available_modules": ["crm", "sale", "account", "project", "stock"],
  "success": false
}
```

### 🎯 CRM Module Endpoints

#### GET /api/v1/crm/leads
List CRM leads with pagination and filtering.

**Query Parameters:**
- `limit`: Number of records (default: 50, max: 1000)
- `offset`: Records to skip (default: 0)
- `search`: Text search across lead fields
- `stage_id`: Filter by stage ID
- `user_id`: Filter by assigned user ID
- `priority`: Filter by priority (0-3)
- `type`: Filter by type (lead/opportunity)

**Example:**
```bash
GET /api/v1/crm/leads?limit=20&priority=3&type=opportunity
```

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Potential Client",
      "partner_name": "ABC Company",
      "email_from": "contact@abc.com",
      "stage_id": [1, "New"],
      "expected_revenue": 50000,
      "priority": 3,
      "type": "opportunity"
    }
  ],
  "total": 50,
  "limit": 20,
  "offset": 0,
  "model": "crm.lead",
  "endpoint": "crm/leads"
}
```

#### GET /api/v1/crm/leads/{id}
Get specific lead by ID.

#### POST /api/v1/crm/leads
Create new lead.

**Request Body:**
```json
{
  "name": "New Business Opportunity",
  "partner_name": "XYZ Corp",
  "email_from": "info@xyz.com",
  "expected_revenue": 75000,
  "stage_id": 1,
  "type": "lead"
}
```

#### PUT /api/v1/crm/leads/{id}
Update existing lead.

#### DELETE /api/v1/crm/leads/{id}
Delete lead.

### 📋 Generic Model Endpoints (All Odoo Models)

#### GET /api/v1/models/{model}
List records from any Odoo model with advanced features.

**Query Parameters:**
- `limit`: Number of records (default: 50, max: 1000)
- `offset`: Records to skip (default: 0)
- `search`: Text search across common name fields
- `domain`: JSON domain filter for advanced filtering
- `fields`: Comma-separated field list

**Examples:**

Get employees with pagination:
```bash
GET /api/v1/models/hr.employee?limit=10&offset=0
```

Search employees:
```bash
GET /api/v1/models/hr.employee?search=john&limit=20
```

Advanced domain filtering:
```bash
GET /api/v1/models/hr.employee?domain=[["active","=",true],[["department_id","!=",false]]]&fields=name,email,department_id
```

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "John Doe",
      "work_email": "john@example.com",
      "department_id": [1, "Engineering"]
    }
  ],
  "total": 1000,
  "limit": 50,
  "offset": 0,
  "model": "hr.employee"
}
```

#### GET /api/v1/models/{model}/{id}
Get a specific record by ID.

**Example:**
```bash
GET /api/v1/models/hr.employee/1?fields=name,email,department_id
```

#### POST /api/v1/models/{model}
Create a new record.

**Request Body:** JSON object with field values

**Example:**
```bash
POST /api/v1/models/hr.employee
Content-Type: application/json

{
  "name": "Bob Wilson",
  "work_email": "bob@example.com",
  "department_id": 1,
  "active": true
}
```

#### PUT /api/v1/models/{model}/{id}
Update an existing record.

#### DELETE /api/v1/models/{model}/{id}
Delete a record.

### 🌐 Generic API (All Odoo Models)

The generic API provides CRUD operations for any Odoo model.

#### List Records
```http
GET /api/models/{model}
```

**Parameters:**
- `limit` (optional): Number of records to return (default: 100)
- `offset` (optional): Number of records to skip (default: 0)
- `domain` (optional): Odoo domain filter as JSON array
- `fields` (optional): List of fields to return

**Examples:**

Get first 10 employees:
```http
GET /api/models/hr.employee?limit=10
```

Get employees with specific domain:
```http
GET /api/models/hr.employee?domain=[["active","=",true]]&fields=["name","work_email"]
```

**Response:**
```json
{
  "model": "hr.employee",
  "records": [
    {
      "id": 1,
      "name": "John Doe",
      "work_email": "john@example.com"
    }
  ],
  "count": 1
}
```

#### Get Specific Record
```http
GET /api/models/{model}/{id}
```

**Example:**
```http
GET /api/models/hr.employee/1
```

**Response:**
```json
{
  "model": "hr.employee",
  "record": {
    "id": 1,
    "name": "John Doe",
    "job_title": "Software Engineer",
    "work_email": "john@example.com",
    "work_phone": "+1234567890",
    "active": true
  }
}
```

#### Create Record
```http
POST /api/models/{model}
Content-Type: application/json
```

**Request Body:** Model fields as JSON object

**Example:**
```http
POST /api/models/hr.employee
Content-Type: application/json

{
  "name": "Bob Wilson",
  "work_email": "bob@example.com",
  "job_title": "Designer",
  "active": true
}
```

**Response:**
```json
{
  "model": "hr.employee",
  "record": {
    "id": 4,
    "name": "Bob Wilson",
    "work_email": "bob@example.com",
    "job_title": "Designer",
    "active": true
  },
  "id": 4
}
```

#### Update Record
```http
PUT /api/models/{model}/{id}
Content-Type: application/json
```

**Request Body:** Fields to update as JSON object

**Example:**
```http
PUT /api/models/hr.employee/1
Content-Type: application/json

{
  "work_phone": "+9998887777",
  "job_title": "Senior Software Engineer"
}
```

**Response:**
```json
{
  "model": "hr.employee",
  "record": {
    "id": 1,
    "name": "John Doe",
    "work_phone": "+9998887777",
    "job_title": "Senior Software Engineer"
  },
  "id": 1
}
```

#### Delete Record
```http
DELETE /api/models/{model}/{id}
```

**Example:**
```http
DELETE /api/models/hr.employee/4
```

**Response:**
```json
{
  "model": "hr.employee",
  "deleted_id": 4,
  "message": "Record deleted successfully"
}
```

## Available Models

### Get All Available Models
```http
GET /api/models
```

**Response:**
```json
{
  "models": [
    {
      "model": "hr.employee",
      "name": "Employee"
    },
    {
      "model": "hr.department",
      "name": "Department"
    },
    {
      "model": "res.users",
      "name": "Users"
    }
  ]
}
```

## Mock Mode

The API supports a mock mode for development when the Odoo backend is not available.

### Enable Mock Mode

Set the environment variable:
```bash
NEXT_PUBLIC_MOCK=1
```

Or use the mock-specific npm scripts:
```bash
npm run dev:mock    # Development with mock mode
npm run build:mock  # Build with mock mode
npm run start:mock  # Production with mock mode
```

### Mock Mode Features

- **Realistic Data**: Generates realistic mock data for all endpoints
- **Simulated Delays**: Adds realistic response delays (default: 500ms)
- **Error Simulation**: Optional random errors for testing (configurable)
- **Graceful Degradation**: Clear indicators when modules are not available

### Mock Mode Responses

When a module is not available in the backend, the API returns:
```json
{
  "error": "HR module not available. Model \"hr.employee\" not found.",
  "module": "hr",
  "available_modules": ["crm", "sale", "account", "project", "stock"],
  "success": false
}
```

## Frontend Integration

### Configuration

```typescript
// lib/config.ts
import { config } from '@/lib/config'

const apiConfig = {
  baseUrl: config.api.baseUrl,
  version: config.api.version,
  mock: {
    enabled: config.mock.enabled,
    delay: config.mock.delay,
  }
}
```

### API Client

```typescript
// services/apiClient.ts
import { apiClient } from '@/services/apiClient'

// Login
const response = await apiClient.login({
  login: 'user@example.com',
  password: 'password123'
})

// List employees
const employeesResponse = await apiClient.listEmployees({
  limit: 10,
  search: 'john'
})

// Create employee
const createResponse = await apiClient.createEmployee({
  name: 'Jane Smith',
  email: 'jane@example.com',
  department_id: 1
})
```

### Generic Model Service

```typescript
// services/genericModelService.ts
import { genericModelService } from '@/services/genericModelService'

// List any model
const response = await genericModelService.list('hr.employee', {
  limit: 20,
  search: 'john'
})

// Get specific record
const employee = await genericModelService.get('hr.employee', 1)

// Create record
const newEmployee = await genericModelService.create('hr.employee', {
  name: 'Bob Wilson',
  email: 'bob@example.com'
})
```

### HR Service

```typescript
// services/hrService.ts
import { hrService } from '@/services/hrService'

// List employees with HR-specific filters
const employees = await hrService.listEmployees({
  departmentId: 1,
  active: true,
  limit: 50
})

// Get employee statistics
const stats = await hrService.getEmployeeStats()

// Get employee hierarchy
const hierarchy = await hrService.getEmployeeHierarchy()
```

### CRM Service

```typescript
// services/crmService.ts
import { crmService } from '@/services/crmService'

// List leads with CRM-specific filters
const leads = await crmService.listLeads({
  stageId: 1,
  priority: 3,
  type: 'opportunity'
})

// Get lead statistics
const stats = await crmService.getLeadStats()

// Get leads pipeline
const pipeline = await crmService.getLeadsPipeline()
```

### UI Components

```typescript
// components/ui/card-stat.tsx
import { CardStat, CardStatGrid } from '@/components/ui/card-stat'

<CardStatGrid columns={4}>
  <CardStat
    title="Total Employees"
    value={employeeStats?.total || 0}
    subtitle={`${employeeStats?.active || 0} active`}
    trend={{
      value: 5.2,
      label: 'vs last month',
      direction: 'up'
    }}
  />
</CardStatGrid>

// components/ui/table.tsx
import { Table } from '@/components/ui/table'

<Table
  data={employees}
  columns={[
    { key: 'name', label: 'Name', sortable: true },
    { key: 'email', label: 'Email' },
    { key: 'department_id', label: 'Department' }
  ]}
  loading={loading}
  pagination={{
    total: 100,
    current: 1,
    pageSize: 10,
    onChange: (page, pageSize) => setPage(page)
  }}
  actions={[
    { label: 'Edit', onClick: handleEdit },
    { label: 'Delete', onClick: handleDelete, variant: 'danger' }
  ]}
/>

// components/ui/spinner.tsx
import { Spinner, PageSpinner, InlineSpinner } from '@/components/ui/spinner'

<Spinner size="lg" />
<PageSpinner message="Loading..." />
<InlineSpinner message="Saving..." />
```

### Employee Service

```typescript
// services/employeeService.ts
import apiClient from '@/lib/api';

export interface Employee {
  id: number;
  name: string;
  job_title?: string;
  work_email?: string;
  work_phone?: string;
  active: boolean;
}

export class EmployeeService {
  /**
   * Get all employees using the dedicated API
   */
  static async getEmployees(params?: {
    limit?: number;
    offset?: number;
    domain?: any[];
    fields?: string[];
  }): Promise<Employee[]> {
    try {
      const queryParams = new URLSearchParams();

      if (params?.limit) queryParams.append('limit', params.limit.toString());
      if (params?.offset) queryParams.append('offset', params.offset.toString());
      if (params?.domain) queryParams.append('domain', JSON.stringify(params.domain));
      if (params?.fields) queryParams.append('fields', JSON.stringify(params.fields));

      const response = await apiClient.get<Employee[]>(
        `/v1/employees?${queryParams.toString()}`
      );

      return response.data || [];
    } catch (error: any) {
      console.error('Error fetching employees:', error);
      throw new Error(error.response?.data?.error || 'Failed to fetch employees');
    }
  }

  /**
   * Create a new employee
   */
  static async createEmployee(employeeData: Omit<Employee, 'id'>): Promise<Employee> {
    try {
      const response = await apiClient.post<Employee>(
        '/v1/employees',
        employeeData
      );

      return response.data;
    } catch (error: any) {
      console.error('Error creating employee:', error);
      throw new Error(error.response?.data?.error || 'Failed to create employee');
    }
  }

  /**
   * Update an existing employee
   */
  static async updateEmployee(id: number, employeeData: Partial<Employee>): Promise<Employee> {
    try {
      const response = await apiClient.put<Employee>(
        `/v1/employees/${id}`,
        employeeData
      );

      return response.data;
    } catch (error: any) {
      console.error(`Error updating employee ${id}:`, error);
      throw new Error(error.response?.data?.error || 'Failed to update employee');
    }
  }

  /**
   * Delete an employee
   */
  static async deleteEmployee(id: number): Promise<void> {
    try {
      await apiClient.delete(`/v1/employees/${id}`);
    } catch (error: any) {
      console.error(`Error deleting employee ${id}:`, error);
      throw new Error(error.response?.data?.error || 'Failed to delete employee');
    }
  }
}
```

## Error Handling

### HTTP Status Codes

| Code | Description |
|------|-------------|
| `200` | Success |
| `201` | Created |
| `400` | Bad Request |
| `401` | Unauthorized |
| `404` | Not Found |
| `500` | Internal Server Error |

### Error Response Format

```json
{
  "error": "Error description message"
}
```

### Common Errors

#### 400 Bad Request
- Invalid JSON in request body
- Missing required fields
- Invalid field values

#### 401 Unauthorized
- Not logged in to Odoo
- Session expired
- Insufficient permissions

#### 404 Not Found
- Model does not exist
- Record does not exist
- Endpoint not found

#### 500 Internal Server Error
- Database connection issues
- Odoo server errors
- Unexpected exceptions

## Advanced Features

### Domain Filtering

Use Odoo domain syntax for advanced filtering:

```typescript
// Get active employees in specific department
const domain = [
  ['active', '=', true],
  ['department_id', '=', departmentId]
];

const employees = await EmployeeService.getEmployees({ domain });
```

### Field Selection

Specify which fields to return:

```typescript
// Get only name and email fields
const fields = ['name', 'work_email'];
const employees = await EmployeeService.getEmployees({ fields });
```

### Pagination

```typescript
// Get second page of results (10 per page)
const employees = await EmployeeService.getEmployees({
  limit: 10,
  offset: 10
});
```

## Rate Limiting

The API implements basic rate limiting to prevent abuse:
- Maximum 100 requests per minute per IP
- Burst limit of 20 requests per second

## CORS Configuration

The API supports Cross-Origin Resource Sharing for web applications:

```http
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Allow-Credentials: true
```

## Best Practices

### Frontend Integration

1. **Error Handling**: Always implement proper error handling
2. **Loading States**: Show loading indicators during API calls
3. **Optimistic Updates**: Update UI immediately for better UX
4. **Retry Logic**: Implement retry for failed requests
5. **Caching**: Cache frequently accessed data

### API Usage

1. **Batch Operations**: Use list endpoints for multiple records
2. **Field Selection**: Only request needed fields
3. **Domain Filtering**: Use server-side filtering when possible
4. **Pagination**: Implement pagination for large datasets
5. **Error Logging**: Log errors for debugging

## Examples

### Complete Employee Management Example

```typescript
// pages/employees.tsx
'use client';

import { useState, useEffect } from 'react';
import { EmployeeService, Employee } from '@/services/employeeService';

export default function EmployeesPage() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await EmployeeService.getEmployees({ limit: 20 });
      setEmployees(data);
    } catch (err: any) {
      console.error('Error fetching employees:', err);
      setError(err.message || 'Failed to fetch employees');
    } finally {
      setLoading(false);
    }
  };

  const createEmployee = async (employeeData: Omit<Employee, 'id'>) => {
    try {
      setError(null);
      const newEmployee = await EmployeeService.createEmployee(employeeData);
      setEmployees(prev => [...prev, newEmployee]);
      return newEmployee;
    } catch (err: any) {
      console.error('Error creating employee:', err);
      setError(err.message || 'Failed to create employee');
      throw err;
    }
  };

  if (loading) return <div>Loading employees...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h1>Employee Management</h1>
      {/* Employee list and forms */}
    </div>
  );
}
```

## Support

For API-related issues:
- Check the browser network tab for request/response details
- Verify Odoo session authentication
- Review Odoo server logs for backend errors
- Test endpoints with curl or Postman first

## API Versioning

Current API version: **v1**

Future versions will be available at:
- `/api/v2/` - Next major version
- `/api/v1/` - Current version (stable)

Breaking changes will be introduced in new major versions only.