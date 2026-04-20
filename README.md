# TickerFlow

A real-time stock price tracking system using Apache Kafka, Apache Flink, and Redis.

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Poetry (for local Python development)
- Python 3.12+
- Alpaca API credentials (sign up at [alpaca.markets](https://alpaca.markets))

### Setup

1. **Clone the repository**
   ```bash
   cd TickerFlow
   ```

2. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```env
   ALPACA_API_KEY=your_api_key
   ALPACA_API_SECRET=your_api_secret
   ```

3. **Install dependencies** (for local development)
   ```bash
   poetry install
   ```

4. **Start all services**
   ```bash
   docker-compose up -d --build
   ```

5. **Verify services are running**
   ```bash
   docker-compose ps
   ```

### Accessing Services

- **Flink Dashboard**: http://localhost:8081
- **Kafdrop (Kafka UI)**: http://localhost:19000
- **RedisInsight (Redis UI)**: http://localhost:5540

## Accessing Redis Data

**RedisInsight UI**: http://localhost:5540

First-time setup: Click "Add Redis Database" → Host: `redis`, Port: `6379`

### Daily Data Management

Data is organized by date. To clear old data:

```bash
# Clear all data except today's
poetry run python scripts/clear_old_redis_data.py

# Keep last 7 days
poetry run python scripts/clear_old_redis_data.py --days-to-keep 7
```

## Development

### Project Structure

```
TickerFlow/
├── src/
│   ├── backend/
│   │   ├── alpaca_utils.py      # Alpaca API integration
│   │   ├── tickerflow.py        # Main Kafka producer
│   │   └── flink/
│   │       └── highest_price.py # Flink job with Redis sink
│   └── frontend/                # (To be implemented)
├── scripts/
│   ├── test_alpaca_api.py       # Test Alpaca connection
│   └── clear_old_redis_data.py  # Clear old daily data from Redis
├── docker-compose.yml           # All services configuration
├── Dockerfile                   # Main app container
└── flink.Dockerfile             # Flink container
```

### Useful Commands

See [Commands.md](Commands.md) for a comprehensive list of commands.
