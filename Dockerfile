# Use official Python 3.12 slim image (better performance than 3.9)
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install git and production dependencies
RUN apt-get update && \
    apt-get install -y git --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy entrypoint script into container
COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

# Set entrypoint script
ENTRYPOINT ["/entrypoint.sh"]
