'''
transactions
'''

from config.config import Config
from pkg.database import Database
from pkg.logger import logging

class Transactions:
    '''
    Transactions
    '''
    def __init__(self, config: Config, logger: logging.Logger) -> None:
        self.config = config
        self.logger = logger
        self.database = Database(config=config.get("database").get("redis"), logger=self.logger).connect()

    def get_transaction(self, transaction_id: str) -> dict:
        '''
        get_transaction
        '''

        transaction_db = self.config.get("database").get("transaction_db")
        try:
            self.database.select(index=transaction_db)
            result = self.database.hgetall(name=transaction_id)
        except Exception as exc:
            self.logger.error(f"Failed to get transactionID: {transaction_id}: {exc}")
            raise Exception (30001, f"Failed to get transactionID: {transaction_id}") from exc
        else:
            return result