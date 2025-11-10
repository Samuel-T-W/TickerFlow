import os
from typing import Set
from unittest import TestProgram

from alpaca.data.live import StockDataStream 
from alpaca.data.enums import DataFeed
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
DEFAULT_STOCK_LIST = {"AAPL"}
TEST_STOCK_LIST = {"FAKEPACA"} # after hour stocks
TEST_URL = "wss://stream.data.alpaca.markets/v2/test"  # for streaming test market data during off hours 

async def handle_trade(trade):
    print("trade:", trade)
    
    
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
    
    stocks = TEST_STOCK_LIST
    
    for symbol in stocks:
        stream.subscribe_trades(handle_trade, symbol)

    stream.run()