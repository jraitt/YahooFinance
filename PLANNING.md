# Project Planning: YahooFinance Utilities

## 1. Project Goals

*   Provide a robust and easy-to-use Python package for interacting with Yahoo Finance data.
*   Offer functionalities for fetching current fund details, managing historical price data, and calculating various investment returns.
*   Ensure data accuracy and reliability by handling potential API errors and data inconsistencies.
*   Maintain a clean, well-documented, and testable codebase.

## 2. Architecture

*   **Core Module (`yf_utilities.py`)**: Contains all primary functions for data fetching, processing, and calculations.
*   **Data Storage**:
    *   Historical data will be stored in a CSV file (`data/historical_fund_data.csv`).
    *   The `data` directory will be created automatically if it doesn't exist.
*   **Modularity**: Functions are designed to be modular and reusable. Future enhancements might involve splitting `yf_utilities.py` if it grows too large (respecting the 500-line limit per file).
*   **Error Handling**: Functions should include try-except blocks to gracefully handle API request failures or data parsing issues, providing informative error messages.

## 3. Code Style & Conventions

*   **Language**: Python 3.6+
*   **Formatting**: PEP8, enforced by `black` (though not explicitly integrated into a CI/CD pipeline for this project yet).
*   **Type Hinting**: All function signatures and variables should include type hints.
*   **Docstrings**: Google style docstrings for all public functions and classes.
    ```python
    def example_function(param1: str, param2: int) -> bool:
        """Brief summary of the function.

        More detailed explanation if necessary.

        Args:
            param1 (str): Description of the first parameter.
            param2 (int): Description of the second parameter.

        Returns:
            bool: Description of the return value.
        """
        # Function logic here
        return True
    ```
*   **Imports**:
    *   Standard library imports first.
    *   Third-party library imports next.
    *   Local application/library specific imports last.
    *   Prefer relative imports within the `YahooFinance` package if sub-modules are created.
*   **Naming Conventions**:
    *   Modules: `lowercase_with_underscores.py`
    *   Functions: `lowercase_with_underscores()`
    *   Variables: `lowercase_with_underscores`
    *   Classes: `CapWords`
    *   Constants: `UPPERCASE_WITH_UNDERSCORES`
*   **Line Length**: Aim for a maximum of 79 characters for code and 72 for docstrings/comments, though `black` might reformat this.
*   **Comments**: Use inline comments (`# Reason: ...`) for non-obvious logic.

## 4. Data Validation

*   While `pydantic` is mentioned as a preferred tool for data validation in the custom instructions, its direct integration into the current `yf_utilities.py` might be overkill for the existing functions.
*   Input validation (e.g., checking if `tickers` is a list of strings) is currently handled implicitly or with basic checks.
*   For future enhancements, especially if handling more complex input structures or API responses, `pydantic` models should be considered.

## 5. Testing

*   **Framework**: Pytest.
*   **Location**: Tests should reside in a `/tests` directory, mirroring the main application structure (e.g., `tests/test_yf_utilities.py`).
*   **Coverage**: Aim for comprehensive test coverage, including:
    *   Happy path (expected use cases).
    *   Edge cases (e.g., empty ticker lists, single ticker, non-existent tickers).
    *   Failure cases (e.g., API errors, malformed data - mock these scenarios).
*   **Mocking**: Use `unittest.mock` or `pytest-mock` for external API calls (`yfinance`) to ensure tests are fast and reliable.

## 6. Dependencies

*   `yfinance`
*   `pandas`
*   `numpy`
*   (For testing): `pytest`, `pytest-mock`

Managed via `setup.py`.

## 7. Constraints & Considerations

*   **API Rate Limits**: Be mindful of Yahoo Finance API rate limits. Implement caching or delays if necessary, though `yfinance` handles some of this.
*   **Data Accuracy**: Yahoo Finance data can sometimes have inaccuracies or be delayed. The package should reflect the data as provided by the API.
*   **File Size Limit**: No single Python file should exceed 500 lines of code. Refactor into smaller modules if necessary.
*   **Extensibility**: Design functions and the overall structure to be extensible for future features (e.g., different types of financial data, more complex calculations).

## 8. Future Enhancements (Potential)

*   More sophisticated caching mechanisms for API responses.
*   Support for different data frequencies (e.g., intraday, weekly).
*   Additional financial calculations (e.g., Sharpe ratio, volatility).
*   Integration with plotting libraries for visualizations.
*   CLI interface for common operations.
