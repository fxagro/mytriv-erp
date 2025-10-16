# MyTriv ERP Frontend

A modern, responsive frontend application for MyTriv ERP built with Next.js, TypeScript, and Tailwind CSS.

## Features

- **Modern Tech Stack**: Next.js 15, TypeScript, Tailwind CSS
- **Responsive Design**: Mobile-first responsive UI
- **Type Safety**: Full TypeScript coverage with comprehensive type definitions
- **Mock Mode**: Development without backend dependency
- **Modular Architecture**: Organized services and components
- **Authentication**: Session-based auth with Odoo integration
- **Real-time Updates**: Live data synchronization
- **Error Handling**: Comprehensive error boundaries and user feedback

## Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn
- Odoo 17 (optional, for production)

### Installation

1. **Clone and install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env.local
   ```

   Edit `.env.local`:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8069
   NEXT_PUBLIC_MOCK=1  # Enable for development without backend
   ```

3. **Start development server:**

   **With backend (Odoo running):**
   ```bash
   npm run dev
   ```

   **Mock mode (no backend required):**
   ```bash
   npm run dev:mock
   ```

4. **Open browser:**
   ```
   http://localhost:3000
   ```

## Development Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run dev:mock` | Start with mock mode enabled |
| `npm run build` | Build for production |
| `npm run build:mock` | Build with mock mode |
| `npm run start` | Start production server |
| `npm run start:mock` | Start production with mock mode |
| `npm run lint` | Run ESLint |
| `npm run type-check` | Run TypeScript type checking |

## Mock Mode

Mock mode allows development without a running Odoo backend. Enable it by:

1. **Environment variable:**
   ```env
   NEXT_PUBLIC_MOCK=1
   ```

2. **Using mock scripts:**
   ```bash
   npm run dev:mock
   npm run build:mock
   ```

### Mock Mode Features

- **Realistic Data**: Generates realistic sample data for all modules
- **Simulated API Delays**: Configurable response delays (default: 500ms)
- **Error Simulation**: Optional random errors for testing
- **Module Availability**: Simulates missing modules with clear messages
- **Authentication**: Mock login with any credentials

### Mock Mode Configuration

```typescript
// lib/config.ts
export const config = {
  mock: {
    enabled: process.env.NEXT_PUBLIC_MOCK === '1',
    delay: 500,        // Response delay in ms
    errorRate: 0,      // Random error rate (0-1)
  }
}
```

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── login/             # Authentication page
│   │   ├── dashboard/         # Main dashboard
│   │   ├── employees/         # HR employee management
│   │   ├── crm/leads/         # CRM leads management
│   │   └── ...
│   ├── components/            # Reusable UI components
│   │   └── ui/               # Base UI components
│   │       ├── button.tsx
│   │       ├── table.tsx
│   │       ├── modal.tsx
│   │       ├── card-stat.tsx
│   │       └── spinner.tsx
│   ├── lib/                  # Utilities and configuration
│   │   ├── config.ts        # Application configuration
│   │   ├── types.ts         # TypeScript type definitions
│   │   └── utils.ts         # Utility functions
│   ├── services/            # API services and business logic
│   │   ├── apiClient.ts     # HTTP client for Odoo API
│   │   ├── genericModelService.ts  # Generic CRUD operations
│   │   ├── hrService.ts     # HR-specific operations
│   │   ├── crmService.ts    # CRM-specific operations
│   │   └── ...
│   └── styles/              # Global styles
├── public/                  # Static assets
├── .env.example            # Environment configuration template
└── package.json            # Dependencies and scripts
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Odoo backend API URL | `http://localhost:8069` |
| `NEXT_PUBLIC_MOCK` | Enable mock mode | `0` |
| `NEXT_PUBLIC_AUTH_TYPE` | Authentication type | `cookie` |
| `NODE_ENV` | Environment | `development` |

### Application Configuration

```typescript
// lib/config.ts
export const config = {
  api: {
    baseUrl: process.env.NEXT_PUBLIC_API_URL,
    timeout: 30000,
    retry: { attempts: 3, delay: 1000 }
  },
  auth: {
    sessionCookieName: 'session_id',
    loginRedirect: '/dashboard',
    logoutRedirect: '/login'
  },
  pagination: {
    defaultLimit: 50,
    maxLimit: 1000
  }
}
```

## API Integration

### Authentication

```typescript
import { apiClient } from '@/services/apiClient'

// Login
const response = await apiClient.login({
  login: 'user@example.com',
  password: 'password123'
})

// Check authentication
const authStatus = await apiClient.checkAuth()
```

### Generic Model Operations

```typescript
import { genericModelService } from '@/services/genericModelService'

// List records
const employees = await genericModelService.list('hr.employee', {
  limit: 20,
  search: 'john'
})

// Get specific record
const employee = await genericModelService.get('hr.employee', 1)

// Create record
const newEmployee = await genericModelService.create('hr.employee', {
  name: 'Jane Doe',
  email: 'jane@example.com'
})
```

### HR Operations

```typescript
import { hrService } from '@/services/hrService'

// List employees with filters
const employees = await hrService.listEmployees({
  departmentId: 1,
  active: true,
  search: 'developer'
})

// Get employee statistics
const stats = await hrService.getEmployeeStats()
```

### CRM Operations

