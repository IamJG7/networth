from datetime import datetime, timedelta
import json
import os
import time
from requests import HTTPError
from config.config import Config
from internal.core_analyzer_service.thirdparty_api.polygon import Polygon
from pkg.http import HTTP
from pkg.logger import logging



API_KEY=os.getenv("POLYGON_DEV_API_KEY")
ALPHAVANTAGE_API_KEY=os.getenv("ALPHAVANTAGE_PROD_API_KEY")

class Stock:
    '''
    Stock
    '''

    def __init__(self, config: Config, logger: logging.Logger) -> None:
        self.config = config
        self.logger = logger
        self.polygon = Polygon(api_key=API_KEY)
        self.http = HTTP(config=self.config.get("http"))
        self.session = self.__get_http_session()

    def __get_http_session(self):
        header = {"Authorization": f"Bearer {API_KEY}", "content-type": "application/json"}
        session = self.http.get_session(header=header)
        return session

    def get_price(self, ticker: str, date: datetime.date) -> dict:
        '''
        get_price
        '''
        url = self.polygon.get_open_close(ticker=ticker, date=date)
        try:
            response = self.__make_http_requests(url=url)
        except Exception as exc:
            raise Exception(f"Failed to get price for- {ticker}: {exc}") from exc
        else:
            data = response.get("content")
            result = {}
            result["open"] = round(data.get("open"), 2)
            result["close"] = round(data.get("close"), 2)
            result["high"] = round(data.get("high"), 2)
            result["low"] = round(data.get("low"), 2)
            result["volume"] = round(data.get("volume"), 2)
            result["after_hours"] = round(data.get("afterHours"), 2)
            result["pre_market"] = round(data.get("preMarket"), 2)
            return result
        
    def get_sma(self, ticker: str, date: datetime.date, sma: int) -> dict:
        '''
        get_sma
        '''
        url = self.polygon.get_sma(ticker=ticker, date=date, window=sma)
        try:
            response = self.__make_http_requests(url=url)
        except Exception as exc:
            raise Exception(f"Failed to get Simple Moving Average for- {ticker}: {exc}") from exc
        else:
            result = {}
            result[f"sma{sma}"] = round(response.get("content").get("results").get("values")[0].get("value"), 2)
            return result

    def get_ema(self, ticker: str, date: datetime.date, ema: int) -> dict:
        '''
        get_ema
        '''
        url = self.polygon.get_ema(ticker=ticker, date=date, window=ema)
        try:
            response = self.__make_http_requests(url=url)
        except Exception as exc:
            raise Exception(f"Failed to get Exponential Moving Average for- {ticker}: {exc}") from exc
        else:
            result = {}
            result[f"ema{ema}"] = round(response.get("content").get("results").get("values")[0].get("value"), 2)
            return result

    def get_rsi(self, ticker: str, date: datetime.date) -> dict:
        '''
        get_rsi
        '''
        url = self.polygon.get_rsi(ticker=ticker, date=date)
        try:
            response = self.__make_http_requests(url=url)
        except Exception as exc:
            raise Exception(f"Failed to get RSI for- {ticker}: {exc}") from exc
        else:
            actual_response = response.get("content").get("results")
            result = {}
            result["rsi"] = round(actual_response.get("values")[0].get("value"), 2)
            return result

    def __make_http_requests(self, url):
        self.logger.debug(f"Making HTTP request for- {url}")
        try:
            response = self.http.make_request(method="GET", url=url, session=self.session)
        except HTTPError as exc:
            raise Exception (11000, f"Failed to make a HTTP request for {url}: {exc}") from exc
        return response

    def __convert_epoch_to_date(self, epoch: int):
        return datetime.fromtimestamp(int(str(epoch)[10:])).strftime("%Y-%m-%d")
