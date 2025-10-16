# MyTriv ERP Backend

## 🏗️ Overview

MyTriv ERP Backend is a comprehensive Enterprise Resource Planning system built on **Odoo 17 Community Edition** with custom modules and REST API capabilities. This backend provides a solid foundation for business management with modular architecture that supports both Community and Enterprise editions.

### 🏛️ Architecture

- **Framework**: Odoo 17.0 (Community Edition)
- **Database**: PostgreSQL 15
- **Containerization**: Docker & Docker Compose
- **Custom Modules**: CRM, Accounting, Project Management, Sales, HR, and REST API
- **API**: RESTful API endpoints for frontend integration

## 🚀 Quick Start

### Prerequisites

- **Docker** (latest version)
- **Docker Compose** (latest version)
- **Git** (for submodule management)

### Installation

1. **Clone the repository with submodules:**
   ```bash
   git clone --recursive https://github.com/your-username/mytriv-erp.git
   cd mytriv-erp/backend
   ```

2. **Run the automated setup:**
   ```bash
   ./setup_mytriv_erp.sh
   ```

   The setup script will:
   - Initialize Odoo 17 as a Git submodule
   - Build Docker containers
   - Start PostgreSQL and Odoo services
   - Display access information

3. **Access your ERP system:**
   - **Odoo Backend**: http://localhost:8069
   - **Database**: localhost:5432
   - **Default Admin**: Username: `admin`, Password: `admin`

## 📁 Directory Structure

```
backend/
├── addons/                          # Custom Odoo modules
│   ├── base_rest_api/              # REST API framework
│   ├── crm_custom/                 # Custom CRM functionality
│   ├── account_custom/             # Custom accounting features
│   ├── project_custom/             # Custom project management
│   ├── sale_custom/                # Custom sales enhancements
│   └── hr_custom/                  # Custom HR management
├── odoo/                           # Odoo 17 Community (Git submodule)
│   ├── addons/                     # Core Odoo modules
│   ├── odoo-bin                    # Odoo executable
│   └── requirements.txt            # Python dependencies
├── Dockerfile                      # Docker configuration
├── docker-compose.yml              # Container orchestration
├── odoo.conf                       # Odoo configuration
├── setup_mytriv_erp.sh             # Automated setup script
└── README.md                       # This file
```

## 🔧 Manual Setup (Alternative)

If you prefer manual setup or need more control:

### 1. Odoo Submodule Setup

```bash
# Add Odoo as submodule
git submodule add https://github.com/odoo/odoo.git odoo

# Initialize and checkout Odoo 17
git submodule update --init --recursive
cd odoo && git checkout 17.0 && cd ..
```

### 2. Docker Build and Run

```bash
# Build containers
docker compose build

# Start services
docker compose up -d

# View logs
docker compose logs -f
```

## ⚙️ Configuration

### Odoo Configuration (`odoo.conf`)

```ini
[options]
addons_path = /mnt/extra-addons,/opt/odoo/odoo/addons
admin_passwd = admin
db_host = db
db_port = 5432
db_user = odoo
db_password = odoo
logfile = /var/log/odoo/odoo.log
```

### Environment Variables

The following environment variables are configured in `docker-compose.yml`:

- `HOST`: Database hostname (`db`)
- `USER`: Database username (`odoo`)
- `PASSWORD`: Database password (`odoo`)
- `DATABASE`: Database name (`mytriv_erp`)

## 🛠️ Development

### Useful Docker Commands

```bash
# View running containers
docker compose ps

# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f odoo

# Stop all services
docker compose down

# Restart specific service
docker compose restart odoo

# Execute Odoo shell
docker compose exec odoo odoo shell

# Access container bash
docker compose exec odoo bash
```

### Custom Modules Development

All custom modules are located in the `addons/` directory:

- **`base_rest_api`**: Provides REST API framework for external integrations
- **`crm_custom`**: Enhanced CRM with custom lead management and analytics
- **`account_custom`**: Custom accounting features and journal entries
- **`project_custom`**: Project management with timesheets and task customization
- **`sale_custom`**: Enhanced sales orders and customer management
- **`hr_custom`**: HR management with attendance and employee customization

### Module Structure

Each custom module follows Odoo conventions:

```
module_name/
├── __init__.py              # Module initialization
├── __manifest__.py          # Module manifest
├── models/                  # Data models
│   ├── __init__.py
│   └── model_name.py
├── controllers/             # HTTP controllers (API endpoints)
│   ├── __init__.py
│   └── controller_name.py
├── views/                   # User interface views
├── security/                # Access rights and rules
└── data/                    # Demo data and configuration
```

## 🔌 API Integration

### REST API Endpoints

The backend exposes RESTful API endpoints through the `base_rest_api` module:

- **Base URL**: `http://localhost:8069/api`
- **Authentication**: API key or session-based
- **Formats**: JSON (default), XML

### Common API Patterns

```bash
# List records
GET /api/v1/module_name/

# Get specific record
GET /api/v1/module_name/{id}

# Create record
POST /api/v1/module_name/

# Update record
PUT /api/v1/module_name/{id}

# Delete record
DELETE /api/v1/module_name/{id}
```

## 🔒 Security & Permissions

### Access Control

- **Module Access**: Controlled via `ir.model.access.csv` files
- **Record Rules**: Domain-based access control
- **User Groups**: Role-based permissions

### Best Practices

- Always use HTTPS in production
- Implement proper authentication for API endpoints
- Regularly update Odoo and custom modules
- Use strong database passwords
- Implement proper backup strategies

## 🐛 Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check port usage
   lsof -i :8069
   lsof -i :5432

   # Stop conflicting services
   docker compose down
   ```

2. **Submodule Issues**
   ```bash
   # Reinitialize submodules
   git submodule update --init --recursive

   # Update submodule to latest
   git submodule update --remote
   ```

3. **Container Issues**
   ```bash
   # View container logs
   docker compose logs odoo

   # Restart containers
   docker compose restart

   # Rebuild containers
   docker compose build --no-cache
   ```

### Logs Location

- **Odoo Logs**: `/var/log/odoo/odoo.log` (inside container)
- **Docker Logs**: `docker compose logs -f`

## 🔄 Updates & Maintenance

### Updating Odoo

```bash
# Update Odoo submodule
cd odoo
git checkout 17.0
git pull origin 17.0
cd ..

# Update submodules
git submodule update --remote

# Rebuild containers
docker compose build
docker compose up -d
```

### Backup & Restore

```bash
# Database backup
docker compose exec db pg_dump -U odoo mytriv_erp > backup.sql

# Database restore
docker compose exec -T db psql -U odoo -d mytriv_erp < backup.sql
```

## 🌐 Compatibility

This project supports **Odoo 17 Community & Enterprise API standards**:

- ✅ **Odoo 17 Community Edition**: Full compatibility
- ✅ **Odoo 17 Enterprise Edition**: API compatibility maintained
- ✅ **REST API**: Compatible with modern frontend frameworks
- ✅ **PostgreSQL 15**: Optimized for performance

## 📞 Support

For issues and questions:

1. Check the troubleshooting section above
2. Review Docker container logs
3. Verify Odoo logs for detailed error messages
4. Ensure all prerequisites are properly installed

## 📄 License

This project is part of the MyTriv ERP system. See the main project LICENSE file for details.

---

**Happy ERP development! 🚀**