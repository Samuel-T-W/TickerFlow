from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import redis
import json
import os

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
except Exception as e:
    print(f"Error connecting to Redis: {e}")
    redis_client = None

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

from datetime import datetime, timezone, timedelta

def get_data_with_fallback(symbol: str, stat_type: str):
    if not redis_client:
        raise HTTPException(status_code=503, detail="Redis not available")

    # Try today
    today = datetime.now(timezone.utc).date()
    today_str = today.isoformat()
    key_today = f"{stat_type}:{today_str}:{symbol}"
    data = redis_client.get(key_today)
    
    if data:
        return json.loads(data)
        
    # Try yesterday
    yesterday = today - timedelta(days=1)
    yesterday_str = yesterday.isoformat()
    key_yesterday = f"{stat_type}:{yesterday_str}:{symbol}"
    data = redis_client.get(key_yesterday)
    
    if data:
        return json.loads(data)
        
    return {"symbol": symbol, "price": None, "error": "No data found for today or yesterday"}

@app.get("/api/latest/{symbol}")
async def get_latest_price(symbol: str):
    return get_data_with_fallback(symbol, "latest_trade")

@app.get("/api/lowest/{symbol}")
async def get_lowest_price(symbol: str):
    return get_data_with_fallback(symbol, "lowest_price")

@app.get("/api/highest/{symbol}")
async def get_highest_price(symbol: str):
    return get_data_with_fallback(symbol, "highest_price")
