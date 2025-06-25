# 1. Use a minimal Python image
FROM python:3.11-slim

# 2. Set environment variables
ENV PYTHONUNBUFFERED=1 \
    FLASK_ENV=production

# 3. Set working directory
WORKDIR /app

# 4. Install system dependencies (only what's necessary)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# 5. Install Python packages
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 6. Copy project files
COPY . .

# 7. Expose app port
EXPOSE 5000

# 8. Launch app with Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
