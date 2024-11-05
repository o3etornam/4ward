# Use a slim Python image
FROM python:3.10-slim

# Set up working directory
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy the pyproject.toml and poetry.lock files
COPY pyproject.toml poetry.lock ./

# Install dependencies without virtual environments
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Copy the rest of the app
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# Set PYTHONPATH and Start FastAPI
CMD ["sh", "-c", "PYTHONPATH=/app uvicorn main:app --host 0.0.0.0 --port 8000"]
