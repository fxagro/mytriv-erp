# Contributing to MyTriv ERP

Thank you for your interest in contributing to MyTriv ERP! We welcome contributions from the community to help improve and grow this open-source ERP solution.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Standards](#code-standards)
- [Submitting Contributions](#submitting-contributions)
- [Reporting Issues](#reporting-issues)
- [Feature Requests](#feature-requests)

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Docker & Docker Compose** (for running the full stack)
- **Git** (for version control)
- **Node.js 18+** (for frontend development)
- **Python 3.11+** (for backend development)
- **PostgreSQL 15+** (for database development)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/mytriv-erp.git
   cd mytriv-erp
   ```

3. Add the upstream remote:
   ```bash
   git remote add upstream https://github.com/fxagro/mytriv-erp.git
   ```

## Development Setup

### Using Docker Compose (Recommended)

1. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit environment variables if needed:**
   ```bash
   nano .env  # or use your preferred editor
   ```

3. **Start all services:**
   ```bash
   docker-compose up -d
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend (Odoo): http://localhost:8069
   - Database: localhost:5432

### Manual Setup (Advanced)

#### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

#### Backend Setup

```bash
cd backend
# Install Odoo dependencies
pip install -r requirements.txt
# Start Odoo
./odoo-bin -c odoo.conf
```

## Code Standards

### General Guidelines

- **Write clear, readable code** with proper documentation
- **Follow existing code style** and conventions
- **Test your changes** thoroughly before submitting
- **Update documentation** when adding new features

### Frontend Standards

#### TypeScript/JavaScript
- Use **TypeScript** for all new code
- Follow **ESLint** and **Prettier** configurations
- Use **functional components** with hooks
- Implement **proper error handling**

#### React/Next.js
- Use **shadcn/ui components** for consistent UI
- Follow **Next.js App Router** conventions
- Implement **proper loading states** and error boundaries
- Use **React Query** for server state management

#### Styling
- Use **TailwindCSS** for styling
- Follow **BEM methodology** for custom CSS classes
- Ensure **responsive design** for all components

### Backend Standards

#### Python/Odoo
- Follow **PEP 8** style guidelines
- Use **Odoo development best practices**
- Write **proper docstrings** for all methods
- Implement **proper error handling** and logging

#### Database
- Use **Odoo ORM** methods for database operations
- Avoid **raw SQL queries** unless necessary
- Implement **proper database constraints** and indexes

## Submitting Contributions

### Contribution Process

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

2. **Make your changes** following code standards

3. **Test your changes:**
   ```bash
   # Run frontend tests
   cd frontend && npm test

   # Run backend tests
   cd backend && python -m pytest

   # Test with Docker
   docker-compose down
   docker-compose up --build
   ```

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Add: brief description of changes"
   ```

5. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request** on GitHub

### 📝 **Commit Message Guidelines**

Follow **Angular-style conventional commits**:

```
type(scope): description

[optional body]

[optional footer]
```

#### **Types:**
| Type | Description |
|------|-------------|
| `feat` | ✨ A new feature |
| `fix` | 🐛 A bug fix |
| `docs` | 📚 Documentation only changes |
| `style` | 💅 Code style changes (formatting, etc.) |
| `refactor` | 🔄 Code refactoring |
| `test` | ✅ Adding or updating tests |
| `chore` | 🔧 Maintenance tasks |
| `perf` | ⚡ Performance improvements |
| `ci` | 👷 CI/CD related changes |
| `build` | 🔨 Build system changes |

#### **Scope:**
- `frontend` - Frontend React/Next.js code
- `backend` - Backend Odoo/Python code
- `docs` - Documentation files
- `devops` - Docker, CI/CD, deployment
- `api` - API related changes

**Examples:**
```bash
feat(frontend): add employee dashboard component
fix(backend): resolve API authentication issue
docs: update API documentation
refactor(api): optimize employee search endpoint
test(frontend): add unit tests for employee service
ci: update GitHub Actions workflow
```

### Pull Request Guidelines

- **Clear title** describing the changes
- **Detailed description** of what was changed and why
- **Screenshots** for UI changes
- **Testing instructions** if applicable
- **Reference related issues** using #issue-number

## Reporting Issues

### Bug Reports

When reporting bugs, please include:

1. **Clear title** describing the issue
2. **Steps to reproduce** the issue
3. **Expected behavior**
4. **Actual behavior**
5. **Environment information** (OS, browser, versions)
6. **Error messages** and stack traces
7. **Screenshots** if applicable

### Issue Template

```markdown
## Description
[Brief description of the issue]

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Environment
- OS: [e.g., Windows 10]
- Browser: [e.g., Chrome 120]
- Node.js: [e.g., 18.17.0]
- Odoo: [e.g., 17.0]

## Additional Information
[Any additional context, screenshots, or related issues]
```

## Feature Requests

### Feature Request Template

```markdown
## Feature Description
[Clear description of the feature you'd like to see]

## Use Case
[Describe how this feature would be used]

## Proposed Solution
[If you have ideas on how to implement this feature]

## Alternatives Considered
[Any alternative solutions you've considered]

## Additional Information
[Any additional context or examples]
```

## Development Workflow

### Branch Strategy

- **`main`**: Production-ready code
- **`develop`**: Integration branch for features
- **`feature/*`**: New features
- **`fix/*`**: Bug fixes
- **`release/*`**: Release preparation

### Code Review Process

1. **Automated checks** run on all PRs
2. **At least one approval** required from maintainers
3. **All tests must pass** before merge
4. **No merge conflicts** with target branch

### Testing Requirements

#### Frontend Testing
- **Unit tests** for utilities and hooks
- **Integration tests** for API calls
- **E2E tests** for critical user flows
- **Accessibility tests** for UI components

#### Backend Testing
- **Unit tests** for model methods
- **Integration tests** for API endpoints
- **Database tests** for data operations

## Community Guidelines

### Code of Conduct

- Be **respectful** and **inclusive**
- Use **welcoming and inclusive language**
- Be **collaborative** and open to different viewpoints
- Focus on **constructive feedback**

### Getting Help

- **Check existing documentation** first
- **Search issues** for similar problems
- **Ask questions** in discussions or issues
- **Join our community** for real-time help

## Recognition

Contributors who make significant contributions may be:
- **Added to contributors list**
- **Given commit access** for trusted contributors
- **Invited to become maintainers**

## License

By contributing to MyTriv ERP, you agree that your contributions will be licensed under the same MIT License that covers the project.