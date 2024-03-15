# Use an official Python runtime as a parent image
FROM python:3.11-slim

COPY requirements.txt .

# Install Tesseract and other dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-spa \
        libtesseract-dev \
        poppler-utils \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    # pip install --no-cache-dir -r requirements.txt
    pip install --no-cache-dir -r requirements.txt

# Set the working directory in the container
WORKDIR .

# Copy the current directory contents into the container at /app
COPY . .

# Define environment variable
# ENV PATH="/app:${PATH}"

# # Run the Python script when the container launches
CMD ["python", "main.py"]
