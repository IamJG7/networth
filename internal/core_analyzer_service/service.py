'''
flask module is the main module to kickstart the application webserver
'''

import json
import time
from config.config import Config
from internal.core_analyzer_service.forwarder import Forwarder
from pkg.database import Database
from pkg.logger import Logger

class CoreService:
    '''
    CoreService
    '''

    def __init__(self, config: Config, logger: Logger) -> None:
        self.config = config
        self.logger = logger
        self.database = Database(config=config.get("database").get("redis"), logger=logger).connect()
        self.forwarder = Forwarder(config=config, logger=logger)
        
    def start(self) -> None:
        '''
        start method initiates the AnalyzerService
        '''
        channel = self.config.get("database").get("channel_api_to_core")

        envrionment = self.config.get("webserver").get("environment").upper()
        self.logger.info(f"Starting the CoreService in {envrionment} environment")
        subscriber = self.database.pubsub()
        subscriber.subscribe(channel)

        for message in subscriber.listen():
            if message.get("type") == "message":
                data = json.loads(message.get("data"))
                if data.get("request") == "statistics":
                    self.forwarder.add_statistics(user_data=data.get("user_data"), transaction_id=data.get("transaction_id"))
                if data.get("request") == "fundamentals":
                    pass
                if data.get("request") == "notify":
                    self.forwarder.send_notification(user_data=data.get("user_data"), transaction_id=data.get("transaction_id"))
            else:
                time.sleep(3)