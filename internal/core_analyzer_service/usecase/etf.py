import os

from src.lib.database.postgres import Postgres
from src.lib.http.http import HTTP
from src.lib.logger.logger import logging
from src.services.core.thirdparty_api.alphavantage import AlphaVantage

API_KEY=os.getenv("ALPHAVANTAGE_DEV_API_KEY")

class ETF:

    def __init__(self, logger: logging.Logger, db: Postgres, http: HTTP) -> None:
        self.logger = logger
        self.db = db
        self.http = http
        self.api = AlphaVantage(api_key=API_KEY)
        self.session = self.__get_http_session()

    def __get_http_session(self):
        header = {"content-type": "application/json"}
        session = self.http.get_session(header=header)
        return session

    def get_price(self, ticker: str, limit: str = "one"):
        self.logger.info(f"Getting price for ticker- {ticker}")
        url = self.api.get_open_close(ticker=ticker)
        try:
            response = self.http.make_request(method="GET", url=url, session=self.session)
        except Exception as err:
            self.logger.error(f"Failed to get price spread for- {ticker}: {err}")
        else:
            result = {}
            result[ticker] = {}
            raw_data = response.get("content").get("Time Series (Daily)")
            for date, stats in raw_data:
                temp_result = {}
                temp_result["date"] = date
                temp_result["open"] = stats.get("1. open")
                temp_result["close"] = stats.get("4. close")
                temp_result["volume"] = stats.get("5. volume")
                result[ticker].update(temp_result)
                if limit == "one":
                    break
            return result

    def get_rsi(self, ticker: str, limit: str = "one"):
        self.logger.info(f"Getting price for ticker- {ticker}")
        url = self.api.get_open_close(ticker=ticker)
        try:
            response = self.http.make_request(method="GET", url=url, session=self.session)
        except Exception as err:
            self.logger.error(f"Failed to get price spread for- {ticker}: {err}")
        else:
            result = {}
            result[ticker] = {}
            raw_data = response.get("content").get("Technical Analysis: RSI")
            for date, stats in raw_data:
                temp_result = {}
                temp_result["date"] = date
                temp_result["RSI"] = stats.get("RSI")
                result[ticker].update(temp_result)
                if limit == "one":
                    break
            return result