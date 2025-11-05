import os, sys

from yfinance import Ticker
# add MCP libs
from mcp.server.fastmcp import FastMCP
from loguru import logger

logger.add(sys.stderr, backtrace=True, diagnose=True, format="{time} {level} {message}", filter="my_module", level="INFO")
# create the server
mcp = FastMCP("YahooFinanceServer")

@mcp.tool()
def stock_price(ticker: str, period: str = "1mo", col: str = "Close") -> str:
    """
    Get the stock price for a given ticker symbol and period.
    :param ticker: The stock ticker symbol.
    :param period: The period for which to get the stock price (default is "1mo").
    :param col: The column to return (default is "Close").
    :return: The stock price as a string.
    """

    ticker = Ticker(ticker)
    data = ticker.history(period=period)
    if data.empty:
        logger.error(f"No data found for ticker '{ticker}'.")
        raise ValueError(f"No data found for ticker '{ticker}' with period '{period}'.")
    
    if col:
        if col not in data.columns:
            logger.error(f"Column '{col}' not found in the data.")
            raise ValueError(f"Column '{col}' not found in the data.")
        
        data = data[col]
        if data.empty:
            logger.error(f"No data found for column '{col}' in the ticker '{ticker}'.")
            raise ValueError(f"No data found for column '{col}' in the ticker '{ticker}'.")

    return str(f"Stock price for {ticker}: {data.to_list()}")


@mcp.tool()
def stock_info(ticker: str) -> str:
    """
    Get the stock info for a given ticker symbol.
    :param ticker: The stock ticker symbol.
    :return: The stock info as a string.
    """
    ticker = Ticker(ticker)
    data = ticker.info
    if not data:
        logger.error(f"No data found for ticker '{ticker}'.")
        raise ValueError(f"No data found for ticker '{ticker}'.")

    return str(f"Stock info for {ticker}: {data}")


@mcp.tool()
def income_statement(ticker: str) -> str:
    """
    Get the income statement for a given ticker symbol.
    :param ticker: The stock ticker symbol.
    :return: The income statement as a string.
    """
    ticker = Ticker(ticker)
    data = ticker.quarterly_income_stmt
    if data.empty:
        logger.error(f"No data found for ticker '{ticker}'.")
        raise ValueError(f"No data found for ticker '{ticker}'.")

    return str(f"Income statement for {ticker}: {data}")


if __name__ == "__main__":
    # start the server
    try:
        # mcp.start()
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        mcp.stop()
        logger.info("Server stopped by user.")
    except Exception as e:
        mcp.stop()
        logger.exception("An error occurred: {e}")
        raise e
