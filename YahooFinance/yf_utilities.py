import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from pandas.tseries.offsets import DateOffset


def fetch_fund_details(tickers: list[str]) -> pd.DataFrame:
    """
    Fetches key details for a list of funds and returns them as a Pandas DataFrame.

    Args:
        tickers (list[str]): A list of stock ticker symbols.

    Returns:
        pd.DataFrame: A DataFrame containing fund details, with 'Symbol' as the index.
                      Columns include: 'Price', 'P Close', 'D Ch', 'D Ch%',
                      '52 High', '52 Low', '50 Day', '200 Day', 'Yield', 'ER'.
                      Returns an empty DataFrame if fetching fails for all tickers.
    """
    fund_details_list = []
    for ticker in tickers:
        try:
            fund = yf.Ticker(ticker)
            info = fund.info
            fast_info = fund.fast_info

            details = {
                "Symbol": info.get("symbol"),
                "Name": info.get("shortName"),
                "Category": info.get("category"),
                "Type": info.get('quoteType'),
                "Price": info['regularMarketPrice'] if info.get('quoteType') == "MONEYMARKET" else round(fast_info['last_price'], 2),
                "P Close": info['regularMarketPrice'] if info.get('quoteType') == "MONEYMARKET" else round(fast_info['previousClose'], 2),
                "52 High": info.get('fiftyTwoWeekHigh', np.nan),
                "52 Low": info.get('fiftyTwoWeekLow', np.nan),
                "50 Day": info.get('fiftyDayAverage', np.nan),
                "200 Day": info.get('twoHundredDayAverage', np.nan),
                "Yield": info.get("yield"),
                "ER": info['netExpenseRatio']/100 if info.get('quoteType') in ["ETF", "MUTUALFUND"] else "N/A",
            }

            if details.get("Type") == "MONEYMARKET":
                details["Price"] = 1.00
                details["P Close"] = 1.00
                details["52 High"] = 1.00
                details["52 Low"] = 1.00
                details["50 Day"] = 1.00
                details["200 Day"] = 1.00
                details["ER"] = 0.011

            if details.get("Type") == "INDEX":
                details["Yield"] = "N/A"
                details["ER"] = "N/A"
            
            fund_details_list.append(details)

        except Exception as e:
            print(f"Error fetching details for {ticker}: {e}")
            # Continue to the next ticker even if one fails

    # Define expected columns for the DataFrame, even if empty
    expected_cols = ['Symbol', 'Name', 'Category', 'Type', 'Price', 'P Close', '52 High', '52 Low', '50 Day', '200 Day', 'Yield', 'ER']
    
    if not fund_details_list: # If list is empty, create an empty DataFrame with defined columns
        fund_details_df = pd.DataFrame(columns=expected_cols).set_index('Symbol')
    else:
        fund_details_df = pd.DataFrame(fund_details_list).set_index('Symbol')

    # Add custom calculation columns (these will be added only if DataFrame is not empty)
    if not fund_details_df.empty:
        fund_details_df['D Ch'] = fund_details_df['Price'] - fund_details_df['P Close']
        # Handle division by zero for D Ch%
        fund_details_df['D Ch%'] = (fund_details_df['Price'] / fund_details_df['P Close']) - 1 
    else:
        # If empty, ensure 'D Ch' and 'D Ch%' columns are added with appropriate dtype
        fund_details_df['D Ch'] = pd.Series(dtype='float64')
        fund_details_df['D Ch%'] = pd.Series(dtype='float64')

    return fund_details_df


DATA_DIR = "data"
HISTORICAL_DATA_FILE = "historical_fund_data.csv"

def _get_data_filepath() -> str:
    """
    Returns the full path to the historical data file, ensuring the data directory exists.
    """
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    return os.path.join(DATA_DIR, HISTORICAL_DATA_FILE)

