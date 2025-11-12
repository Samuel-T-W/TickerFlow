import os
import json
import time as time_module
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from alpaca.data.live import StockDataStream 
from alpaca.data.enums import DataFeed
from dotenv import load_dotenv
from datetime import datetime, time
from zoneinfo import ZoneInfo

# Load environment variables from .env file
load_dotenv()

# kafka args
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")

# Alpaca api args 
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
DEFAULT_STOCK_LIST = {"AAPL"}
TEST_STOCK_LIST = {"FAKEPACA"} # after hour stocks
TEST_URL = "wss://stream.data.alpaca.markets/v2/test"  # for streaming test market data during off hours 

# market time constants
NY_TIMEZONE = ZoneInfo("America/New_York")
MARKET_OPEN_HOUR = time(9, 30)
MARKET_CLOSE_HOUR = time(16, 0)

# Lazy-loaded Kafka producer
_PRODUCER = None

def get_producer():
    """Get or create Kafka producer with retry logic."""
    global _PRODUCER
    if _PRODUCER is None:
        max_retries = 5
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                _PRODUCER = KafkaProducer(
                    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                    value_serializer=lambda v: v.encode('utf-8')
                )
                print(f"Successfully connected to Kafka at {KAFKA_BOOTSTRAP_SERVERS}")
                break
            except NoBrokersAvailable:
                if attempt < max_retries - 1:
                    print(f"Kafka not available, retrying in {retry_delay}s... (attempt {attempt + 1}/{max_retries})")
                    time_module.sleep(retry_delay)
                else:
                    print("Failed to connect to Kafka after all retries")
                    raise
    return _PRODUCER


async def handle_trade(trade):
    """
    Prints trade event and send it to kafka
    """    
    # breakpoint()
    print("trade:", trade)
    
    # Access the raw dictionary data from the trade object and send to kafka
    trade_data = trade.json()
    producer = get_producer()
    producer.send("ticker_events", value=trade_data)

def is_market_open() -> bool:
    """
    Checks if the New York stock market is currently open.
    
    This function considers the time of day and the day of the week,
    but does not account for market holidays.
    
    Returns:
        bool: True if the market is open, False otherwise.
    """
    current_ny_datetime = datetime.now(NY_TIMEZONE)
    current_ny_time = current_ny_datetime.time()
    is_weekday = current_ny_datetime.weekday() < 5

    is_within_market_hours = MARKET_OPEN_HOUR <= current_ny_time < MARKET_CLOSE_HOUR
    
    return is_weekday and is_within_market_hours
    
    
def consume_stock_trade_data(stocks: list[str]):
    """
    Connects to the Alpaca data stream and subscribes to data for the given symbols.
    """

    stream = StockDataStream(
        api_key=ALPACA_API_KEY,
        secret_key=ALPACA_SECRET_KEY,
        url_override= "wss://stream.data.alpaca.markets/v2/test", # for streaming test market data during off hours 
        feed=DataFeed.IEX,
    )
    
    # TODO: test stock list should only work for dev 
    if is_market_open():
        stocks = DEFAULT_STOCK_LIST
    else:
        stocks = TEST_STOCK_LIST
    
    for symbol in stocks:
        stream.subscribe_trades(handle_trade, symbol)

    stream.run()