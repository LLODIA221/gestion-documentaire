FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd --create-home --shell /bin/bash app

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY gestion_doc/ ./gestion_doc/

# Change ownership to app user
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Set working directory to Django project
WORKDIR /app/gestion_doc

# Create media directory
RUN mkdir -p media

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python manage.py check || exit 1

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"] 