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
        self.database = Database(config=config.get("database").get("redis"), logger=logger).connect(db=1)
    
    def add_stock_statistics(self, date: str, statistics: dict, tx_id: str) -> None:
        '''
        add_stock_statistics
        '''
        try:
            ticker = [i for i in statistics.keys()][0]
            result = [i for i in statistics.values()][0]
            self.database.hset(name=date, key=ticker, value=json.dumps(result))
        except Exception as exc:
            self.database.select(index=0)
            self.database.hset(name=tx_id, key="staus", value=FAILURE)
            raise Exception(f"Failed to update database request for {tx_id}: {exc}") from exc
        else:
            self.database.select(index=0)
            self.database.hset(name=tx_id, key="staus", value=SUCCESS)
            self.logger.info(f"Successfully updated database for transactionID: {tx_id} with statistics: {statistics}")
