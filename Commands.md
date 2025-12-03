# TickerFlow Commands

A collection of useful commands for running and testing the TickerFlow project.

## Running a Python File

To execute a Python file within the project's environment, use the following command:

poetry run python <path_to_file> Replace `<path_to_file>` with the actual path to the Python script you want to run.

## Running the Alpaca API Test Script

poetry run python scripts/test_alpaca_api.py


## running ticker flow backend python module (use -m so relative imports work)
poetry run python -m src.backend.tickerflow

# running docker (-d detached mode)
docker compose up -d --build

# shutting down docker 
docker compose down

# view logs for docker 
docker compose logs -f

# restarting only app after changes to src
docker compose restart app

## Redis Commands

# Access RedisInsight UI (Web interface for Redis)
# Open in browser: http://localhost:5540
# First time setup: Add database with host=redis, port=6379

# Clear old Redis data (keep only today's data)
poetry run python scripts/clear_old_redis_data.py

# Keep last 7 days of data
poetry run python scripts/clear_old_redis_data.py --days-to-keep 7

# Clear ALL data (use with caution!)
poetry run python scripts/clear_old_redis_data.py --clear-all