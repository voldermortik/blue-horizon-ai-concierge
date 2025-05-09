FROM python:3.12-slim

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Install system dependencies required for psycopg2 and other packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY --chown=user . .

# Install spacy model
RUN python -m spacy download en_core_web_sm

# Set environment variables
ENV PORT=8000
ENV HOST=0.0.0.0

# Expose the port
EXPOSE 8000

COPY --chown=user . /app
# Start the FastAPI application with the standard asyncio event loop
CMD ["uvicorn", "blue_horizon.app.api:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "asyncio"] 