import pandas
import yfinance
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed


def get_sp500_tickers() -> pandas.DataFrame:
    sp = pandas.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    return sp[0]["Symbol"]


def get_relative_volume(volume: pandas.Series, window: int) -> float:
    if len(volume) < window or window <= 0:
        raise Exception("Invalid window value, must be 0 < window < len(volume)")

    if len(volume) == window:
        return volume.mean()

    return volume.tail(window).mean()


def get_ticker_data(
    ticker: str, days: int = 20, interval: str = "1d"
) -> pandas.DataFrame:
    start = datetime.now() - timedelta(days=days)
    end = datetime.now()

    data = yfinance.download(
        [ticker],
        start=start,
        end=end,
        auto_adjust=True,
        interval=interval,
    )

    return data.droplevel(1, axis=1)


def get_ticker_float(ticker: str) -> float:
    token = os.getenv("FMP_API_KEY")
    url = f"https://financialmodelingprep.com/stable/shares-float?symbol={ticker}&apikey={token}"
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200 or not data or "floatShares" not in data[0]:
        raise Exception(f"Failed to fetch data for ticker: {ticker}")

    return data[0].get("floatShares", 0)


def validate_rossc_condition(priceData: pandas.DataFrame, floatShares: float):
    # Price must be between $2 and $20
    if not 2 < priceData.tail()["Close"].mean() < 20:
        return False

    # Volume needs to be 5x the average volume for the last 14 days
    volume = priceData["Volume"]
    if volume.iloc[-1] < (get_relative_volume(volume, 14) * 5):
        return False

    # Price must be up 10% from the previous close
    last_pct_change = priceData["Close"].pct_change().iloc[-1]
    if last_pct_change < 0.1:
        return False

    # Float must be less than 20 million
    if floatShares >= 20000000:
        return False

    # TODO: Stock must have some news in the day or day before

    return True


def process_batch(tickers):
    result = []
    for ticker in tickers:
        try:
            priceData = get_ticker_data(ticker)
            floatShares = get_ticker_float(ticker)

            if validate_rossc_condition(priceData, floatShares) or 1:
                print(f"Found a match! for ticker: {ticker}")
                volume_change = priceData["Volume"].pct_change().iloc[-1] * 100
                price_change = priceData["Close"].pct_change().iloc[-1] * 100
                result.append(
                    {
                        "ticker": ticker,
                        "price": priceData["Close"].iloc[-1],
                        "price_change": price_change,
                        "volume": priceData["Volume"].iloc[-1],
                        "volume_change": volume_change,
                        "floatShares": floatShares,
                    }
                )
        except Exception as err:
            print(err)

    return result


def main():
    load_dotenv(dotenv_path=".env")

    tickers = get_sp500_tickers()
    filtered_tickers = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        batches = [tickers[i : i + 100] for i in range(0, len(tickers), 100)]
        futures = [executor.submit(process_batch, batch) for batch in batches]
        for future in as_completed(futures):
            filtered_tickers.extend(future.result())

    tickers_df = pandas.DataFrame(filtered_tickers)
    tickers_df = tickers_df.sort_values(
        by=["price_change", "volume_change"], ascending=[False, False]
    )
    print(tickers_df)


if __name__ == "__main__":
    main()