def fetch_and_store_max_history(tickers: list[str]):
    """
    Fetches the maximum available historical data (Close price only) for a list of tickers
    and stores it in a CSV file in a wide format (Date, Ticker1_Close, Ticker2_Close, ...).

    Args:
        tickers (list[str]): A list of ticker symbols.
    """
    print(f"Fetching and storing max historical data (Close only) for: {tickers}")
    close_series = {} # Dictionary to hold 'Close' series for each ticker
    data_filepath = _get_data_filepath()

    for ticker in tickers:
        try:
            print(f"Fetching max data for {ticker}...")
            # Fetch data, auto_adjust=False keeps 'Close' and 'Adj Close' separate, we want 'Close'
            data = yf.download(ticker, period="max", auto_adjust=False)
            if not data.empty and 'Close' in data.columns:
                close_series[ticker] = data['Close'].squeeze() # Get the Close series
                print(f"Successfully fetched max data for {ticker}.")
            else:
                print(f"Fetched empty data or missing 'Close' for {ticker}.")
        except Exception as e:
            print(f"Error fetching max data for {ticker}: {e}")

    if close_series:
        # Combine all Close series into a single DataFrame, aligning by Date index
        all_close_data = pd.DataFrame(close_series)

        # Reset index to make Date a column
        all_close_data = all_close_data.reset_index().rename(columns={'index': 'Date'})

        # Ensure Date is datetime
        all_close_data['Date'] = pd.to_datetime(all_close_data['Date'])

        # Sort by Date for consistency
        all_close_data = all_close_data.sort_values(by=['Date'])

        try:
            all_close_data.to_csv(data_filepath, index=False)
            print(f"Successfully stored max historical data to {data_filepath}")
        except Exception as e:
            print(f"Error saving data to {data_filepath}: {e}")
    else:
        print("No data fetched for any ticker. Skipping save.")

def update_historical_data(tickers: list[str], force_update: bool = False):
    """
    Updates the historical data file with new data (Close price only) from the last stored date for each ticker.
    Loads existing data, fetches new data, combines them, and overwrites the file.

    Args:
        tickers (list[str]): A list of ticker symbols.
    """
    print(f"Updating historical data (Close only) for: {tickers}")
    data_filepath = _get_data_filepath()

    # Load existing data
    existing_data = load_historical_data(tickers) # Use the updated load function

    newly_fetched_close_series = {} # Dictionary to hold newly fetched 'Close' series

    for ticker in tickers:
        # Get the last date for this specific ticker from the existing data
        last_date = None
        if not existing_data.empty and ticker in existing_data.columns:
             # Find the last non-NaN date for this ticker
             last_date = existing_data.dropna(subset=[ticker])['Date'].max()


        if last_date:
            # Fetch data from the day after the last date
            start_date = last_date + timedelta(days=1)
            print(f"Fetching new data (Close only) for {ticker} from {start_date.strftime('%Y-%m-%d')} to today...")
            try:
                # Fetch data, auto_adjust=False keeps 'Close' and 'Adj Close' separate, we want 'Close'
                new_data = yf.download(ticker, start=start_date.strftime('%Y-%m-%d'), auto_adjust=False)
                if not new_data.empty and 'Close' in new_data.columns:
                    squeezed_data = new_data['Close'].squeeze()
                    if pd.api.types.is_scalar(squeezed_data):
                        # If squeeze returns a scalar, wrap it in a Series with the correct index
                        newly_fetched_close_series[ticker] = pd.Series([squeezed_data], index=[new_data.index[0]])
                    else:
                        newly_fetched_close_series[ticker] = squeezed_data # It's already a Series
                    print(f"Successfully fetched new data for {ticker}.")
                else:
                    print(f"No new data available for {ticker} since {last_date.strftime('%Y-%m-%d')}.")
            except Exception as e:
                print(f"Error fetching new data for {ticker}: {e}")
        else:
            # If no existing data for this ticker, fetch max history for it
            print(f"No existing data found for {ticker}. Fetching max history for this ticker.")
            try:
                 data = yf.download(ticker, period="max", auto_adjust=False)
                 if not data.empty and 'Close' in data.columns:
                      squeezed_data = data['Close'].squeeze()
                      if pd.api.types.is_scalar(squeezed_data):
                           # If squeeze returns a scalar, wrap it in a Series with the correct index
                           newly_fetched_close_series[ticker] = pd.Series([squeezed_data], index=[data.index[0]])
                      else:
                           newly_fetched_close_series[ticker] = squeezed_data # It's already a Series
                      print(f"Successfully fetched max data for {ticker}.")
                 else:
                      print(f"Fetched empty data or missing 'Close' for {ticker}.")
            except Exception as e:
                 print(f"Error fetching max data for {ticker}: {e}")


    if newly_fetched_close_series:
        # Combine all newly fetched Close series into a single DataFrame, aligning by Date index
        # Ensure all values in newly_fetched_close_series are Series before creating DataFrame
        series_dict = {k: (v if isinstance(v, pd.Series) else pd.Series([v])) for k, v in newly_fetched_close_series.items()}
        new_data_df = pd.DataFrame(series_dict)


        if not existing_data.empty:
            # Combine existing and new data
            # Set Date as index for combining
            existing_data = existing_data.set_index('Date')
            new_data_df.index = pd.to_datetime(new_data_df.index) # Ensure index is datetime for new data
            combined_data = new_data_df.combine_first(existing_data)
            combined_data = combined_data.reset_index().rename(columns={'index': 'Date'}) # Reset index back to column
        else:
            # If no existing data, the new data is the combined data
            combined_data = new_data_df.reset_index().rename(columns={'index': 'Date'}) # Reset index to make Date a column

        # Ensure Date is datetime and sort by Date
        combined_data['Date'] = pd.to_datetime(combined_data['Date'])
        combined_data = combined_data.sort_values(by=['Date'])

        # Ensure all original tickers are present as columns, even if no new data was fetched for them
        # Use the tickers list provided to the function for consistent column order
        column_order = ['Date'] + tickers
        combined_data = combined_data.reindex(columns=column_order)


        try:
            # Overwrite the entire file with the combined data
            combined_data.to_csv(data_filepath, index=False)
            print(f"Successfully updated historical data and saved to {data_filepath}")
        except Exception as e:
            print(f"Error saving updated data to {data_filepath}: {e}")
    else:
        print("No new data fetched for any ticker. Skipping update.")

