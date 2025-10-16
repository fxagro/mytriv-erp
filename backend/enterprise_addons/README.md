# Odoo Enterprise Addons

This directory is reserved for **Odoo Enterprise licensed modules only**.

## ⚠️ Important Security Notice

- **DO NOT commit Enterprise modules to public repositories**
- Enterprise modules contain proprietary Odoo code that must be kept private
- Only add Enterprise modules locally on systems with valid Odoo Enterprise licenses

## How to Add Enterprise Modules

### Option 1: Local Development
1. Obtain your licensed Enterprise modules from Odoo
2. Copy the module directories to this folder:
   ```bash
   # Example: Copy specific enterprise modules
   cp -r /path/to/enterprise/module_name backend/enterprise_addons/
   ```

### Option 2: Docker Compose Volume Mount
Add this volume mount to your `docker-compose.yml`:
```yaml
services:
  odoo:
    volumes:
      - ./enterprise_addons:/mnt/enterprise-addons
```

### Option 3: Host Directory Mount
Mount your Enterprise modules directory directly:
```yaml
services:
  odoo:
    volumes:
      - /host/path/to/enterprise/modules:/mnt/enterprise-addons
```

## Configuration

The `odoo.conf` file has been configured to include this path in `addons_path`:
```
addons_path = /mnt/extra-addons,/mnt/enterprise-addons,/opt/odoo/odoo/addons
```

Enterprise modules will be automatically loaded when Odoo starts, provided you have:
1. A valid Odoo Enterprise license
2. The Enterprise modules placed in this directory
3. Proper volume mounting in Docker (if using containers)

## Troubleshooting

- Ensure your Odoo Enterprise license is valid and active
- Check that Enterprise modules are compatible with your Odoo version
- Verify volume mounts are correctly configured in Docker
- Check Odoo logs for any module loading errors