'''
This module defines logging methods of the application
'''

import logging
import os
import pathlib
from config.config import Config

LOG_FILE_LOCATION = os.path.join("artifacts", "logs")

class Logger:
    '''
    Logger
    '''

    application_name = os.getenv("APP_NAME")
    service_name=os.getenv("SERVICE_NAME")
    logger_name= f"{application_name}-{service_name}"
    log_file_name = f"{logger_name}.log"

    def __init__(self, config: Config) -> None:
        self.config = config

    def get_logger(self, name: str = None) -> logging.LoggerAdapter:
        '''
        get_logger
        '''
        if name is None:
            logger = logging.getLogger(name=self.logger_name)
        else:
            logger = logging.getLogger(name=name)
        self.__set_level(logger=logger)
        self.__set_handler(logger=logger)
        return logger
    
    def __set_level(self, logger: logging.Logger) -> None:
        if os.getenv("APP_LOGGING_LEVEL").upper() == "DEBUG":
            logger.setLevel(logging.DEBUG)
        if os.getenv("APP_LOGGING_LEVEL").upper() == "INFO":
            logger.setLevel(logging.INFO)
        if os.getenv("APP_LOGGING_LEVEL").upper() == "WARNING":
            logger.setLevel(logging.WARNING)
        if os.getenv("APP_LOGGING_LEVEL").upper() == "ERROR":
            logger.setLevel(logging.ERROR)
        if os.getenv("APP_LOGGING_LEVEL").upper() == "CRITICAL":
            logger.setLevel(logging.CRITICAL)

    def __set_handler(self, logger: logging.Logger) -> None:
        stream_handler = self.config.get("stream_handler")
        file_handler = self.config.get("file_handler")
        syslog_handler = self.config.get("syslog_handler")
        
        if not logger.hasHandlers():
            if stream_handler:
                streamhandler = logging.StreamHandler()
                self.__set_format(handler=streamhandler)
                logger.addHandler(hdlr=streamhandler)
            if file_handler:
                application_root = os.getenv("APP_DIRECTORY")
                log_file_directory = os.path.join(application_root, LOG_FILE_LOCATION)
                log_file_location = os.path.join(log_file_directory, LOG_FILE_NAME)
                if not os.path.exists(path=log_file_location):
                    pathlib.Path(log_file_directory).mkdir(parents=True, exist_ok=True)
                log_handle_mode = self.config.get("file_handler_mode")
                log_file_size = self.config.get("file_rotation_size")
                log_file_backup_counts = self.config.get("file_backup_count")
                log_file_encoding = self.config.get("file_handler_encoding")
                filehandler =logging.handlers.RotatingFileHandler(
                    filename=log_file_location,
                    mode=log_handle_mode,
                    maxBytes=log_file_size,
                    backupCount=log_file_backup_counts,
                    encoding=log_file_encoding
                )
                self.__set_format(handler=filehandler)
                logger.addHandler(hdlr=filehandler)
            if syslog_handler:
                syslog_host = self.config.get("syslog_host")
                syslog_port = self.config.get("syslog_port")
                syslog_socket = self.config.get("syslog_socket")
                sysloghandler = logging.handlers.SysLogHandler(
                    address=(syslog_host, syslog_port),
                    socktype=syslog_socket
                )
                self.__set_format(handler=sysloghandler)
                logger.addHandler(hdlr=sysloghandler)

    def __set_format(self, handler: logging.Handler) -> None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        datetime_format = "%d-%m-%Y T%H:%M%S"
        formatter = logging.Formatter(fmt=log_format, datefmt=datetime_format)
        handler.setFormatter(formatter)