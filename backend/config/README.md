# MyTriv ERP Docker Configuration

This directory contains the complete Docker containerization setup for MyTriv ERP backend (Odoo 17) and frontend (Next.js) with Nginx reverse proxy and PostgreSQL database.

## 📁 Directory Structure

```
backend/config/
├── docker-compose.yml      # Main Docker Compose configuration
├── Dockerfile.backend      # Odoo backend container definition
├── Dockerfile.frontend     # Next.js frontend container definition
├── nginx.conf             # Nginx reverse proxy configuration
├── odoo.conf             # Odoo configuration file
├── .env.example          # Environment variables template
├── supervisor.conf       # Process management configuration
└── README.md            # This file
```

## 🚀 Quick Start

### 1. Environment Setup

Copy the environment template and configure your variables:

```bash
cp .env.example .env
# Edit .env file with your preferred settings
```

### 2. Build and Start Containers

```bash
# Build all images
docker compose -f docker-compose.yml build

# Start all services
docker compose -f docker-compose.yml up -d

# View logs
docker compose -f docker-compose.yml logs -f

# Stop services
docker compose -f docker-compose.yml down
```

### 3. Access Your Application

- **Frontend**: http://localhost
- **Backend (Odoo)**: http://localhost:8069
- **API Gateway**: http://localhost/api
- **PostgreSQL**: localhost:5432

## 🔧 Services Overview

### PostgreSQL Database
- **Image**: postgres:15
- **Port**: 5432
- **Default Credentials**: odoo/odoo
- **Database**: mytriv_erp

### Odoo Backend
- **Base Image**: odoo:17.0
- **Port**: 8069
- **Custom Addons**: Mounted from `../addons/`
- **Configuration**: Uses odoo.conf

### Next.js Frontend
- **Base Image**: node:20-alpine
- **Port**: 3000
- **API URL**: Configured for http://localhost/api

### Nginx Reverse Proxy
- **Image**: nginx:latest
- **Port**: 80
- **Routes**:
  - `/api/*` → Odoo backend (port 8069)
  - `/*` → Next.js frontend (port 3000)

## ⚙️ Configuration Files

### Environment Variables (.env)

```bash
POSTGRES_USER=odoo          # Database username
POSTGRES_PASSWORD=odoo      # Database password
POSTGRES_DB=mytriv_erp      # Database name
ODOO_PORT=8069             # Odoo port
FRONTEND_PORT=3000         # Frontend port
NGINX_PORT=80              # Nginx port
```

### Odoo Configuration (odoo.conf)

Key settings:
- Database connection (host, port, user, password)
- HTTP server configuration
- Addons path configuration
- Security settings (proxy_mode, XML-RPC)
- Logging configuration

## 🔍 Troubleshooting

### Common Issues

1. **Port Conflicts**
   - Ensure ports 80, 3000, 5432, 8069 are available
   - Check if other services are using these ports

2. **Database Connection Issues**
   ```bash
   # Check database logs
   docker compose -f docker-compose.yml logs postgres

   # Test database connection
   docker compose -f docker-compose.yml exec postgres psql -U odoo -d mytriv_erp
   ```

3. **Odoo Addons Issues**
   - Verify addons are properly mounted
   - Check file permissions in the container
   - Review Odoo logs for specific errors

4. **Frontend Build Issues**
   ```bash
   # Check frontend logs
   docker compose -f docker-compose.yml logs frontend

   # Rebuild frontend container
   docker compose -f docker-compose.yml build frontend
   ```

### Useful Commands

```bash
# View all logs
docker compose -f docker-compose.yml logs -f

# View specific service logs
docker compose -f docker-compose.yml logs -f postgres
docker compose -f docker-compose.yml logs -f odoo
docker compose -f docker-compose.yml logs -f frontend
docker compose -f docker-compose.yml logs -f nginx

# Execute commands in containers
docker compose -f docker-compose.yml exec postgres psql -U odoo -d mytriv_erp
docker compose -f docker-compose.yml exec odoo bash

# Clean up (removes containers, networks, volumes)
docker compose -f docker-compose.yml down -v

# Rebuild specific service
docker compose -f docker-compose.yml build --no-cache odoo
```

## 🔒 Security Notes

- Change default database credentials in production
- Configure proper firewall rules
- Use SSL/TLS in production environments
- Regularly update container images
- Scan for vulnerabilities: `docker scan <image>`

## 📊 Monitoring

### Health Checks

The setup includes health checks for:
- PostgreSQL database connectivity
- Service dependencies

### Log Locations

- **Odoo logs**: `/var/log/odoo/` (inside container)
- **Nginx logs**: `/var/log/nginx/` (inside container)
- **Supervisor logs**: Configured in supervisor.conf

## 🚢 Production Deployment

For production deployment:

1. **Use environment-specific compose files**
2. **Configure proper secrets management**
3. **Set up SSL certificates**
4. **Configure firewall and security groups**
5. **Set up monitoring and alerting**
6. **Configure backup strategies**
7. **Use production-grade PostgreSQL configuration**

## 🤝 Support

For issues and questions:
1. Check the troubleshooting section
2. Review container logs
3. Verify configuration files
4. Check Docker and container status

## 📝 License

This Docker configuration is part of the MyTriv ERP project.