import datetime
import os

from requests import HTTPError

from config.config import Config
from internal.core_analyzer_service.thirdparty_api.alphavantage import AlphaVantage
from pkg.http import HTTP
from pkg.logger import logging

API_KEY=os.getenv("ALPHAVANTAGE_DEV_API_KEY")

class ETF:

    def __init__(self, config: Config, logger: logging.Logger) -> None:
        self.config = config
        self.logger = logger
        self.alphavantage = AlphaVantage(api_key=API_KEY)
        self.http = HTTP(config=self.config.get("http"))
        self.session = self.__get_http_session()

    def __get_http_session(self):
        header = {"Authorization": f"Bearer {API_KEY}", "content-type": "application/json"}
        session = self.http.get_session(header=header)
        return session

    def get_price(self, ticker: str, limit: str = "one"):
        '''
        get_price
        '''
        self.logger.info(f"Getting price for ticker- {ticker}")
        url = self.alphavantage.get_open_close(symbol=ticker)
        try:
            response = self.http.make_request(method="GET", url=url, session=self.session)
        except Exception as err:
            self.logger.error(f"Failed to get price spread for- {ticker}: {err}")
        else:
            result = {}
            for stats in response.get("content").get("Time Series (Daily)").values():
                result["open"] = round(float(stats.get("1. open")), 2)
                result["close"] = round(float(stats.get("4. close")), 2)
                result["high"] = round(float(stats.get("2. high")), 2)
                result["low"] = round(float(stats.get("3. low")), 2)
                result["volume"] = round(float(stats.get("5. volume")), 2)
                result["after_hours"] = round(0.0, 2)
                result["pre_market"] = round(0.0, 2)
                if limit == "one":
                    break
            return result

    def get_sma(self, ticker: str, sma: int, limit: str = "one") -> dict:
        '''
        get_sma
        '''
        url = self.alphavantage.get_sma(symbol=ticker, time_period=sma)
        try:
            response = self.__make_http_requests(url=url)
        except Exception as exc:
            self.logger.error(f"Failed to get Simple Moving Average for- {ticker}: {exc}")
        else:
            result = {}
            for stats in response.get("content").get("Technical Analysis: SMA").values():
                result[f"sma{sma}"] = round(float(stats.get("SMA")), 2)
                if limit == "one":
                    break
            return result

    def get_ema(self, ticker: str, ema: int, limit: str = "one") -> dict:
        '''
        get_ema
        '''
        url = self.alphavantage.get_ema(symbol=ticker, time_period=ema)
        try:
            response = self.__make_http_requests(url=url)
        except Exception as exc:
            self.logger.error(f"Failed to get Exponential Moving Average for- {ticker}: {exc}")
        else:
            result = {}
            for stats in response.get("content").get("Technical Analysis: EMA").values():
                result[f"ema{ema}"] = round(float(stats.get("EMA")), 2)
                if limit == "one":
                    break
            return result

    def get_rsi(self, ticker: str, limit: str = "one") -> dict:
        '''
        get_rsi
        '''
        url = self.alphavantage.get_rsi(symbol=ticker)
        try:
            response = self.__make_http_requests(url=url)
        except Exception as exc:
            self.logger.error(f"Failed to get RSI for- {ticker}: {exc}")
        else:
            result = {}
            for stats in response.get("content").get("Technical Analysis: RSI").values():
                result["rsi"] = round(float(stats.get("RSI")), 2)
                if limit == "one":
                    break
            return result

    def __make_http_requests(self, url):
        self.logger.debug(f"Making HTTP request for- {url}")
        try:
            response = self.http.make_request(method="GET", url=url, session=self.session)
        except HTTPError as exc:
            raise Exception (11000, f"Failed to make a HTTP request for {url}: {exc}") from exc
        return response
