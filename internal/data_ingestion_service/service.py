'''
flask module is the main module to kickstart the application webserver
'''

import json
import time
from config.config import Config
from internal.data_ingestion_service.forwarder import Forwarder
from pkg.database import Database
from pkg.logger import Logger

class IngestionService:
    '''
    IngestionService
    '''
    def __init__(self, config: Config, logger: Logger) -> None:
        self.config = config
        self.logger = logger
        self.database = Database(config=config.get("database").get("redis"), logger=logger).connect()
        self.forwarder = Forwarder(config=config, logger=logger)
        
 
    def start(self) -> None:
        '''
        start method initiates the IngestionService
        '''
        channel = self.config.get("database").get("channel_core_to_ingestion")

        envrionment = self.config.get("webserver").get("environment").upper()
        self.logger.info(f"Starting the IngestionService in {envrionment} environment")
        subscriber = self.database.pubsub()
        subscriber.subscribe(channel)

        for message in subscriber.listen():
            if message.get("type") == "message":
                data = json.loads(message.get("data"))
                if data.get("request") == "ingestion":
                    self.forwarder.add_statistics(date=data.get("date"),
                                                  result=data.get("result"),
                                                  transaction_id=data.get("transaction_id"))
            else:
                time.sleep(5)