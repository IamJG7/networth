"""
This module defines all the applicable methods for 
"""

import datetime
import os
from urllib.parse import urlencode

BASE_URL="api.polygon.io"

class Polygon:

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def __build_url(self, uri: str, ticker: str, date: datetime.date, adjusted: bool = True) -> str:
        url_path = f"{uri}/{ticker}/{date}"
        query_param = urlencode({"adjusted": adjusted, "apiKey": self.api_key})
        url = f"https://{BASE_URL}/{url_path}?{query_param}"
        return url

    def __build_url_indicator(self, uri: str, ticker: str, date: datetime.date, timespan: str, window: int, series_type: str = "close", order: str = "desc", adjusted: bool = True) -> str:
        url_path = f"{uri}/{ticker}"
        if date is None:
            query_param = urlencode({"timespan": timespan, "window": window, "series_type": series_type, "order": order, "adjusted": adjusted, "apiKey": self.api_key})
        else:
            query_param = urlencode({"timestamp": date, "timespan": timespan, "window": window, "series_type": series_type, "order": order, "adjusted": adjusted, "apiKey": self.api_key})
        url = f"https://{BASE_URL}/{url_path}?{query_param}"
        return url

    def get_open_close(self, ticker: str, date: datetime.date):
        uri = "v1/open-close"
        url = self.__build_url(uri=uri, ticker=ticker, date=date)
        return url
    
    def get_rsi(self, ticker: str, date: datetime.date = None, timespan: str = "day", window: int = 14):
        uri = "v1/indicators/rsi"
        url = self.__build_url_indicator(uri=uri, ticker=ticker, date=date, timespan=timespan, window=window)
        return url

    def get_sma(self, ticker: str, date: datetime.date, timespan: str = "day", window: int = 50):
        uri = "v1/indicators/sma"
        url = self.__build_url_indicator(uri=uri, ticker=ticker, date=date, timespan=timespan, window=window)
        return url

    def get_ema(self, ticker: str, date: datetime.date, timespan: str = "day", window: int = 9):
        uri = "v1/indicators/ema"
        url = self.__build_url_indicator(uri=uri, ticker=ticker, date=date, timespan=timespan, window=window)
        return url
    
    def get_aggregate(self, ticker: str, start_day: datetime.date, end_date: datetime.date, multiplier: int = 1, timespan: str = "day", adjusted: bool = True):
        uri = "v2/aggs"
        url_path = f"ticker/{ticker}/range/{multiplier}/{timespan}/{start_day}/{end_date}"
        query_param = urlencode({"adjusted": adjusted, "apiKey": self.api_key})
        url = f"https://{BASE_URL}/{uri}/{url_path}?{query_param}"
        return url

    def get_dividend(self, ticker: str, limit: int = 10):
        uri = "v3/reference/dividends"
        query_param = urlencode({"ticker": ticker, "limit": limit, "apiKey": self.api_key})
        url = f"https://{BASE_URL}/{uri}?{query_param}"
        return url
