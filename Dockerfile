# 1. Pick a slim Python base
FROM python:3.11-slim

# 2. Avoid Python buffering, set Flask config
ENV PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    FLASK_APP=run.py

# 3. Create & switch to /app
WORKDIR /app

# 4. Install system deps & Python reqs
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip \
 && pip install -r requirements.txt
 
# 5. Copy your application code
COPY . .

# 6. Expose the port your Flask app listens on
EXPOSE 5000

# 7. Launch with Gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]