def load_historical_data(tickers: list[str] = None) -> pd.DataFrame:
    """
    Loads historical data from the CSV file.

    Args:
        tickers (list[str], optional): A list of ticker symbols to filter by. If None, loads data for all tickers. Defaults to None.

    Returns:
        pd.DataFrame: DataFrame containing historical data, or an empty DataFrame if the file doesn't exist or is empty.
    """
    data_filepath = _get_data_filepath()
    if not os.path.exists(data_filepath):
        print(f"Historical data file not found at {data_filepath}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(data_filepath, parse_dates=['Date'])

        if df.empty:
            print("Historical data file is empty.")
            return pd.DataFrame()

        # The CSV is now in a wide format: Date, Ticker1, Ticker2, ...
        # We don't need to filter by ticker here, as all tickers are columns.
        # The 'tickers' argument can still be used by the caller to select specific columns if needed.

        # Ensure numeric columns (the ticker columns) are of the correct type
        # Use the provided tickers list to identify the numeric columns
        numeric_cols = tickers if tickers is not None else df.columns.tolist()
        # Exclude 'Date' from numeric conversion
        if 'Date' in numeric_cols:
            numeric_cols.remove('Date')

        for col in numeric_cols:
            if col in df.columns:
                # Use errors='coerce' to turn non-numeric values into NaN
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Drop rows where essential numeric data (any of the ticker columns if tickers were specified) could not be converted
        subset_cols_to_check = tickers if tickers is not None else df.columns.tolist()
        if 'Date' in subset_cols_to_check:
             subset_cols_to_check.remove('Date')
        # Ensure data is sorted by Date
        df = df.sort_values(by=['Date'])

        # Fill NaN values in ticker columns with 0.0
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].fillna(0.0)

        #print(df)
        return df

    except Exception as e:
        print(f"Error loading historical data from {data_filepath}: {e}")
        return pd.DataFrame()

def calculate_individual_fund_period_return(prices: pd.Series, period_label: str) -> float | None:
    """
    Calculates the percentage return for a single fund over a specified period.

    Args:
        prices (pd.Series): Series of historical close prices for a single fund (indexed by Date).
        period_label (str): The period label (e.g., "1mo", "1y", "max").

    Returns:
        float | None: The percentage return for the period, or None if data is insufficient.
    """
    if prices.empty:
        return None

    prices = prices.sort_index() # Ensure prices are sorted by date
    end_date = prices.index[-1]
    end_price = prices.iloc[-1]

    if period_label == "max":
        # Find the index of the first non-zero price
        first_non_zero_index = prices[prices != 0].first_valid_index()
        if first_non_zero_index is None:
            return None # No non-zero prices found

        start_price = prices.loc[first_non_zero_index]
        if start_price == 0:
            return None # Return None for division by zero, indicating N/A
        return (end_price / start_price) - 1
    elif period_label == "ytd":
        # Calculate Year-to-Date return
        end_year = end_date.year

        # Calculate Year-to-Date return using the last trading day of the previous year as the base
        start_of_current_year = pd.Timestamp(f'{end_year}-01-01')
        # Find the last trading day of the previous year
        previous_year_end_date_series = prices.loc[prices.index < start_of_current_year]

        if previous_year_end_date_series.empty:
            # If no data in the previous year, use the first available data point in the current year
            current_year_start_date_series = prices.loc[prices.index >= start_of_current_year]
            if current_year_start_date_series.empty:
                return None # No data points in the current year
            start_price = current_year_start_date_series.iloc[0]
        else:
            start_price = previous_year_end_date_series.iloc[-1]

        if start_price == 0:
            return None # Return None for division by zero, indicating N/A
        return (end_price / start_price) - 1

    else:
        offset = None
        if period_label == "1w":
            offset = DateOffset(weeks=1)
        elif period_label == "1mo":
            offset = DateOffset(months=1)
        elif period_label == "3mo":
            offset = DateOffset(months=3)
        elif period_label == "6mo":
            offset = DateOffset(months=6)
        elif period_label == "1y":
            offset = DateOffset(years=1)
        elif period_label == "2y":
            offset = DateOffset(years=2)
        elif period_label == "3y":
            offset = DateOffset(years=3)
        elif period_label == "5y":
            offset = DateOffset(years=5)
        elif period_label == "10y":
            offset = DateOffset(years=10)
        else:
            return None # Invalid period label

        target_start_date = end_date - offset

        # Find the closest trading day on or before the target_start_date
        start_date_series = prices.loc[prices.index <= target_start_date]

        if start_date_series.empty:
            return None # Not enough historical data for the period

        # Use the price from the trading day *before* the start of the period
        # If the target_start_date is the very first date, use that date's price
        if start_date_series.index[-1] == prices.index[0]:
             start_price = start_date_series.iloc[-1]
        else:
            # Find the index of the closest date on or before target_start_date
            closest_date_index = prices.index.get_loc(start_date_series.index[-1])
            # Get the price from the day before
            start_price = prices.iloc[closest_date_index - 1]

        if start_price == 0:
            return None # Return None for division by zero, indicating N/A
        return (end_price / start_price) - 1
    
