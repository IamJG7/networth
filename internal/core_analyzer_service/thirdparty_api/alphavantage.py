"""
alphavantage module returns URIs for AlphaVantage.co
"""

import datetime
import os
from urllib.parse import urlencode

BASE_URL="www.alphavantage.co"

class AlphaVantage:
    '''
    AlphaVantage
    '''

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def __build_url(self, function: str, symbol: str) -> str:
        url_path = "query"
        query_param = urlencode({"function": function, "symbol": symbol, "apikey": self.api_key})
        url = f"https://{BASE_URL}/{url_path}?{query_param}"
        return url

    def __build_url_indicator(self, function: str, symbol: str, interval: str, time_period: int, series_type: str) -> str:
        url_path = "query"
        query_param = urlencode({"function": function, "symbol": symbol, "interval": interval, "time_period": time_period, "series_type": series_type, "apikey": self.api_key})
        url = f"https://{BASE_URL}/{url_path}?{query_param}"
        return url

    def get_open_close(self, symbol: str):
        '''
        get_open_close
        '''
        function = "TIME_SERIES_DAILY"
        url = self.__build_url(function=function, symbol=symbol)
        return url

    def get_rsi(self, symbol: str, interval: str = "daily", time_period: int = 14, series_type: str = "close"):
        '''
        get_rsi
        '''
        function = "RSI"
        url = self.__build_url_indicator(function=function, symbol=symbol, interval=interval, time_period=time_period, series_type=series_type)
        return url

    def get_sma(self, symbol: str, interval: str = "daily", time_period: int = 50, series_type: str = "close"):
        '''
        get_sma
        '''
        function = "SMA"
        url = self.__build_url_indicator(function=function, symbol=symbol, interval=interval, time_period=time_period, series_type=series_type)
        return url

    def get_ema(self, symbol: str, interval: str = "daily", time_period: int = 20, series_type: str = "close"):
        '''
        get_ema
        '''
        function = "EMA"
        url = self.__build_url_indicator(function=function, symbol=symbol, interval=interval, time_period=time_period, series_type=series_type)
        return url