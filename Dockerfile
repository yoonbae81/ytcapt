# Use official Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install git only
RUN apt-get update && \
    apt-get install -y git --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy entrypoint script into container
COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

EXPOSE 8001

# Set entrypoint script
ENTRYPOINT ["/entrypoint.sh"]
