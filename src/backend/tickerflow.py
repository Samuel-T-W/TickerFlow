from .alpaca_utils import consume_stock_trade_data, DEFAULT_STOCK_LIST


def main():
    consume_stock_trade_data(DEFAULT_STOCK_LIST)
    print("subscribed to alpaca")


if __name__ == "__main__":
    main()