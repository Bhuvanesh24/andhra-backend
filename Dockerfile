# Use a lightweight Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /andhra-backend

# Install pipenv
RUN pip install --no-cache-dir pipenv

# Copy Pipfile and Pipfile.lock
COPY Pipfile Pipfile.lock /andhra-backend/

# Install dependencies
RUN pipenv install --system --deploy

# Copy project files
COPY . /andhra-backend/

# Expose ports
EXPOSE 8001  
EXPOSE 8000 

# Run both servers
CMD ["sh", "-c", "gunicorn -b 0.0.0.0:8001 fastAPI.main:app -k uvicorn.workers.UvicornWorker & python reservoir_management/manage.py runserver 0.0.0.0:8000"]
