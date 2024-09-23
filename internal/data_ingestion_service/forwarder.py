'''
forwarder
'''

from config.config import Config
from internal.data_ingestion_service.usecase.ingestor import EquityIngestor
from pkg.logger import logging

class Forwarder:
    '''
    Forwarder
    '''
    def __init__(self, config: Config, logger: logging.Logger) -> None:
        self.config = config
        self.logger = logger
        self.ingestor = EquityIngestor(config=config, logger=logger)

    def add_statistics(self, date: str, result: dict, transaction_id: str):
        '''
        add_statistics
        '''
        try:
            self.ingestor.add_stock_statistics(date=date, statistics=result, tx_id=transaction_id)
        except Exception as exc:
            self.logger.error(f"Failed to add statistical data for transactionID: {transaction_id}: {exc}")