# 1. Use official Python image
FROM python:3.11-slim

# 2. Set working directory
WORKDIR /app

# 3. Install system dependencies including PostgreSQL dev packages
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy requirements file first (for caching)
COPY requirements.txt .

# 5. Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of the code
COPY . .

# 7. Expose the port FastAPI will run on
EXPOSE 8000

# 8. Set environment variables (optional)
ENV PYTHONUNBUFFERED=1

# 9. Command to run FastAPI using uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]