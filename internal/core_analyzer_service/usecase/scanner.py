'''
scanner module
'''

import json
import re
from uuid import uuid4
from config.config import Config
from internal.core_analyzer_service.usecase.etf import ETF
from internal.core_analyzer_service.usecase.stock import Stock
from pkg.database import Database
from pkg.logger import logging

CHANNEL = "ch2"
WAIT_TIME = 65
SUCCESS="success"
FAILURE="failure"

class EquityScanner:
    '''
    EquityScanner
    '''
    def __init__(self, config: Config, logger: logging.Logger) -> None:
        self.config = config
        self.logger = logger
        self.etf = ETF(config=config, logger=logger)
        self.stock = Stock(config=config, logger=logger)
        self.database = Database(config=config.get("database").get("redis"), logger=logger).connect(db=0)
    
    def scan_stock_statistics(self, user_data: dict, tx_id: str) -> dict:
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
                try:
                    if type_ == "stock":
                            price = self.stock.get_price(ticker=ticker, date=date)
                            self.database.hset(name=tx_id, key="status", value=SUCCESS)
                    elif type_ == "etf":
                        price = self.etf.get_price(ticker=ticker)
                        self.database.hset(name=tx_id, key="status", value=SUCCESS)
                except Exception as exc:
                    self.logger.error(exc)
                    self.database.hset(name=tx_id, key="status", value=FAILURE)
                else:
                    result[ticker].update(price)

            if indicator == "rsi":
                try:
                    if type_ == "stock":
                        rsi = self.stock.get_rsi(ticker=ticker, date=date)
                        self.database.hset(name=tx_id, key="status", value=SUCCESS)
                    elif type_ == "etf":
                        rsi = self.etf.get_rsi(ticker=ticker)
                        self.database.hset(name=tx_id, key="status", value=SUCCESS)
                except Exception as exc:
                    self.logger.error(exc)
                    self.database.hset(name=tx_id, key="status", value=FAILURE)
                else:
                    result[ticker].update(rsi)

            if "sma" in indicator:
                match = re.match(r"([a-z]+)([0-9]+)", indicator, re.I)
                try:
                    if type_ == "stock":
                        sma = self.stock.get_sma(ticker=ticker, date=date, sma=match.group(2))
                        self.database.hset(name=tx_id, key="status", value=SUCCESS)
                    elif type_ == "etf":
                        sma = self.etf.get_sma(ticker=ticker, sma=match.group(2))
                        self.database.hset(name=tx_id, key="status", value=SUCCESS)
                except Exception as exc:
                    self.logger.error(exc)
                    self.database.hset(name=tx_id, key="status", value=FAILURE)
                else:
                    result[ticker].update(sma)

            if "ema" in indicator:
                match = re.match(r"([a-z]+)([0-9]+)", indicator, re.I)
                try:
                    if type_ == "stock":
                        ema = self.stock.get_ema(ticker=ticker, date=date, ema=match.group(2))
                        self.database.hset(name=tx_id, key="status", value=SUCCESS)
                    elif type_ == "etf":
                        ema = self.etf.get_ema(ticker=ticker, ema=match.group(2))
                        self.database.hset(name=tx_id, key="status", value=SUCCESS)
                except Exception as exc:
                    self.logger.error(exc)
                    self.database.hset(name=tx_id, key="status", value=FAILURE)
                else:
                    result[ticker].update(ema)

        try:
            message = {}
            transaction_status = self.database.hget(name=tx_id, key="status")
            if transaction_status == "success":
                message["date"] = date
                message["result"] = result
                message[tx_id] = SUCCESS
                message["transaction_id"] = str(uuid4())
                message["request"] = "ingestion"
            else:
                message[tx_id] = FAILURE
            self.database.publish(channel=CHANNEL, message=json.dumps(message))
        except Exception as exc:
            raise Exception(f"Failed to publish ingestion request for {tx_id}: {exc}") from exc
        else:
            self.logger.info(f"Successfully published ingestion request for transactionID: {tx_id} with message: {message}")
