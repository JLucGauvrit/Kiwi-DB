FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps needed by some packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy only what we need to leverage Docker cache
COPY requirements.txt /app/requirements.txt
RUN python3 -m pip install --upgrade pip setuptools wheel && \
    python3 -m pip install --no-cache-dir -r /app/requirements.txt

# Copy loader script and any other app files
COPY scripts /app/scripts

# Copy an entrypoint that waits for Mongo and runs the loader
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
