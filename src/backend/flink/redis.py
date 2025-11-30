import redis
import logging
from datetime import datetime, timezone
import json


class RedisWriter:
    """
    A simple Redis writer class to store highest prices per stock symbol.
    """
    def __init__(self, redis_host='redis', redis_port=6379):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_client = None
    
    def open(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            logging.info(f"Successfully connected to Redis at {self.redis_host}:{self.redis_port}")
        except Exception as e:
            logging.error(f"Failed to connect to Redis: {e}")
            raise
    
    def write(self, key, data):
        """Write the highest price for a symbol to Redis, keyed by date."""
        if not self.redis_client:
            self.open()
        
        try:
            
            
            
            self.redis_client.set(key, json.dumps(data))
            logging.info(f"Stored in Redis - {key}: {data}")
            
        except Exception as e:
            logging.error(f"Error writing to Redis for symbol {data["symbol"]}: {e}")
    
    def close(self):
        """Close Redis connection."""
        if self.redis_client:
            self.redis_client.close()