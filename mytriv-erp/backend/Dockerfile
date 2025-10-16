FROM odoo:17

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