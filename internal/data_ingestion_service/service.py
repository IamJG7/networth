'''
flask module is the main module to kickstart the application webserver
'''

from config.config import Config
from pkg.database import Database
from pkg.logger import Logger

class IngestionService:
    '''
    IngestionService
    '''

    def __init__(self, config: Config, logger: Logger) -> None:
        self.config = config
        self.logger = logger
        self.database = Database(config=config.get("database").get("redis"), logger=self.logger).connect()
        
    def start(self) -> None:
        '''
        start method initiates the IngestionService
        '''

