# Gunakan base image Python resmi
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh project
COPY . .

# Expose port yang digunakan aplikasi
EXPOSE 5000

# Variabel environment untuk production
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Jalankan aplikasi menggunakan gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
