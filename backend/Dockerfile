FROM odoo:17.0

# Switch to root user to install system dependencies
USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3-dev \
    build-essential \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Switch back to odoo user
USER odoo

# Copy custom addons
COPY ./addons /mnt/extra-addons

# Install Python dependencies for custom addons
RUN pip install --user requests

# Set environment variables
ENV ODOO_EXTRA_ADDONS=/mnt/extra-addons

# Enterprise Addons Configuration (DO NOT COPY enterprise code)
# To mount enterprise addons from host or docker-compose volume:
# VOLUME ["/mnt/enterprise-addons"]
# In docker-compose.yml, add volume mount:
# services:
#   odoo:
#     volumes:
#       - ./enterprise_addons:/mnt/enterprise-addons
# Or mount from host directory:
#       - /host/path/to/enterprise/modules:/mnt/enterprise-addons