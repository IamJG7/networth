'''
scanner module
'''

import json
import re
import time
from uuid import uuid4
from config.config import Config
from internal.core_analyzer_service.usecase.etf import ETF
from internal.core_analyzer_service.usecase.stock import Stock
from pkg.database import Database
from pkg.logger import logging

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
        self.database = Database(config=config.get("database").get("redis"), logger=logger).connect()
    
    def scan_stock_statistics(self, user_data: dict, tx_id: str) -> dict:
        '''
        scan_stock_statistics
        '''
        equity_type = user_data.get("type")
        tickers = user_data.get("tickers")
        date = user_data.get("date")
        channel = self.config.get("database").get("channel_core_to_ingestion")
        transaction_db = self.config.get("database").get("transaction_db")
        _ = self.config.get("database").get("stats_db")
        cooling_period = self.config.get("third_party").get("polygon").get("request_cooling_period")
        transaction_expiry = self.config.get("database").get("transaction_key_expiry")

        if tickers[0].lower() == "watchlist":
            tickers = self.database.hkeys(name="watchlist")
        
        self.database.select(index=transaction_db)
        self.database.hset(name=tx_id, key="status", value="in_progress")
        
        try:
            for ticker in tickers:
                if self.database.exists("request_wait_period"):
                    time.sleep(self.database.ttl(name="request_wait_period"))
                request_count = 0
                result = {}
                result[ticker] = {}
                for indicator in user_data.get("statistics"):

                    if indicator == "price":
                        try:
                            if equity_type == "stock":
                                    price = self.stock.get_price(ticker=ticker, date=date)
                                    self.database.hset(name=tx_id, key=indicator, value=SUCCESS)
                            elif equity_type == "etf":
                                price = self.etf.get_price(ticker=ticker)
                                self.database.hset(name=tx_id, key=indicator, value=SUCCESS)
                        except Exception as exc:
                            self.logger.error(exc)
                            self.database.hset(name=tx_id, key=indicator, value=FAILURE)
                        else:
                            result[ticker].update(price)
                            request_count += 1

                    if indicator == "rsi":
                        try:
                            if equity_type == "stock":
                                rsi = self.stock.get_rsi(ticker=ticker, date=date)
                                self.database.hset(name=tx_id, key=indicator, value=SUCCESS)
                            elif equity_type == "etf":
                                rsi = self.etf.get_rsi(ticker=ticker)
                                self.database.hset(name=tx_id, key=indicator, value=SUCCESS)
                        except Exception as exc:
                            self.logger.error(exc)
                            self.database.hset(name=tx_id, key=indicator, value=FAILURE)
                        else:
                            result[ticker].update(rsi)
                            request_count += 1

                    if "sma" in indicator:
                        match = re.match(r"([a-z]+)([0-9]+)", indicator, re.I)
                        try:
                            if equity_type == "stock":
                                sma = self.stock.get_sma(ticker=ticker, date=date, sma=match.group(2))
                                self.database.hset(name=tx_id, key=indicator, value=SUCCESS)
                            elif equity_type == "etf":
                                sma = self.etf.get_sma(ticker=ticker, sma=match.group(2))
                                self.database.hset(name=tx_id, key=indicator, value=SUCCESS)
                        except Exception as exc:
                            self.logger.error(exc)
                            self.database.hset(name=tx_id, key=indicator, value=FAILURE)
                        else:
                            result[ticker].update(sma)
                            request_count += 1

                    if "ema" in indicator:
                        match = re.match(r"([a-z]+)([0-9]+)", indicator, re.I)
                        try:
                            if equity_type == "stock":
                                ema = self.stock.get_ema(ticker=ticker, date=date, ema=match.group(2))
                                self.database.hset(name=tx_id, key=indicator, value=SUCCESS)
                            elif equity_type == "etf":
                                ema = self.etf.get_ema(ticker=ticker, ema=match.group(2))
                                self.database.hset(name=tx_id, key=indicator, value=SUCCESS)
                        except Exception as exc:
                            self.logger.error(exc)
                            self.database.hset(name=tx_id, key=indicator, value=FAILURE)
                        else:
                            result[ticker].update(ema)
                            request_count += 1

                if request_count >= 5:
                    self.database.setex(name="request_wait_period", time=cooling_period, value="cooling_period")

                try:
                    message = {}
                    message["date"] = date
                    message["result"] = result
                    message[tx_id] = ticker
                    message["transaction_id"] = str(uuid4())
                    message["request"] = "ingestion"

                    self.database.publish(channel=channel,
                                          message=json.dumps(message))
                except Exception as exc:
                    raise Exception(f"Failed to publish ingestion request for {tx_id}: {exc}") from exc
                else:
                    self.logger.info(f"Successfully published ingestion request for transactionID: {tx_id} with message: {message}")
        except Exception as exc:
            self.database.hset(name=tx_id, key="status", value=FAILURE)
            self.database.expire(name=tx_id, time=transaction_expiry)
            raise Exception(f"Failed to scan stock statistics: {exc}") from exc
        else:
            self.database.hset(name=tx_id, key="status", value=SUCCESS)
            self.database.expire(name=tx_id, time=transaction_expiry)
