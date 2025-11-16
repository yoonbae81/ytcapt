# Use official Python 3.9 slim image
FROM python:3.9-slim

# Set working directory inside the container
WORKDIR /app

# Install git for cloning repository
RUN apt-get update && \
    apt-get install -y git --no-install-recommends && \
    apt-get clean

# Clone the GitHub repository into the working directory
RUN git clone https://github.com/yoonbae81/ytcapt.git .

# Install Python dependencies from requirements.txt in the root directory
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Default command to run the Bottle web app (located under src/)
EXPOSE 8080
CMD ["python", "src/app.py"]
