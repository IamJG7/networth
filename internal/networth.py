
from config.config import Config
from internal.api_service.service import APIService
from internal.core_analyzer_service.service import CoreService
from pkg.logger import Logger

class Application:
    '''
    Service class defines start and stop methods
    '''
    def __init__(self) -> None:
        self.config = Config().get_global_config()
        self.logger = Logger(config=self.config.get('logging')).get_logger()

    def start(self) -> None:
        '''
        start method initiates the respective services (APIService/CoreAnalyzer/DataIngestion)
        '''
        self.logger.info("Starting the Networth Analyzer Application")

        api_service = APIService(config=self.config, logger=self.logger)
        core_service = CoreService(config=self.config, logger=self.logger)
        ingestion_service = APIService(config=self.config, logger=self.logger)

        core_service.start()
    
    def stop(self) -> None:
        '''
        stop method terminates the respective services (APIService/CoreAnalyzer/DataIngestion)
        '''
        self.logger.info("Stopping the Networth Analyzer Application")
