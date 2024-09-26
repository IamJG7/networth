'''
notify
'''

import json
from config.config import Config
from pkg.database import Database
from pkg.logger import logging
from pkg.notification import Email

class Notify:
    '''
    Notify
    '''
    def __init__(self, config: Config, logger: logging.Logger) -> None:
        self.config = config
        self.logger = logger
        self.database = Database(config=config.get("database").get("redis"), logger=self.logger).connect()
        self.email = Email(config=config.get("smtp"), logger=logger)
    
    def send_email(self, user_data: dict, tx_id: str):
        '''
        send_email
        '''
        tickers = user_data.get("tickers")
        date = user_data.get("date")
        transaction_db = self.config.get("database").get("transaction_db")
        stats_db = self.config.get("database").get("stats_db")
        transaction_expiry = self.config.get("database").get("transaction_key_expiry")

        stats = self.__retrieve_statistics(user_data=user_data)
        tech_analysis = self.__perform_technical_analysis(statistics=stats)

    def __retrieve_statistics(self, user_data: dict) -> dict:
        '''
        retrieve_statistics
        '''
        tickers = user_data.get("tickers")
        date = user_data.get("date")
        stats_db = self.config.get("database").get("stats_db")

        self.logger.debug(f"Retrieving statistical data for {user_data}")
        result = {}
        try:
            self.database.select(index=stats_db)
            if tickers[0] == "watchlist":
                watchlist_tickers = self.database.hkeys(name="watchlist")
                for wticker in watchlist_tickers:
                    stats = self.database.hget(name=date, key=wticker)
                    if stats is None:
                        result[wticker] = {}
                    else:
                        result[wticker] = json.loads(stats)
            else:
                for ticker in tickers:
                    stats = self.database.hget(name=date, key=ticker)
                    if stats is None:
                        result[ticker] = {}
                    else:
                        result[ticker] = json.loads(stats)
        except Exception as exc:
            self.logger.error(f"Failed to retrieve statistics: {exc}")
            raise Exception((10005, f"Failed to retrieve statistics")) from exc
        else:
            return result
    
    def __perform_technical_analysis(self, statistics: dict) -> dict:
        result = {}
        for ticker, statstic in statistics.items():
            result[ticker] = {}
            if statstic.get("rsi") < 30:
                if statstic.get("close") < statstic.get("sma50") and statstic.get("close") < statstic.get("sma200"):
                    result[ticker]["signal"] = "MustBuy"
                    result[ticker]["position"] = "ForLongRun"
                if statstic.get("close") < statstic.get("sma50") and statstic.get("close") > statstic.get("sma200"):
                    result[ticker]["signal"] = "Buy"
                    result[ticker]["position"] = "ForLongRun"
                if statstic.get("close") > statstic.get("sma50") and statstic.get("close") < statstic.get("sma200"):    # Rare to find
                    result[ticker]["signal"] = "Wait"
                    result[ticker]["position"] = "Undetermined"
                if statstic.get("close") > statstic.get("sma50") and statstic.get("close") > statstic.get("sma200"):    # Rare to find
                    result[ticker]["signal"] = "Wait"
                    result[ticker]["position"] = "Undetermined"

            if 30 < statstic.get("rsi") < 50:
                if statstic.get("close") < statstic.get("sma50") and statstic.get("close") < statstic.get("sma200"):
                    result[ticker]["signal"] = "WatchForTrend"
                    result[ticker]["position"] = "ForShortRun"
                if statstic.get("close") < statstic.get("sma50") and statstic.get("close") > statstic.get("sma200"):
                    result[ticker]["signal"] = "WatchForTrend"
                    result[ticker]["position"] = "ForShortRun"
                if statstic.get("close") > statstic.get("sma50") and statstic.get("close") < statstic.get("sma200"):
                    result[ticker]["signal"] = "WaitToFallMore"
                    result[ticker]["position"] = "Hold"
                if statstic.get("close") > statstic.get("sma50") and statstic.get("close") > statstic.get("sma200"):    # Rare to find
                    result[ticker]["signal"] = "CanBuy"
                    result[ticker]["position"] = "ForLongRun"

            if 50 < statstic.get("rsi") < 70:
                if statstic.get("close") < statstic.get("sma50") and statstic.get("close") < statstic.get("sma200"):    # Rare to find
                    result[ticker]["signal"] = "Wait"
                    result[ticker]["position"] = "Undetermined"
                if statstic.get("close") < statstic.get("sma50") and statstic.get("close") > statstic.get("sma200"):
                    result[ticker]["signal"] = "WatchForTrend"
                    result[ticker]["position"] = "Hold"
                if statstic.get("close") > statstic.get("sma50") and statstic.get("close") < statstic.get("sma200"):
                    result[ticker]["signal"] = "WatchForTrend"
                    result[ticker]["position"] = "Hold"
                if statstic.get("close") > statstic.get("sma50") and statstic.get("close") > statstic.get("sma200"):
                    result[ticker]["signal"] = "WatchForTrend"
                    result[ticker]["position"] = "Hold"

            if statstic.get("rsi") > 70:
                if statstic.get("close") < statstic.get("sma50") and statstic.get("close") < statstic.get("sma200"):    # Rare to find
                    result[ticker]["signal"] = "Wait"
                    result[ticker]["position"] = "Undetermined"
                if statstic.get("close") < statstic.get("sma50") and statstic.get("close") > statstic.get("sma200"):    # Rare to find
                    result[ticker]["signal"] = "Wait"
                    result[ticker]["position"] = "Undetermined"
                if statstic.get("close") > statstic.get("sma50") and statstic.get("close") < statstic.get("sma200"):    # Rare to find
                    result[ticker]["signal"] = "Wait"
                    result[ticker]["position"] = "Undetermined"
                if statstic.get("close") > statstic.get("sma50") and statstic.get("close") > statstic.get("sma200"):
                    result[ticker]["signal"] = "StartToSell"
                    result[ticker]["position"] = "Undetermined"
        return result

# TODO: Write an API for analysis