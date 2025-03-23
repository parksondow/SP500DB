[中文版 README](README.zh-TW.md)

# S&P 500 Stock Data Download Tool

This is a Python script used for downloading and managing historical data of S&P 500 component stocks.

## Features

- Automatically fetches the latest list of S&P 500 component stocks from Wikipedia
- Supports both incremental update and full re-download modes
- Saves data simultaneously as CSV files and SQLite database
- Built-in error handling and progress display

## Installation Requirements

```bash
pip install pandas
pip install yfinance
pip install requests
pip install beautifulsoup4
```

## Usage

1. Run the script:
   
   ```bash
   python.exe SP500_StkBase.py
   ```

2. Choose the update mode:
   
   - 1: Incremental update (from the last update date to today)
   - 2: Full re-download (from 2023 onwards)
   - 3: Exit the script

## Data Storage

- CSV files: Stored in the `Stk_data` directory
- SQLite database: `sp500_stock_data.db`

## Database Structure

The `stock_prices` table contains the following fields:

- ticker: Stock symbol
- date: Trading date
- open: Opening price
- high: Highest price
- low: Lowest price
- close: Closing price
- volume: Trading volume

## Notes

- The script automatically controls the API request frequency to avoid exceeding limits
- A full re-download will delete all existing data
- It is recommended to perform incremental updates regularly to keep the data up-to-date

## Author

[Parkson Dow]

## License

MIT License
