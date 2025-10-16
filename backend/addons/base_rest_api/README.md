# Base REST API

A flexible and secure REST API addon for MyTriv ERP that provides standardized endpoints for accessing Odoo models through HTTP requests.

## Features

- **Generic Model API**: Access any Odoo model via standardized REST endpoints
- **Specific Module APIs**: Dedicated controllers for HR and CRM modules
- **Authentication**: Session-based authentication with login/logout endpoints
- **Security**: Respects Odoo security model and user permissions
- **Pagination**: Built-in pagination support for large datasets
- **Search**: Text search across common name fields
- **Error Handling**: Comprehensive error responses with HTTP status codes
- **Graceful Degradation**: Returns clear messages when modules are not available

## Installation

1. Ensure the addon is properly installed in your Odoo instance
2. The addon depends on: `base`, `web`, `hr`
3. No additional configuration required - endpoints are available immediately

## API Endpoints

### Authentication Endpoints

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

### Generic Model Endpoints

#### GET /api/v1/models/{model}
List records from any Odoo model with pagination and search.

**Query Parameters:**
- `limit`: Number of records (default: 50, max: 1000)
- `offset`: Records to skip (default: 0)
- `search`: Text search across name fields
- `domain`: JSON domain filter
- `fields`: Comma-separated field list

**Example:**
```bash
GET /api/v1/models/hr.employee?limit=10&search=john&fields=name,email,department_id
```

**Response:**
```json
{
    "items": [
        {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "department_id": 1
        }
    ],
    "total": 100,
    "limit": 10,
    "offset": 0,
    "model": "hr.employee"
}
```

#### GET /api/v1/models/{model}/{id}
Get a specific record by ID.

**Example:**
```bash
GET /api/v1/models/hr.employee/1
```

#### POST /api/v1/models/{model}
Create a new record.

**Request Body:** JSON object with field values

**Example:**
```bash
POST /api/v1/models/hr.employee
Content-Type: application/json

{
    "name": "Jane Smith",
    "email": "jane@example.com",
    "department_id": 1
}
```

#### PUT /api/v1/models/{model}/{id}
Update an existing record.

#### DELETE /api/v1/models/{model}/{id}
Delete a record.

### HR Module Endpoints

#### GET /api/v1/hr/employees
List HR employees with HR-specific filtering.

**Query Parameters:**
- `department_id`: Filter by department
- `active`: Filter by active status (true/false)
- Standard pagination parameters

**Response:** Same format as generic endpoint but with HR-specific fields

#### GET /api/v1/hr/employees/{id}
Get specific employee.

#### POST /api/v1/hr/employees
Create new employee.

#### PUT /api/v1/hr/employees/{id}
Update employee.

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

### CRM Module Endpoints

#### GET /api/v1/crm/leads
List CRM leads with CRM-specific filtering.

**Query Parameters:**
- `stage_id`: Filter by stage
- `user_id`: Filter by assigned user
- `priority`: Filter by priority (0-3)
- `type`: Filter by type (lead/opportunity)
- Standard pagination parameters

#### GET /api/v1/crm/leads/{id}
Get specific lead.

#### POST /api/v1/crm/leads
Create new lead.

#### PUT /api/v1/crm/leads/{id}
Update lead.

#### DELETE /api/v1/crm/leads/{id}
Delete lead.

## Security

- All endpoints require authentication (`auth='user'`)
- Respects Odoo user permissions and access rights
- Uses `sudo()` only when necessary for models requiring elevated privileges
- Validates model existence before processing requests
- Comprehensive error logging for debugging

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `201`: Created
- `400`: Bad Request (invalid data)
- `401`: Unauthorized (authentication required)
- `404`: Not Found (resource or model not found)
- `500`: Internal Server Error

**Error Response Format:**
```json
{
    "error": "Error description",
    "success": false
}
```

## Usage Examples

### Using curl

```bash
# Login
curl -X POST http://localhost:8069/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login": "admin", "password": "admin", "db": "mytriv_erp"}'

# Get employees
curl -X GET "http://localhost:8069/api/v1/hr/employees?limit=5" \
  -H "Cookie: session_id=YOUR_SESSION_ID"

# Create employee
curl -X POST http://localhost:8069/api/v1/hr/employees \
  -H "Content-Type: application/json" \
  -H "Cookie: session_id=YOUR_SESSION_ID" \
  -d '{"name": "New Employee", "email": "new@example.com"}'

# Update employee
curl -X PUT http://localhost:8069/api/v1/hr/employees/1 \
  -H "Content-Type: application/json" \
  -H "Cookie: session_id=YOUR_SESSION_ID" \
  -d '{"name": "Updated Name"}'

# Delete employee
curl -X DELETE http://localhost:8069/api/v1/hr/employees/1 \
  -H "Cookie: session_id=YOUR_SESSION_ID"
```

### Using JavaScript/TypeScript

```typescript
// Login
const loginResponse = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    login: 'user@example.com',
    password: 'password123'
  })
});

// Get employees
const employeesResponse = await fetch('/api/v1/hr/employees?limit=10&search=john');
const employees = await employeesResponse.json();

// Create employee
const createResponse = await fetch('/api/v1/hr/employees', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'Jane Smith',
    email: 'jane@example.com'
  })
});
```

## Development

### Adding New Module Controllers

1. Create a new controller file in `controllers/`
2. Import it in `controllers/__init__.py`
3. Follow the pattern of existing controllers:
   - Check if model exists
   - Return 404 with clear message if not available
   - Use proper error handling and logging
   - Follow the response format

### Extending Generic API

The generic model API in `main.py` can be extended to support additional features like:
- Custom field filtering
- Advanced sorting options
- Bulk operations
- Export functionality

## Troubleshooting

### Common Issues

1. **"Model not found" errors**: Ensure the module is installed and the model exists
2. **Permission denied**: Check user has appropriate access rights in Odoo
3. **Session expired**: Re-authenticate using the login endpoint
4. **Invalid JSON**: Ensure request body is valid JSON

### Debugging

Enable debug logging in Odoo configuration to see detailed error messages:

```ini
[options]
log_level = debug
log_handler = odoo.addons.base_rest_api:DEBUG
```

## Contributing

When contributing to this addon:

1. Maintain backward compatibility
2. Add comprehensive error handling
3. Include proper logging
4. Update documentation for new features
5. Add unit tests for new functionality
6. Follow Odoo coding standards

## License

This addon is part of MyTriv ERP and follows the same license terms.