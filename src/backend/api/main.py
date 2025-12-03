from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import redis
import json
import os
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo

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

def get_target_trading_date():
    try:
        et_tz = ZoneInfo("America/New_York")
        now = datetime.now(et_tz)
    except Exception as e:
        print(f"Error getting ET timezone: {e}. Falling back to UTC.")
        now = datetime.now(timezone.utc)
    
    # If weekend, go back to Friday
    if now.weekday() == 5: # Saturday
        return (now - timedelta(days=1)).date()
    if now.weekday() == 6: # Sunday
        return (now - timedelta(days=2)).date()
        
    # It's a weekday
    market_open = time(9, 30)
    # Ensure we compare time correctly even if fallback to UTC (logic might be slightly off for UTC but prevents crash)
    if now.time() < market_open:
        # Before market open, go to previous trading day
        if now.weekday() == 0: # Monday
            return (now - timedelta(days=3)).date() # Back to Friday
        return (now - timedelta(days=1)).date() # Back to Yesterday
        
    # After market open on a weekday
    return now.date()

def get_data_for_date(symbol: str, stat_type: str):
    if not redis_client:
        raise HTTPException(status_code=503, detail="Redis not available")

    target_date = get_target_trading_date()
    target_date_str = target_date.isoformat()
    
    key = f"{stat_type}:{target_date_str}:{symbol}"
    data = redis_client.get(key)
    
    if data:
        return json.loads(data)
        
    # Return empty structure with the target date so UI knows which date we are LOOKING for
    return {
        "symbol": symbol, 
        "value": None, 
        "trade_date": target_date_str,
        "error": "No data found for target date"
    }

@app.get("/api/latest/{symbol}")
async def get_latest_price(symbol: str):
    return get_data_for_date(symbol, "latest_trade")

@app.get("/api/lowest/{symbol}")
async def get_lowest_price(symbol: str):
    return get_data_for_date(symbol, "lowest_price")

@app.get("/api/highest/{symbol}")
async def get_highest_price(symbol: str):
    return get_data_for_date(symbol, "highest_price")
