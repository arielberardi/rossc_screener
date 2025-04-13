import unittest
from unittest.mock import patch
import requests
import pandas

from rossc_screener.main import get_sp500_tickers
from rossc_screener.main import get_relative_volume
from rossc_screener.main import get_ticker_data
from rossc_screener.main import get_tickers_data
from rossc_screener.main import get_ticker_float
from rossc_screener.main import validate_rossc_condition


class TestMain(unittest.TestCase):
    def test_get_sp500_tickers(self):
        sp500 = get_sp500_tickers()
        self.assertFalse(sp500.empty)
        self.assertEqual(len(sp500), 503)
        self.assertEqual(sp500[0], "MMM")

    def test_relative_volume(self):
        volumes = pandas.Series([10, 15, 30, 25])

        self.assertEqual(get_relative_volume(volumes, 4), volumes.mean())
        self.assertEqual(get_relative_volume(volumes, 2), volumes.tail(2).mean())

        with self.assertRaises(Exception) as context:
            get_relative_volume(volumes, 10)
        self.assertEqual(
            str(context.exception),
            "Invalid window value, must be 0 < window < len(volume)",
        )

        with self.assertRaises(Exception) as context:
            get_relative_volume(volumes, 0)
        self.assertEqual(
            str(context.exception),
            "Invalid window value, must be 0 < window < len(volume)",
        )

    def test_get_ticker_data(self):
        data = get_ticker_data("AAPL")
        self.assertFalse(data.empty)
        self.assertEqual(len(data), 15)
        self.assertEqual(len(data.columns), 5)

    def test_get_tickers_data(self):
        data = get_tickers_data(["AAPL", "MSFT"])
        self.assertFalse(data.empty)
        self.assertEqual(len(data), 15)
        self.assertEqual(len(data.columns), 10)

    @patch("rossc_screener.main.requests.get")
    def test_get_ticker_float(self, mock_get):
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "symbol": "AAPL",
                "date": "2025-04-11 17:23:25",
                "freeFloat": 99.9086,
                "floatShares": 15008369800,
                "outstandingShares": 15022100000,
                "source": "https://www.sec.gov/Archives/edgar/data/320193/000032019324000123/aapl-20240928.htm",
            }
        ]
        mock_get.return_value = mock_response

        f = get_ticker_float("AAPL")
        self.assertEqual(f, 15008369800)

    def test_validate_rossc_condition_pass(self):
        floatShares = 100000
        priceData = pandas.DataFrame(
            {
                "Close": [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 8],
                "Volume": [
                    50,
                    50,
                    50,
                    50,
                    50,
                    50,
                    50,
                    50,
                    50,
                    50,
                    50,
                    50,
                    50,
                    50,
                    10000,
                ],
            }
        )

        self.assertTrue(validate_rossc_condition(priceData, floatShares))

    def test_validate_rossc_condition_1_fail(self):
        floatShares = 100000
        priceData = pandas.DataFrame(
            {
                "Close": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                "Volume": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            }
        )

        self.assertFalse(validate_rossc_condition(priceData, floatShares))

    def test_validate_rossc_condition_2_fail(self):
        floatShares = 100000
        priceData = pandas.DataFrame(
            {
                "Close": [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 8],
                "Volume": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 5],
            }
        )

        self.assertFalse(validate_rossc_condition(priceData, floatShares))

    def test_validate_rossc_condition_3_fail(self):
        floatShares = 100000
        priceData = pandas.DataFrame(
            {
                "Close": [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2.01],
                "Volume": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 10],
            }
        )

        self.assertFalse(validate_rossc_condition(priceData, floatShares))

    def test_validate_rossc_condition_4_fail(self):
        floatShares = 20000000
        priceData = pandas.DataFrame(
            {
                "Close": [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 8],
                "Volume": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 10],
            }
        )

        self.assertFalse(validate_rossc_condition(priceData, floatShares))


if __name__ == "__main__":
    unittest.main()
