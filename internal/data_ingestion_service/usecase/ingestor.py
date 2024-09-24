'''
ingestor module
'''

import json
from config.config import Config
from pkg.database import Database
from pkg.logger import logging

SUCCESS="success"
FAILURE="failure"

class EquityIngestor:
    '''
    EquityIngestor
    '''
    def __init__(self, config: Config, logger: logging.Logger) -> None:
        self.config = config
        self.logger = logger
        self.database = Database(config=config.get("database").get("redis"), logger=logger).connect(db=config.get("database").get("stats_db"))
    
    def add_stock_statistics(self, date: str, statistics: dict, tx_id: str) -> None:
        '''
        add_stock_statistics
        '''
        stats_db = self.config.get("database").get("stats_db")
        transaction_db = self.config.get("database").get("transaction_db")
        transaction_expiry = self.config.get("database").get("transaction_key_expiry")

        try:
            ticker = [i for i in statistics.keys()][0]
            result = [i for i in statistics.values()][0]
            self.database.select(index=stats_db)
            if self.database.hexists(name=date, key=ticker):
                self.logger.warning(f"Result for {ticker} on {date} already exists!")
            else:
                self.database.hset(name=date, key=ticker, value=json.dumps(result))
        except Exception as exc:
            self.database.select(index=transaction_db)
            self.database.hset(name=tx_id, key="staus", value=FAILURE)
            raise Exception(f"Failed to update database request for {tx_id}: {exc}") from exc
        else:
            self.database.select(index=transaction_db)
            self.database.hset(name=tx_id, key="staus", value=SUCCESS)
            self.database.expire(name=tx_id, time=transaction_expiry)
            self.logger.info(f"Successfully updated database for transactionID: {tx_id} with statistics: {statistics}")
