import yfinance as yf

def ticker_exists(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return 'regularMarketPrice' in info and info['regularMarketPrice'] is not None
    except Exception:
        return False

def get_stock_info(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        current_price = info.get('regularMarketPrice', 'N/A')
        day_high = info.get('dayHigh', 'N/A')
        day_low = info.get('dayLow', 'N/A')
        market_cap = info.get('marketCap', 'N/A')
        return current_price, day_high, day_low, market_cap, stock
    except Exception:
        return None, None, None, None, None
