'''
database module provides database client to perform operations
'''

import os
from redis import Redis, RedisError

from config.config import Config
from pkg.logger import Logger


class Database:
    '''
    Database
    '''

    def __init__(self, config: Config, logger: Logger) -> None:
        self.config = config
        self.logger = logger

    def connect(self, db: int = None) -> Redis:
        '''
        connect
        '''
        host = self.config.get("host")
        port = self.config.get("port")
        if db is None:
            db = self.config.get("db")
        encoding = self.config.get("encoding")
        decode_response = self.config.get("decode_response")
        username = os.getenv("REDIS_USERNAME")
        password = os.getenv("REDIS_PASSWORD")
        try:
            redis_client = Redis(host=host, port=port, db=db, encoding=encoding, decode_responses=decode_response)
        except RedisError as exc:
            self.logger.error(f"Failed to connect to Redis server: {exc}")
            raise RedisError(f"Failed to connect to Redis server: {exc}")
        else:
            return redis_client