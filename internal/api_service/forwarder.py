'''

'''

from flask import json

from config.config import Config
from internal.api_service.usecase.equity import Equity
from pkg.logger import logging
from pkg.tools import password

SUCCESS = "success"

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

    def get_watchlist(self) -> json:
        '''
        get_watchlist
        '''
        return {}

    def add_watchlist(self, user_data: json) -> str:
        '''
        add_watchlist
        '''
        try:
            status = self.equity.create_watchlist(user_data=user_data)
        except Exception as exc:
            self.logger.error(f"Failed to update the Watchlist: {exc}")
            raise Exception from exc
        else:
            return status