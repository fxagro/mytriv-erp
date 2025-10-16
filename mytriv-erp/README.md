# 🧩 MyTriv ERP

<p align="center">
  <img src="https://img.shields.io/badge/Setup-One--Command-blue?style=for-the-badge&logo=gnubash" alt="One-Command Setup">
  <img src="https://github.com/fxagro/mytriv-erp/actions/workflows/ci.yml/badge.svg" alt="CI Pipeline">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Node.js-%3E%3D18.0.0-brightgreen.svg" alt="Node.js">
  <img src="https://img.shields.io/badge/Odoo-17.0-blue.svg" alt="Odoo">
  <img src="https://img.shields.io/badge/PostgreSQL-15.0-336791.svg" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED.svg" alt="Docker">
  <img src="https://img.shields.io/badge/TypeScript-Ready-3178C6.svg" alt="TypeScript">
  <img src="https://img.shields.io/badge/Next.js-15-black.svg" alt="Next.js">
</p>

<p align="center">
  <strong>Modern Full-Stack ERP Solution</strong><br>
  Combining <strong>Odoo 17</strong> backend power with <strong>Next.js 15</strong> React frontend.<br>
  Designed for <em>multi-industry</em> use cases with enterprise-grade scalability.
</p>

<div align="center">

[📖 Documentation](#-documentation) •
[🚀 Quick Start](#-quick-start) •
[🔧 Features](#-features) •
[🤝 Contributing](docs/CONTRIBUTING.md) •
[📚 Module Guide](docs/MODULE_GUIDE.md)

</div>

## ✨ Features

### 🎨 **Modern Frontend**
- ⚡ **Next.js 15** with App Router and Server Components
- 🔷 **TypeScript** for complete type safety
- 🎨 **TailwindCSS** + **shadcn/ui** for beautiful, accessible components
- 📱 **Responsive Design** with mobile-first approach
- 🌙 **Dark Mode** support out of the box

### 🔧 **Robust Backend**
- 🏢 **Odoo 17 Community** - World's most popular open-source ERP
- 🚀 **Custom REST API** module for seamless integration
- 🐍 **Python 3.11** with modern Odoo framework
- 📊 **PostgreSQL 15** for enterprise-grade data storage
- 🔒 **Enterprise Security** with role-based access control

### 🏗️ **Production Ready**
- 🐳 **Docker & Docker Compose** for easy deployment
- 🤖 **Automated Setup Script** for one-command installation
- ⚙️ **GitHub Actions** CI/CD pipeline
- 🚨 **Health Checks** and monitoring
- 📈 **Scalable Architecture** for enterprise growth
- 🔄 **Hot Reload** development environment

### 🔌 **API Integration**
- 📡 **RESTful API** endpoints for all Odoo models
- 🔍 **Advanced Filtering** and search capabilities
- 📤 **Real-time Updates** with automatic UI refresh
- 🛡️ **Error Handling** with user-friendly messages
- 📋 **CRUD Operations** for complete data management

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Automated Setup Details](#automated-setup-details)
- [Manual Setup Guide](#manual-setup-guide)
- [Prerequisites](#prerequisites)
- [Development](#development)
- [API Usage](#api-usage)
- [Deployment](#deployment)
- [CI/CD Pipeline](#cicd-pipeline)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [Documentation](#documentation)
- [License](#license)

## 🚀 Quick Start

Get MyTriv ERP up and running in **seconds** with one of these options:

### ⚡ One-Line Setup (Recommended)
```bash
curl -fsSL https://raw.githubusercontent.com/fxagro/mytriv-erp/main/setup_mytriv_erp.sh | bash
```

### 🤖 Interactive Setup Script
```bash
# Download the setup script
curl -fsSL https://raw.githubusercontent.com/fxagro/mytriv-erp/main/setup_mytriv_erp.sh -o setup_mytriv_erp.sh
chmod +x setup_mytriv_erp.sh
./setup_mytriv_erp.sh
```

### 📋 Manual Setup (Advanced Users)
```bash
git clone https://github.com/fxagro/mytriv-erp.git
cd mytriv-erp
cp .env.example .env
docker compose up -d
```

### 🌐 **Access Your ERP System**
| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | React/Next.js application |
| **Backend** | http://localhost:8069 | Odoo 17 ERP system |
| **Employee API** | http://localhost:8069/api/v1/employees | REST API endpoint |
| **Generic API** | http://localhost:8069/api | All Odoo models API |
| **Database** | localhost:5432 | PostgreSQL admin |

---

## 🤖 Automated Setup Details

The automated script handles the complete setup process:

### ✅ **What It Does**
- **Clones** repository and initializes Git
- **Validates** Docker and port availability
- **Builds** all containers with health checks
- **Starts** services and verifies they're running
- **Displays** access URLs and helpful commands

### 🎨 **Features**
- **Colored output** with progress indicators
- **Error handling** with cleanup and suggestions
- **Port conflict detection** for smooth installation
- **Pre-flight checks** for all dependencies
- **Automatic GitHub remote configuration**

### 📋 **Requirements**
- **Linux/macOS/WSL** (Windows supported via WSL)
- **Docker & Docker Compose**
- **Git** (for cloning and remote setup)
- **4GB+ RAM** and 10GB+ free disk space
- **Internet connection** (for GitHub operations)

---

## 📥 Manual Setup Guide

For developers who prefer manual control or are on Windows without WSL:

### 📥 **Step 1: Clone & Setup**

#### Option A: Automated Setup (Recommended)
```bash
# Download and run the automated setup script
curl -fsSL https://raw.githubusercontent.com/fxagro/mytriv-erp/main/setup_mytriv_erp.sh -o setup_mytriv_erp.sh
chmod +x setup_mytriv_erp.sh
./setup_mytriv_erp.sh
```

#### Option B: Manual Setup
```bash
git clone https://github.com/fxagro/mytriv-erp.git
cd mytriv-erp
cp .env.example .env
```

### 🐳 **Step 2: Start Services**
```bash
docker-compose up -d
```

### 🌐 **Step 3: Access Application**
| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | React application |
| **Backend** | http://localhost:8069 | Odoo ERP system |
| **Employee API** | http://localhost:8069/api/v1/employees | Employee REST API |
| **Generic API** | http://localhost:8069/api | Generic REST API endpoints |
| **Database** | localhost:5432 | PostgreSQL admin |

**That's it! 🎉** Your ERP system is ready!

### 🧪 **Test the API**
```bash
# Get all available models
curl http://localhost:8069/api/models

# Get employees using the dedicated API endpoint
curl http://localhost:8069/api/v1/employees

# Get employees using the generic API (alternative)
curl http://localhost:8069/api/models/hr.employee
```

## 📋 Prerequisites

Before running MyTriv ERP, ensure you have:

- **Docker & Docker Compose** (recommended)
- **Git** for version control
- **At least 4GB RAM** available
- **10GB free disk space** for databases and containers

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 4GB | 8GB |
| CPU | 2 cores | 4 cores |
| Storage | 10GB | 20GB |
| OS | Linux/Windows/macOS | Linux |

## 🔧 Installation

### Option 1: Docker Compose (Recommended)

1. **Clone and navigate:**
   ```bash
   git clone https://github.com/fxagro/mytriv-erp.git
   cd mytriv-erp
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env file with your settings
   ```

3. **Start services:**
   ```bash
   docker-compose up -d
   ```

4. **Verify installation:**
   ```bash
   # Check container status
   docker-compose ps

   # View logs
   docker-compose logs -f odoo
   ```

### Option 2: Manual Installation

#### Frontend Setup

```bash
cd frontend
npm install
npm run build
npm start
```

#### Backend Setup

```bash
cd backend
# Install Odoo dependencies
pip install -r requirements.txt

# Configure Odoo
cp odoo.conf.example odoo.conf
# Edit odoo.conf with your database settings

# Start Odoo
./odoo-bin -c odoo.conf
```

## 💻 Development

### Development Environment

1. **Start development services:**
   ```bash
   docker-compose -f docker-compose.dev.yml up
   ```

2. **Frontend development:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Backend development:**
   - Access Odoo at http://localhost:8069
   - Enable developer mode for advanced features

### Code Quality

- **Frontend**: ESLint, Prettier, TypeScript
- **Backend**: Python PEP 8, Odoo guidelines
- **Testing**: Jest (frontend), unittest (backend)

Run tests:
```bash
# Frontend tests
cd frontend && npm test

# Backend tests
cd backend && python -m pytest

# All tests
npm run test:all
```

## 🔌 API Usage

MyTriv ERP includes a comprehensive REST API for all Odoo models.

### Basic API Endpoints

```bash
# Get all models (generic API)
GET /api/models

# Get employees (dedicated API endpoint)
GET /api/v1/employees

# Get employees (generic API - alternative)
GET /api/models/hr.employee

# Get specific employee
GET /api/v1/employees/1
# OR
GET /api/models/hr.employee/1

# Create new employee
POST /api/v1/employees
{
  "name": "John Doe",
  "work_email": "john@example.com",
  "job_title": "Software Engineer",
  "work_phone": "+1234567890"
}

# Update employee
PUT /api/v1/employees/1
{
  "work_phone": "+1234567890"
}

# Delete employee
DELETE /api/v1/employees/1
```

### Frontend Integration Example

```typescript
import { employeeService } from '@/services/employeeService';

async function fetchEmployees() {
  try {
    const employees = await employeeService.getEmployees();
    console.log('Employees:', employees);
  } catch (error) {
    console.error('Error fetching employees:', error);
  }
}
```

## 🔄 CI/CD Pipeline

MyTriv ERP includes a comprehensive GitHub Actions workflow that runs on every push and pull request:

### ✅ **Automated Checks**
- **Lint & Validate** - YAML syntax and Docker Compose validation
- **Build & Test** - Container building and startup testing
- **Security Scan** - Vulnerability scanning with Trivy
- **Environment Check** - Required files and configuration validation
- **Notification** - Status reporting and PR comments

### 🔍 **Pipeline Features**
- **Multi-job parallel execution** for faster results
- **Security vulnerability reporting** in GitHub Security tab
- **Automatic PR commenting** with pipeline status
- **Comprehensive error reporting** with actionable feedback
- **Container health verification** before marking as successful

### 🚨 **Security Scanning**
The pipeline includes automated security scanning that:
- Scans all container images for vulnerabilities
- Reports HIGH and CRITICAL severity issues
- Generates SARIF reports for GitHub Security tab
- Provides actionable remediation suggestions

---

## 🚢 Deployment

### Production Deployment

1. **Environment setup:**
   ```bash
   cp .env.example .env.production
   # Configure production settings
   ```

2. **Build and deploy:**
   ```bash
   docker-compose -f docker-compose.production.yml up -d
   ```

3. **Health checks:**
   ```bash
   curl http://your-domain.com/api/v1/employees
   ```

### Environment Variables

Key environment variables for production:

```env
NODE_ENV=production
NEXT_PUBLIC_API_URL=https://your-api-domain.com/api
POSTGRES_PASSWORD=your-secure-password
ODOO_PASSWORD=your-odoo-master-password
```

## 📁 Project Structure

```
mytriv-erp/
├── frontend/              # Next.js 15 React application
│   ├── src/
│   │   ├── app/          # Next.js App Router pages
│   │   ├── components/   # Reusable UI components
│   │   └── lib/          # Utility functions
│   ├── Dockerfile        # Frontend container config
│   └── package.json      # Frontend dependencies
├── backend/              # Odoo 17 backend
│   ├── addons/          # Odoo modules
│   │   └── base_rest_api/ # REST API module
│   ├── Dockerfile       # Backend container config
│   └── requirements.txt # Python dependencies
├── docs/                # Documentation
│   ├── ARCHITECTURE.md  # System architecture
│   ├── CONTRIBUTING.md  # Contribution guidelines
│   └── MODULE_GUIDE.md  # Module development guide
├── .github/            # GitHub configuration
│   └── workflows/      # CI/CD pipelines
├── setup_mytriv_erp.sh # Automated setup script
├── docker-compose.yml  # Development environment
├── .env.example       # Environment configuration template
└── README.md          # This file
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING.md) for details.

### How to Contribute

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly
5. **Submit** a pull request

### Development Process

- Follow conventional commit messages
- Write tests for new features
- Update documentation as needed
- Ensure CI/CD checks pass

## 📚 Documentation

- **[Architecture Guide](docs/ARCHITECTURE.md)**: System design and architecture
- **[Module Development](docs/MODULE_GUIDE.md)**: Creating custom Odoo modules
- **[API Documentation](docs/API.md)**: Complete API reference
- **[Deployment Guide](docs/DEPLOYMENT.md)**: Production deployment instructions

## 🛠️ Tech Stack

### Frontend
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **TailwindCSS** - Utility-first CSS framework
- **shadcn/ui** - Modern UI components
- **Axios** - HTTP client for API calls

### Backend
- **Odoo 17** - Enterprise resource planning framework
- **Python 3.11** - Server-side programming
- **PostgreSQL 15** - Relational database
- **Werkzeug** - WSGI web framework

### DevOps
- **Docker** - Containerization platform
- **Docker Compose** - Multi-container orchestration
- **GitHub Actions** - CI/CD automation
- **Nginx** - Reverse proxy (production)

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Odoo Community** for the excellent ERP framework
- **Next.js Team** for the modern React framework
- **shadcn/ui** for beautiful and accessible UI components
- **Open Source Community** for continuous inspiration and support

## 📞 Support

### Getting Help

- **📖 Documentation**: Check our comprehensive docs
- **🐛 Issues**: Report bugs and request features
- **💬 Discussions**: Join community conversations
- **📧 Email**: Contact the maintainers

### Resources

- [Odoo Documentation](https://www.odoo.com/documentation)
- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [TailwindCSS Documentation](https://tailwindcss.com/docs)

## 🎯 Roadmap

### Upcoming Features

- [ ] **Mobile App**: React Native companion app
- [ ] **Advanced Analytics**: Business intelligence dashboard
- [ ] **Multi-tenancy**: Support for multiple organizations
- [ ] **API Rate Limiting**: Enhanced API security
- [ ] **Real-time Updates**: WebSocket integration
- [ ] **Advanced Reporting**: Custom report builder

### Version History

- **v1.0.0**: Initial release with core ERP functionality
- **v0.1.0**: Pre-release with basic setup and API

## 🌐 Repository

**🔗 GitHub:** `https://github.com/fxagro/mytriv-erp.git`

---

<div align="center">

## 🤝 Contributing

We welcome contributions from developers of all skill levels!

### 🚀 **Getting Started**
1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Submit** a pull request

### 📚 **Resources**
- 📖 **[Contribution Guide](docs/CONTRIBUTING.md)**
- 🏗️ **[Module Development](docs/MODULE_GUIDE.md)**
- 🏛️ **[Architecture Guide](docs/ARCHITECTURE.md)**

### 💬 **Community**
- 🐛 **[Report Issues](https://github.com/fxagro/mytriv-erp/issues)**
- 💭 **[Discussions](https://github.com/fxagro/mytriv-erp/discussions)**
- 📧 **Email:** [your-email@mytriv.com](mailto:contact@mytriv.com)

---

**⭐ Star us on GitHub • 🐛 Report Issues • 📖 Read Documentation**

**Built with ❤️ for modern businesses | MyTriv ERP - Open Source ERP Solution**

</div>