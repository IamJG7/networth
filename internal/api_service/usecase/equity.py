'''
equity
'''

import json
import uuid
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
        if isinstance(user_data, dict):
            self.logger.info("Updating 1 stock to the Watchlist")
            status = self.database.hset(name="watchlist",
                                        key=user_data.get("ticker"),
                                        value=json.dumps(user_data))
            if status != 0:
                return FAILURE
            return SUCCESS
        if isinstance(user_data, list):
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

    def retrieve_watchlist(self, user_data: json) -> json:
        '''
        retrieve_watchlist
        '''
        ticker = user_data.get("ticker")
        if ticker is None:
            watchlist = self.database.hgetall(name="watchlist")
        else:
            watchlist = self.database.hget(name="watchlist", key=ticker)
        return watchlist

    def update_statistics(self, user_data: json) -> json:
        '''
        update_statistics
        '''
        message = {}
        message.update(user_data)
        message["transaction_id"] = uuid.uuid4()
        message["request"] = "statistics"

        '''
        TODO: Extract str content from uuid.
        '''
        status = self.database.publish(channel="ch1", message=json.dumps(message))
        print(status)
        print("-"*100)
        return {}

    def retrieve_statistics(self, user_data: json) -> json:
        '''
        retrieve_statistics
        '''
        ticker = user_data.get("ticker")
        date = user_data.get("date")
        self.logger.debug(f"Retrieving statistical data for {ticker}")
        result = {}
        if ticker is None:
            watchlist_tickers = self.database.hkeys(name="watchlist")
            for wticker in watchlist_tickers:
                stats = self.database.hget(name=wticker, key=date)
                result[wticker] = stats
        else:
            stats = self.database.hget(name=ticker, key=date)
            result[ticker] = stats
        return result