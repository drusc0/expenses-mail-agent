# Project Overview

This project is an AI-powered agent that provides real-time stock market data and financial information using Yahoo Finance. It leverages the `smolagents` framework for agent orchestration, `yfinance` for financial data, and `mcp` for tool/server management. The agent can answer questions about stock prices, company info, and income statements.

## Features

- **Stock Price Retrieval:** Get historical or recent prices for any stock ticker.
- **Company Info:** Retrieve detailed information about a company.
- **Income Statement:** Access quarterly income statements for a given ticker.
- **Agent-based Architecture:** Uses a language model agent to interact with the tools.
- **Extensible Tooling:** Easily add more financial tools or data sources.

## File Structure

- `main.py`: Defines the server and tools for stock data retrieval.
- `agent.py`: Sets up and runs the agent, connecting it to the tools in `main.py`.
- `requirements.txt`: Lists all dependencies.
- `README.md`: Project documentation (this file).

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd <repo-directory>
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Agent

The agent is designed to answer questions about stocks. To run the agent:

```bash
python agent.py
```

This will start the agent, which will internally launch the server defined in `main.py` and process a sample query (`"What is the stock price of WDAY?"`).

### Running the Server Directly

You can also run the server directly:

```bash
uv run mcp dev main.py
```

This will start the server in stdio mode, exposing the stock tools.

## Example Tools

- `stock_price(ticker, period="1mo", col="Close")`: Returns historical prices for a ticker.
- `stock_info(ticker)`: Returns company info.
- `income_statement(ticker)`: Returns the quarterly income statement.

## Dependencies

Key dependencies include:

- `yfinance`
- `smolagents`
- `mcp`
- `loguru`
- `pandas`
- `numpy`
- `litellm` (for LLM model integration)

See `requirements.txt` for the full list.

## Customization

- **Add More Tools:** Define new functions in `main.py` and decorate with `@mcp.tool()`.
- **Change Model:** Adjust the `LiteLLMModel` parameters in `agent.py` to use a different LLM.

## License

Specify your license here.