```typescript
import { crmService } from '@/services/crmService'

// List leads with filters
const leads = await crmService.listLeads({
  stageId: 1,
  priority: 3,
  type: 'opportunity'
})

// Get lead statistics
const stats = await crmService.getLeadStats()
```

## UI Components

### Table Component

```typescript
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
```

### Card Statistics

```typescript
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
```

### Modal Component

```typescript
import { Modal } from '@/components/ui/modal'

<Modal
  open={isOpen}
  onClose={() => setIsOpen(false)}
  title="Edit Employee"
  size="lg"
  footer={
    <div className="flex justify-end space-x-2">
      <button onClick={() => setIsOpen(false)}>Cancel</button>
      <button onClick={handleSave}>Save</button>
    </div>
  }
>
  <EmployeeForm />
</Modal>
```

## Development Guidelines

### Code Style

- Use TypeScript for all new code
- Follow ESLint configuration
- Use meaningful variable and function names
- Add JSDoc comments for public APIs
- Keep components small and focused

### Component Structure

```typescript
// ✅ Good: Small, focused component
interface ButtonProps {
  children: React.ReactNode
  onClick: () => void
  variant?: 'primary' | 'secondary'
}

export function Button({ children, onClick, variant = 'primary' }: ButtonProps) {
  return (
    <button
      className={cn(buttonStyles[variant])}
      onClick={onClick}
    >
      {children}
    </button>
  )
}

// ❌ Avoid: Large, complex component
export function ComplexComponent() {
  // 200+ lines of mixed concerns
}
```

### State Management

- Use React hooks for local state
- Keep state close to where it's used
- Use custom hooks for reusable logic
- Avoid prop drilling with context when appropriate

### Error Handling

```typescript
// ✅ Good: Proper error handling
const MyComponent = () => {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true)
        const result = await apiClient.getData()
        setData(result.data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [])

  if (error) return <ErrorMessage message={error} />
  if (loading) return <Spinner />
  return <DataDisplay data={data} />
}
```

## Deployment

### Build for Production

```bash
# Build without mock mode
npm run build

# Build with mock mode (for demo environments)
npm run build:mock
```

### Environment Setup

1. **Copy environment template:**
   ```bash
   cp .env.example .env.local
   ```

2. **Configure production environment:**
   ```env
   NEXT_PUBLIC_API_URL=https://your-odoo-server.com
   NEXT_PUBLIC_MOCK=0
   NODE_ENV=production
   ```

3. **Set up reverse proxy** (recommended):
   ```
   Frontend: https://erp.yourcompany.com
   Backend:  https://erp.yourcompany.com/api/*
   ```

### Docker Deployment

```bash
# Build image
npm run docker:build

# Run container
npm run docker:run
```

## Testing

### Running Tests

```bash
# Run test suite (when implemented)
npm test

# Run specific test file
npm test component-name.test.tsx
```

### Writing Tests

```typescript
// components/__tests__/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from '../Button'

describe('Button', () => {
  it('renders children correctly', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn()
    render(<Button onClick={handleClick}>Click me</Button>)

    fireEvent.click(screen.getByText('Click me'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })
})
```

## Troubleshooting

### Common Issues

1. **"Module not found" errors:**
   ```bash
   npm install
   # Clear Next.js cache
   rm -rf .next
   ```

2. **TypeScript errors:**
   ```bash
   npm run type-check
   # Fix type issues based on output
   ```

3. **Mock mode not working:**
   ```bash
   # Check environment variable
   echo $NEXT_PUBLIC_MOCK
   # Restart development server
   npm run dev:mock
   ```

4. **API connection issues:**
   ```bash
   # Check if Odoo is running
   curl http://localhost:8069/web/login
   # Verify API endpoints
   curl http://localhost:8069/api/v1/auth/me
   ```

### Debug Mode

Enable debug logging:

```env
NODE_ENV=development
# Enable detailed logging in browser console
```

### Performance Optimization

1. **Code splitting**: Components are automatically code-split by Next.js
2. **Image optimization**: Use Next.js `Image` component
3. **Bundle analysis**: Use `npm run build` to analyze bundle size
4. **Caching**: Implement proper caching strategies for API responses

## Contributing

### Development Workflow

1. **Create feature branch:**
   ```bash
   git checkout -b feature/new-component
   ```

2. **Make changes:**
   - Follow TypeScript and ESLint guidelines
   - Add tests for new functionality
   - Update documentation

3. **Test changes:**
   ```bash
   npm run type-check
   npm run lint
   ```

4. **Submit pull request:**
   - Describe changes clearly
   - Reference related issues
   - Ensure CI passes

### Code Standards

- **TypeScript**: Strict mode enabled
- **ESLint**: Follow provided configuration
- **Prettier**: Code formatting (run automatically)
- **Imports**: Use absolute imports with `@/` prefix
- **File naming**: `kebab-case` for files, `PascalCase` for components

## Support

### Getting Help

1. **Check documentation**: Review this README and API docs
2. **Search issues**: Look for similar problems in GitHub issues
3. **Create issue**: Report bugs or request features
4. **Contact team**: Reach out to development team

### Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Odoo API Documentation](../docs/API_DOCUMENTATION.md)

## License

This project is part of MyTriv ERP and follows the same license terms.

---

**Happy coding!** 🎉
