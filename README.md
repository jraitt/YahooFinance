# YahooFinance Utilities

A custom Python package for fetching, processing, and analyzing financial data using the `yfinance` library. This package provides utilities to retrieve fund details, historical market data, and calculate investment returns.

## Features

*   **Fetch Fund Details**: Retrieve key information for a list of fund tickers, including price, previous close, 52-week high/low, moving averages, yield, and expense ratio.
*   **Historical Data Management**:
    *   Fetch and store maximum available historical closing prices for specified tickers.
    *   Update existing historical data with the latest daily closes.
    *   Load stored historical data for analysis.
*   **Return Calculations**:
    *   Calculate percentage returns for individual funds over various predefined periods (1w, 1mo, 3mo, 6mo, YTD, 1y, 2y, 3y, 5y, 10y, max).
    *   Generate a summary table of historical returns for multiple tickers.
*   **Data Storage**: Historical data is stored locally in a CSV file (`data/historical_fund_data.csv`) for efficient retrieval and updates.

## Installation

To install the `YahooFinance` package locally, navigate to the root directory of the project (where `setup.py` is located) and run:

```bash
pip install .
```

Ensure you have Python 3.6+ installed.

## Dependencies

The package relies on the following Python libraries:

*   `yfinance`: For fetching financial data from Yahoo Finance.
*   `pandas`: For data manipulation and analysis, primarily using DataFrames.
*   `numpy`: For numerical operations.

These dependencies will be automatically installed when you install the package using `pip`.

## Usage

Here's a basic example of how to use the `YahooFinance` utilities:

```python
from YahooFinance import yf_utilities

# Define a list of tickers
tickers = ["VTI", "VEA", "BND", "BNDX"]

# Fetch fund details
fund_details_df = yf_utilities.fetch_fund_details(tickers)
print("Fund Details:")
print(fund_details_df)

# Fetch and store maximum historical data (if not already done or to refresh)
# yf_utilities.fetch_and_store_max_history(tickers)

# Update historical data (recommended for daily updates)
yf_utilities.update_historical_data(tickers)

# Load historical data
historical_data = yf_utilities.load_historical_data(tickers)
print("\nLoaded Historical Data (tail):")
print(historical_data.tail())

# Get historical returns
returns_df = yf_utilities.get_historical_returns(tickers)
print("\nHistorical Returns:")
print(returns_df)
```

### Key Functions

*   `fetch_fund_details(tickers: list[str]) -> pd.DataFrame`:
    Fetches details for the given list of tickers.
*   `fetch_and_store_max_history(tickers: list[str])`:
    Downloads and saves the entire available closing price history for the tickers.
*   `update_historical_data(tickers: list[str])`:
    Updates the stored historical data with new entries since the last update.
*   `load_historical_data(tickers: list[str] = None) -> pd.DataFrame`:
    Loads the historical closing prices from the local CSV file.
*   `get_historical_returns(ticker_list: list[str]) -> pd.DataFrame`:
    Calculates and returns various period returns for the specified tickers.

## Data Storage

Historical market data fetched by this package is stored in a CSV file located at `data/historical_fund_data.csv` relative to your project's root directory. The `data` directory will be created automatically if it doesn't exist.

## Author

John Raitt

## License

This project is licensed under the MIT License. See the `LICENSE` file for details (if one is created, otherwise refer to `setup.py` for license information).

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for bugs, feature requests, or improvements.

When contributing, please ensure:
1.  Code follows PEP8 guidelines.
2.  Type hints are used.
3.  Docstrings are provided for new functions/classes (Google style).
4.  Unit tests are added for new features or significant changes.
