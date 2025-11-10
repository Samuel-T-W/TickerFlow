# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffer stdout
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_NO_INTERACTION 1

# Set the working directory in the container
WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy dependency definition files
COPY poetry.lock pyproject.toml /app/

# Install project dependencies (excluding dev dependencies)
RUN poetry install --no-root --no-dev

# Copy the rest of the application source code
COPY . /app/
