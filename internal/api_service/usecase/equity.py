'''
equity
'''

import json
from config.config import Config
from pkg.database import Database
from pkg.logger import Logger

SUCCESS = "success"
FAILURE = "failure"

class Equity:
    '''
    Equity
    '''

    def __init__(self, config: Config, logger: Logger) -> None:
        self.config = config
        self.logger = logger
        self.database = Database(config=config.get("database").get("redis"), logger=self.logger).connect()
    
    def create_watchlist(self, user_data: json) -> str:
        '''
        create_watchlist
        '''
        self.database.select(index=1)
        if isinstance(user_data, dict):
            self.logger.info("Updating 1 stock to the Watchlist")
            status = self.database.hset(name="watchlist",
                                        key=user_data.get("ticker"),
                                        value=json.dumps(user_data))
            if status != 0:
                return FAILURE
            return SUCCESS
        elif isinstance(user_data, list):
            self.logger.info(f"Updating {len(user_data)} stocks to the Watchlist")
            pipe = self.database.pipeline()
            for i in user_data:
                pipe.hset(name="watchlist",
                          key=i.get("ticker"),
                          value=json.dumps(i))
            status = pipe.execute(raise_on_error=True)
            if len(set(status)) != 1 or list(set(status))[0] != 0:
                return FAILURE
            return SUCCESS

