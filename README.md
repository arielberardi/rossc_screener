# Rossc Screener

Inspired by **Ross Cameron's** trading strategy (https://www.youtube.com/watch?v=5X_ZcifasBg), this simple stock screener identifies stocks that match his high-momentum, small-cap breakout criteria.

The screener looks for stocks that meet the following **5 characteristics**:

1. **Price between $2 and $20**  
2. **Relative volume at least 5x the 14-day average**  
3. **Already up at least 10% on the day**  
4. **Ideally has recent news**  
5. **Float of less than 20 million shares**

## How It Works

- Fetches real-time market data from **Yahoo! Finance**  
- Uses **Financial Modeling Prep (FMP)** API for float value
- Uses **Some Site In Here** API for fetching news related to stocks
- Runs in **multithreaded mode** for faster results  
- Filters and displays a list of tickers that meet the criteria, sorted by % price and volume change  

---

## Setup

**Requirements**: Python `3.12.9`

1. Install dependencies:

    `pip install -r requirements.txt`

2. Add your **API key** from [Financial Modeling Prep](https://site.financialmodelingprep.com/) to a `.env` file in the root:

   `FMP_API_KEY=your_api_key_here`

3. Run the screener:

   `python -m rossc_screener.main`