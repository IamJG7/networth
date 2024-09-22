'''
scanner module
'''

import json
from config.config import Config
from internal.core_analyzer_service.usecase.etf import ETF
from internal.core_analyzer_service.usecase.stock import Stock
from pkg.logger import logging

CHANNEL = "ch2"

class EquityScanner:
    '''
    EquityScanner
    '''
    def __init__(self, config: Config, logger: logging.Logger) -> None:
        self.config = config
        self.logger = logger
        self.etf = ETF(config=config, logger=logger)
        self.stock = Stock(config=config, logger=logger)
    
    def scan_stock_statistics(self, user_data: dict) -> dict:
        '''
        scan_stock_statistics
        '''
        type_ = user_data.get("type")
        ticker = user_data.get("ticker")
        date = user_data.get("date")
        result = {}
        result[ticker] = {}
        for indicator in user_data.get("statistics"):
            if indicator == "price":
                if type_ == "stock":
                    price = self.stock.get_price(ticker=ticker, date=date)
                    result[ticker].update(price)

        return result
