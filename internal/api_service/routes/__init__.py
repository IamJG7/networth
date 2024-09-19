import sys
from config.config import Config
from internal.api_service.forwarder import Forwarder
from pkg.logger import Logger

LOGGER_NAME = "WebServer"

try:
    config = Config().get_global_config()
    logger = Logger(config=config.get('logging'), name=LOGGER_NAME).get_logger()

    forwarder = Forwarder(config=config, logger=logger)
except Exception as exc:
    print("Failed to initialize API service prerequisites")
    sys.exit(2)