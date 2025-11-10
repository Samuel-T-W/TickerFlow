import os
from typing import Set

from alpaca.data.live import StockDataStream 
from alpaca.data.enums import DataFeed
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

async def handle_quote(quote):
    print("quote:", quote)

async def handle_trade(trade):
    print("trade:", trade)

async def handle_bar(bar):
    print("bar:", bar)
    

def main():
    """
    Connects to the Alpaca data stream and subscribes to data for the given symbols.
    """

    stream = StockDataStream(
        api_key=ALPACA_API_KEY,
        secret_key=ALPACA_SECRET_KEY,
        url_override= "wss://stream.data.alpaca.markets/v2/test", # for streaming test market data during off hours 
        feed=DataFeed.IEX,
    )
    
    stocks = {"AAPL"}
    stocks = {"FAKEPACA"} # after hour stocks
    for symbol in stocks:
        # stream.subscribe_quotes(handle_quote, symbol)
        stream.subscribe_trades(handle_trade, symbol)
        # stream.subscribe_bars(handle_bar, symbol)

    stream.run()

if __name__ == "__main__":
    main()