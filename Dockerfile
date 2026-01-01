FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for matplotlib (Agg backend)
# Only minimal dependencies needed since we use non-interactive backend
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY pyPlotShotMarker.py .
COPY targets.py .
COPY app.py .
COPY templates/ templates/
COPY static/ static/

# Create necessary directories
RUN mkdir -p static/uploads output

# Set environment variable for Flask port
ENV PORT=8099

# Expose Flask port
EXPOSE 8099

# Run Flask app
# CMD ["python", "app.py"]

# Use Gunicorn for production
CMD ["/usr/local/bin/gunicorn", "-w 4", "-b 0.0.0.0:8099", "app:app"]
