'''
notify
'''

import json
from prettytable import PrettyTable
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
        content = user_data.get("content")
        transaction_db = self.config.get("database").get("transaction_db")
        stats_db = self.config.get("database").get("stats_db")
        transaction_expiry = self.config.get("database").get("transaction_key_expiry")

        data = self.__get_raw_data(tickers=tickers, date=date)
        email_content = self.__convert_data_to_table(result=data)
        print(email_content)


    def __get_raw_data(self, tickers: list, date: str) -> dict:
        result = {}
        try:
            if tickers[0].lower() == "watchlist":
                tickers = self.database.hkeys(name="watchlist")
            for ticker in tickers:
                result[ticker] = {}
                stats = self.database.hget(name=date, key=ticker)
                if stats is None:
                    result[ticker]["statistics"] = {}
                else:
                    result[ticker]["statistics"] = json.loads(stats)

                analysis = self.database.hget(name="analysis", key=ticker)
                if analysis is None:
                    result[ticker]["analysis"] = {}
                else:
                    result[ticker]["analysis"] = json.loads(analysis)
        except Exception as exc:
            self.logger.error(f"Failed to retrieve analysis: {exc}")
            raise Exception((20001, f"Failed to retrieve analysis")) from exc
        else:
            return result

    def __convert_data_to_table(self, result: dict) -> PrettyTable:

        column_fields = ["Ticker", "Open", "Close", "RSI", "SMA50", "SMA200", "Signal", "Position"]
        row_fields = []
        '''
        {'MSFT': {'statistics': {'open': 437.22, 'close': 435.27, 'high': 439.24, 'low': 434.22, 'volume': 49826691.0, 'after_hours': 436.03, 'pre_market': 438.14, 'rsi': 60.58, 'sma50': 421.65, 'sma200': 413.91, 'ema20': 423.69}, 'analysis': {'date': '2024-09-20', 'technical_analysis': {'signal': 'WatchForTrend', 'position': 'Hold'}, 'fundamental_analysis': {}}}, 'AVGO': {'statistics': {'open': 167.18, 'close': 171.1, 'high': 172.02, 'low': 166.47, 'volume': 77338658.0, 'after_hours': 170.84, 'pre_market': 167.44, 'rsi': 59.46, 'sma50': 156.95, 'sma200': 137.63, 'ema20': 160.03}, 'analysis': {'date': '2024-09-20', 'technical_analysis': {'signal': 'WatchForTrend', 'position': 'Hold'}, 'fundamental_analysis': {}}}}
        '''

        # for ticker, stats in result.items():
        return {}