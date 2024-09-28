'''
notify
'''

import json
import os
from prettytable import PrettyTable
from config.config import Config
from pkg.database import Database
from pkg.logger import logging
from pkg.notification import Email

SUCCESS = "success"
APP_DIRECTORY=os.getenv("APP_DIRECTORY")
RESULT_DIRECTORY=os.path.join(APP_DIRECTORY, "artifacts", "result")

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
        recipients = user_data.get("recipients")
        transaction_db = self.config.get("database").get("transaction_db")
        stats_db = self.config.get("database").get("stats_db")
        transaction_expiry = self.config.get("database").get("transaction_key_expiry")

        data = self.__get_raw_data(tickers=tickers, date=date)
        tabular_data = self.__convert_data_to_table(result=data)
        
        self.logger.info(f"Sending email for transactionID: {tx_id}")

        html_data = tabular_data.get_html_string()

        email_subject = f"Stock Analysis | {date}"
        email_body = f"""
        <html><body><p>Hello Investor!</p>
        <p>Thank you for using our beta StockAnalyzer.</p>
        {html_data}
        <p>*Note: These results are probabilistic and do not guarantee any profit. Please invest at your own risk.</p>
        <p></p>
        JGLab Automation
        </body></html>
        """
        try:
            self.email.send(subject=email_subject, body=email_body, recipients=recipients)
        except Exception as exc:
            self.logger.error(exc)
            self.database.hset(name=tx_id, key="status", value=str(exc))
            raise Exception(f"Failed to send email: {exc}") from exc
        else:
            self.database.select(index=transaction_db)
            self.database.hset(name=tx_id, key="staus", value=SUCCESS)
            self.database.expire(name=tx_id, time=transaction_expiry)

    def __get_raw_data(self, tickers: list, date: str) -> dict:
        result = {}
        try:
            if tickers[0].lower() == "watchlist":
                tickers = self.database.hkeys(name="watchlist")
            for ticker in tickers:
                result[ticker] = {}
                stats = self.database.hget(name=date, key=ticker)
                if stats is None:
                    continue
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
        try:
            column_fields = ["Ticker", "Open", "Close", "RSI", "SMA50", "SMA200", "Signal", "Position"]
            row_fields = []

            for ticker, stats in result.items():
                if stats.get("statistics") is None:
                    continue
                open_price = stats.get("statistics").get("open")
                close_price = stats.get("statistics").get("close")
                rsi = stats.get("statistics").get("rsi")
                sma50 = stats.get("statistics").get("sma50")
                sma200 = stats.get("statistics").get("sma200")
                signal = stats.get("analysis").get("technical_analysis").get("signal")
                position = stats.get("analysis").get("technical_analysis").get("position")
                row = [ticker, open_price, close_price, rsi, sma50, sma200, signal, position]
                row_fields.append(row)

            tablular_result = PrettyTable(field_names=column_fields)
            tablular_result.add_rows(rows=row_fields)
        except Exception as exc:
            self.logger.error(f"Failed to convert statistical and analytical data to table: {exc}")
        else:
            return tablular_result
