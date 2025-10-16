# MyTriv ERP API Documentation

## Overview

MyTriv ERP provides a comprehensive REST API that allows external applications to interact with Odoo models. The API is built on top of the `base_rest_api` module and provides both generic endpoints for all Odoo models and specific endpoints for common operations.

## Base URL

```
http://localhost:8069/api
```

## Authentication

The API uses Odoo's built-in session-based authentication. You need to authenticate with Odoo first to access protected endpoints.

### Login Process

1. **Authenticate with Odoo:**
   ```bash
   POST http://localhost:8069/web/login
   Content-Type: application/json

   {
     "login": "your-email@example.com",
     "password": "your-password",
     "db": "mytriv_erp"
   }
   ```

2. **Use session cookies** for subsequent API calls

## API Endpoints

### 📋 Employee API (Specific Endpoints)

#### Get All Employees
```http
GET /api/v1/employees
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "job_title": "Software Engineer",
    "work_email": "john@example.com",
    "work_phone": "+1234567890",
    "active": true
  },
  {
    "id": 2,
    "name": "Jane Smith",
    "job_title": "HR Manager",
    "work_email": "jane@example.com",
    "work_phone": "+0987654321",
    "active": true
  }
]
```

#### Create Employee
```http
POST /api/v1/employees
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Alice Johnson",
  "job_title": "Product Manager",
  "work_email": "alice@example.com",
  "work_phone": "+1112223333",
  "active": true
}
```

**Response:**
```json
{
  "id": 3,
  "name": "Alice Johnson",
  "message": "Employee created successfully"
}
```

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

## Frontend Integration

### TypeScript API Client

```typescript
// lib/api.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8069/api',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.status, error.response?.data);
    if (error.response?.status === 401) {
      // Handle unauthorized access
      console.warn('Unauthorized access - redirecting to login');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
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