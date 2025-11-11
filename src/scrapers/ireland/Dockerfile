# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your Python script into the container
COPY crawler.py .

# Create an output directory inside the container
RUN mkdir -p /output

# Set the command to run your script when the container starts
CMD ["python", "crawler.py"]
