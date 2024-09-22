'''

'''

from flask import json

from config.config import Config

from internal.core_analyzer_service.usecase.scanner import EquityScanner
from pkg.database import Database
from pkg.logger import logging

class Forwarder:
    '''
    Forwarder
    '''
    def __init__(self, config: Config, logger: logging.Logger) -> None:
        self.config = config
        self.logger = logger
        self.scanner = EquityScanner(config=config, logger=logger)
        self.database = Database(config=config.get("database").get("redis"), logger=logger).connect(db=0)

    def add_statistics(self, user_data: json) -> str:
        '''
        add_statistic
        '''
        _ = self.scanner.scan_stock_statistics(user_data=user_data)
        