def get_historical_returns(ticker_list: list[str]) -> pd.DataFrame:
    """
    Calculates historical returns for a list of tickers over predefined periods.

    This function loads historical data, processes it to calculate returns for
    various periods (1w, 1mo, 3mo, 6mo, ytd, 1y, 2y, 5y, 10y, max), and
    returns a DataFrame with tickers as the index and 'Inception' date as a column.

    Args:
        ticker_list (list[str]): A list of ticker symbols for which to calculate returns.

    Returns:
        pd.DataFrame: A DataFrame with 'Symbol' as the index, 'Inception' as a column,
                      and columns for each return period. Returns an empty DataFrame
                      if no historical data can be loaded or processed.
    """
    PERIODS = ["1w", "1mo", "3mo", "6mo", "ytd", "1y", "2y", "3y", "5y", "10y", "max"]
    expected_returns_cols = PERIODS + ['Inception']

    historical_data_df = load_historical_data(ticker_list)

    if historical_data_df.empty:
        print("No historical data loaded. Returning empty DataFrame with expected columns.")
        return pd.DataFrame(columns=expected_returns_cols).set_index(pd.Index([], name='Symbol'))

    # Set the 'Date' column as the index for calculations
    combined_data = historical_data_df.set_index('Date')

    # Prepare data for the returns table
    returns_data_for_df = {}
    fund_earliest_dates = {}

    for ticker in ticker_list:
        if ticker in combined_data.columns:
            fund_prices = combined_data[ticker]
            # Find the index of the first non-zero price
            first_non_zero_index = fund_prices[fund_prices != 0].first_valid_index()

            if first_non_zero_index is not None:
                earliest_date = fund_prices.index[fund_prices.index.get_loc(first_non_zero_index)]
                fund_earliest_dates[ticker] = earliest_date.strftime('%#m/%#d/%Y') # Format as M/D/YYYY
            else:
                fund_earliest_dates[ticker] = "N/A" # No non-zero prices found

            fund_returns_dict = {}
            for period in PERIODS:
                ret = calculate_individual_fund_period_return(combined_data[ticker], period)
                fund_returns_dict[period] = ret if ret is not None else "N/A"
            returns_data_for_df[ticker] = fund_returns_dict
        else:
            fund_earliest_dates[ticker] = "N/A"
            returns_data_for_df[ticker] = {period: "N/A" for period in PERIODS}

    # Create the returns DataFrame directly with tickers as index and periods as columns
    returns_df = pd.DataFrame.from_dict(returns_data_for_df, orient='index')
    returns_df.index.name = 'Symbol'
    
    # Add 'Inception' column using fund_earliest_dates
    returns_df['Inception'] = returns_df.index.map(fund_earliest_dates)
    
    # Ensure 'Inception' is the last column
    if 'Inception' in returns_df.columns:
        cols = [col for col in returns_df.columns if col != 'Inception'] + ['Inception']
        returns_df = returns_df[cols]
    
    return returns_df
    
if __name__ == '__main__':
    # Example Usage
    tickers = ["VTI", "VEA", "BND", "BNDX"]
    fund_details_df = fetch_fund_details(tickers)
    returns_df = get_historical_returns(tickers)
    print(fund_details_df)
    print(returns_df)
    

