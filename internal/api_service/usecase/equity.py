'''
equity
'''

import json
from uuid import uuid4
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
            try:
                _ = self.database.hset(name="watchlist",
                                            key=user_data.get("ticker"),
                                            value=json.dumps(user_data))
            except Exception as exc:
                self.logger.error(f"Failed to create watchlist: {exc}")
                raise Exception(10001, "Failed to create watchlist") from exc
            
            return SUCCESS
            
        if isinstance(user_data, list):
            self.logger.info(f"Updating {len(user_data)} stocks to the Watchlist")
            try:
                pipe = self.database.pipeline()
                for i in user_data:
                    pipe.hset(name="watchlist",
                            key=i.get("ticker"),
                            value=json.dumps(i))
                _ = pipe.execute(raise_on_error=True)
            except Exception as exc:
                self.logger.error(f"Failed to create watchlist: {exc}")
                raise Exception(10002, "Failed to create watchlist") from exc

            return SUCCESS

    def retrieve_watchlist(self, user_data: json) -> json:
        '''
        retrieve_watchlist
        '''
        ticker = user_data.get("ticker")
        try:
            if ticker is None:
                watchlist = self.database.hgetall(name="watchlist")
            else:
                watchlist = self.database.hget(name="watchlist", key=ticker)
        except Exception as exc:
            self.logger.error(f"Failed to retrieve watchlist: {exc}")
            raise Exception(10003, "Failed to retrieve watchlist") from exc
        
        return watchlist

    def update_statistics(self, user_data: dict) -> str:
        '''
        update_statistics
        '''
        channel = self.config.get("database").get("channel_api_to_core")
        transaction_db = self.config.get("database").get("transaction_db")

        message = {}
        message["user_data"] = user_data
        message["transaction_id"] = str(uuid4())
        message["request"] = "statistics"
        try:
            self.logger.debug(f"Publising request to the ch1 with transaction ID: {message['transaction_id']}")
            _ = self.database.publish(channel=channel, message=json.dumps(message))
            self.database.select(index=transaction_db)
            self.database.hset(name=message["transaction_id"], key="status", value="pending")
        except Exception as exc:
            raise Exception((10004, "Failed to update statistics")) from exc
        else:
            return message["transaction_id"]

    def retrieve_statistics(self, user_data: json) -> json:
        '''
        retrieve_statistics
        '''
        ticker = user_data.get("ticker")
        date = user_data.get("date")
        self.logger.debug(f"Retrieving statistical data for {ticker}")
        result = {}
        try:
            if ticker is None:
                watchlist_tickers = self.database.hkeys(name="watchlist")
                for wticker in watchlist_tickers:
                    stats = self.database.hget(name=wticker, key=date)
                    result[wticker] = stats
            else:
                stats = self.database.hget(name=ticker, key=date)
                result[ticker] = stats
        except Exception as exc:
            raise Exception((10005, "Failed to retrieve statistics")) from exc

        return result
