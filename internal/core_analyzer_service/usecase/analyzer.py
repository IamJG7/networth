'''
analyzer
'''

import json
from config.config import Config
from pkg.database import Database
from pkg.logger import Logger

SUCCESS = "success"

class SecurityAnalyzer:
    '''
    SecurityAnalyzer
    '''
    def __init__(self, config: Config, logger: Logger) -> None:
        self.config = config
        self.logger = logger
        self.database = Database(config=config.get("database").get("redis"), logger=self.logger).connect()

    def analyze(self, user_data: dict, tx_id: str) -> dict:
        '''
        analyze
        '''
        tickers = user_data.get("tickers")
        date = user_data.get("date")
        transaction_db = self.config.get("database").get("transaction_db")
        transaction_expiry = self.config.get("database").get("transaction_key_expiry")

        result = {}
        try:
            if tickers[0].lower() == "watchlist":
                tickers = self.database.hkeys(name="watchlist")
            for ticker in tickers:
                result[ticker] = {}
                result[ticker]["date"] = date

                data = self.database.hget(name=date, key=ticker)
                if data is None:
                    continue
                statistics = json.loads(data)
                result[ticker]["technical_analysis"] = {}
                if statistics.get("rsi") < 30:
                    if statistics.get("close") < statistics.get("sma50") and statistics.get("close") < statistics.get("sma200"):
                        result[ticker]["technical_analysis"] = {"signal": "MustBuy", "position": "ForLongRun"}
                    if statistics.get("close") < statistics.get("sma50") and statistics.get("close") > statistics.get("sma200"):
                        result[ticker]["technical_analysis"] = {"signal": "Buy", "position": "ForLongRun"}
                    if statistics.get("close") > statistics.get("sma50") and statistics.get("close") < statistics.get("sma200"):    # Rare to find
                        result[ticker]["technical_analysis"] = {"signal": "Wait", "position": "Undetermined"}
                    if statistics.get("close") > statistics.get("sma50") and statistics.get("close") > statistics.get("sma200"):    # Rare to find
                        result[ticker]["technical_analysis"] = {"signal": "Wait", "position": "Undetermined"}

                if 30 < statistics.get("rsi") < 50:
                    if statistics.get("close") < statistics.get("sma50") and statistics.get("close") < statistics.get("sma200"):
                        result[ticker]["technical_analysis"] = {"signal": "WatchForTrend", "position": "ForShortRun"}
                    if statistics.get("close") < statistics.get("sma50") and statistics.get("close") > statistics.get("sma200"):
                        result[ticker]["technical_analysis"] = {"signal": "WatchForTrend", "position": "ForShortRun"}
                    if statistics.get("close") > statistics.get("sma50") and statistics.get("close") < statistics.get("sma200"):
                        result[ticker]["technical_analysis"] = {"signal": "WaitToFallMore", "position": "Hold"}
                    if statistics.get("close") > statistics.get("sma50") and statistics.get("close") > statistics.get("sma200"):    # Rare to find
                        result[ticker]["technical_analysis"] = {"signal": "CanBuy", "position": "ForLongRun"}

                if 50 < statistics.get("rsi") < 70:
                    if statistics.get("close") < statistics.get("sma50") and statistics.get("close") < statistics.get("sma200"):    # Rare to find
                        result[ticker]["technical_analysis"] = {"signal": "Wait", "position": "Undetermined"}
                    if statistics.get("close") < statistics.get("sma50") and statistics.get("close") > statistics.get("sma200"):
                        result[ticker]["technical_analysis"] = {"signal": "WatchForTrend", "position": "Hold"}
                    if statistics.get("close") > statistics.get("sma50") and statistics.get("close") < statistics.get("sma200"):
                        result[ticker]["technical_analysis"] = {"signal": "WatchForTrend", "position": "Hold"}
                    if statistics.get("close") > statistics.get("sma50") and statistics.get("close") > statistics.get("sma200"):
                        result[ticker]["technical_analysis"] = {"signal": "WatchForTrend", "position": "Hold"}

                if statistics.get("rsi") > 70:
                    if statistics.get("close") < statistics.get("sma50") and statistics.get("close") < statistics.get("sma200"):    # Rare to find
                        result[ticker]["technical_analysis"] = {"signal": "Wait", "position": "Undetermined"}
                    if statistics.get("close") < statistics.get("sma50") and statistics.get("close") > statistics.get("sma200"):    # Rare to find
                        result[ticker]["technical_analysis"] = {"signal": "Wait", "position": "Undetermined"}
                    if statistics.get("close") > statistics.get("sma50") and statistics.get("close") < statistics.get("sma200"):    # Rare to find
                        result[ticker]["technical_analysis"] = {"signal": "Wait", "position": "Undetermined"}
                    if statistics.get("close") > statistics.get("sma50") and statistics.get("close") > statistics.get("sma200"):
                        result[ticker]["technical_analysis"] = {"signal": "StartToSell", "position": "Undetermined"}

                if statistics is None:
                    result[ticker]["technical_analysis"] = {}

                # fundamentals = self.database.hget(name="fundamental", key=ticker)
                result[ticker]["fundamental_analysis"] = {}

                self.database.hset(name="analysis", key=ticker, value=json.dumps(result[ticker]))
        except Exception as exc:
            self.logger.error(f"Failed to analyze {user_data}: {exc}")
        else:
            self.database.select(index=transaction_db)
            self.database.hset(name=tx_id, key="status", value=SUCCESS)
            self.database.expire(name=tx_id, time=transaction_expiry)
            return result
