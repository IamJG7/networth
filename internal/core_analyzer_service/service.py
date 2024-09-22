'''
flask module is the main module to kickstart the application webserver
'''

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

        envrionment = self.config.get("webserver").get("environment").upper()
        self.logger.info(f"Starting the CoreService in {envrionment} environment")
        subscriber = self.database.pubsub()
        subscriber.subscribe("ch1")

        for message in subscriber.listen():
            if message.get("type") == "message":
                data = message.get("data")
                if data.get("")