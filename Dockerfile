# Dockerfile for Screenshot Bug Detection Tool
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxss1 \
    libasound2 \
    libatspi2.0-0 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY screenshot_bug_detector.py .
COPY sudoku_test_automation.py .
COPY test_runner.py .
COPY config.json .

# Create necessary directories
RUN mkdir -p screenshots reference_images bug_reports

# Set permissions
RUN chmod +x screenshot_bug_detector.py sudoku_test_automation.py test_runner.py

# Create entrypoint script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Start Xvfb for headless operation\n\
Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &\n\
export DISPLAY=:99\n\
\n\
# Execute the command passed to the container\n\
exec "$@"' > /entrypoint.sh && chmod +x /entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Default command
CMD ["python", "test_runner.py", "--help"]