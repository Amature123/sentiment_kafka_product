# Use Python 3.11 as base image
FROM python:3.11

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    cron \
    && rm -rf /var/lib/apt/lists/*


# Copy Python requirements first
COPY requirements.txt .

# Install maturin first
RUN pip install --no-cache-dir maturin

# Install underthesea explicitly with version
RUN pip install --no-cache-dir underthesea==6.8.4
RUN pip install --no-cache-dir pytz
# Install other dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh


# Expose ports for FastAPI
EXPOSE 8000

