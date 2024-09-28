'''

'''

from flask import json

from config.config import Config
from internal.api_service.usecase.equity import Equity
from pkg.logger import logging
from pkg.tools import password

class Forwarder:
    '''
    Forwarder
    '''
    def __init__(self, config: Config, logger: logging.Logger) -> None:
        self.config = config
        self.logger = logger
        self.equity = Equity(config=config, logger=logger)

    def generate_password(self, user_data: json) -> str:
        '''
        generate_password
        '''
        passphrase = password.get_password(length=user_data.get("length"),
                                           skip_symbol=user_data.get("skip_symbol"))
        return passphrase

    def get_watchlist(self, user_data: json) -> json:
        '''
        get_watchlist
        '''
        result = self.equity.retrieve_watchlist(user_data=user_data)
        return result

    def add_watchlist(self, user_data: json) -> str:
        '''
        add_watchlist
        '''
        status = self.equity.create_watchlist(user_data=user_data)
        return status

    def get_statistics(self, user_data: json) -> json:
        '''
        fetch_stock_data
        '''
        status = self.equity.retrieve_statistics(user_data=user_data)
        return status

    def add_statistic(self, user_data: json) -> str:
        '''
        add_statistic
        '''
        status = self.equity.update_statistics(user_data=user_data)
        return status

    def analyze(self, user_data: dict) -> str:
        '''
        analyze
        '''
        status = self.equity.analyze(user_data=user_data)
        return status


    def notify(self, user_data: dict) -> str:
        '''
        notify
        '''
        status = self.equity.notify(user_data=user_data)
        return status
