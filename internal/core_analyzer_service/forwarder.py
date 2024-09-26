'''
forwarder
'''

from config.config import Config
from internal.core_analyzer_service.usecase.notify import Notify
from internal.core_analyzer_service.usecase.scanner import EquityScanner
from pkg.logger import logging

class Forwarder:
    '''
    Forwarder
    '''
    def __init__(self, config: Config, logger: logging.Logger) -> None:
        self.config = config
        self.logger = logger
        self.scanner = EquityScanner(config=config, logger=logger)
        self.notify = Notify(config=config, logger=logger)

    def add_statistics(self, user_data: dict, transaction_id: str) -> None:
        '''
        add_statistic
        '''
        try:
            self.scanner.scan_stock_statistics(user_data=user_data, tx_id=transaction_id)
        except Exception as exc:
            self.logger.error(f"Failed to add statistical data for transactionID: {transaction_id}: {exc}")
    
    def send_notification(self, user_data: dict, transaction_id: str) -> None:
        '''
        notify
        '''
        try:
            self.notify.send_email(user_data=user_data, tx_id=transaction_id)
        except Exception as exc:
            self.logger.error(f"Failed to send notification for transactionID: {transaction_id}: {exc}")