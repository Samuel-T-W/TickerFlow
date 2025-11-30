# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Prevent Python from writing .pyc files and buffer stdout
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_NO_INTERACTION 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies, including the JDK for the 'pemja' package and build tools for C extensions
RUN apt-get update && apt-get install -y default-jdk build-essential && rm -rf /var/lib/apt/lists/*
# Set the JAVA_HOME environment variable so that 'pemja' can find it
ENV JAVA_HOME=/usr/lib/jvm/default-java

# Install poetry
RUN pip install poetry

# Copy dependency files, the README, and the application source code
COPY poetry.lock pyproject.toml README.md /app/
COPY ./src /app/src

# Install project dependencies (including the project itself)
RUN poetry install

# Set the entrypoint for the container
CMD ["poetry", "run", "python", "-m", "src.backend.tickerflow"]
