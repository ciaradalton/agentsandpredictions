FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=10000

# Set the working directory
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy dependency files first to leverage Docker caching
COPY pyproject.toml poetry.lock ./

# Configure Poetry to not create virtual environments
RUN poetry config virtualenvs.create false

# Now copy all necessary source files
COPY . .

# Install all dependencies including the current project
RUN poetry install --no-interaction --no-ansi

# Add the source directory to the Python path
ENV PYTHONPATH="${PYTHONPATH}:/app/src"

# Create a start script that explicitly uses PORT
RUN echo '#!/bin/bash\n\
export PORT="${PORT:-10000}"\n\
echo "Starting server on port $PORT"\n\
poetry run gunicorn \
    --bind "0.0.0.0:$PORT" \
    --workers 2 \
    --threads 4 \
    --timeout 120 \
    --graceful-timeout 120 \
    --keep-alive 5 \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    src.api:app' > /start.sh && chmod +x /start.sh

# Command to run the application
CMD ["/start.sh"]
