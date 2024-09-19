'''
flask module is the main module to kickstart the application webserver
'''

import os
from flask import Flask
from gevent.pywsgi import WSGIServer

from config.config import Config
from pkg.logger import Logger
from pkg.network import Network
from pkg.tools import password

from internal.api_service.routes.v1.configuration import configuration_blueprint
from internal.api_service.routes.v1.operation import operation_blueprint
from internal.api_service.routes.v1.operational import operational_blueprint
from internal.api_service.routes.error.error import error_blueprint

class APIService:

    def __init__(self, config: Config, logger: Logger) -> None:
        self.config = config
        self.logger = logger
        self.network = Network(logger=self.logger)
        
    def start(self) -> None:
        '''
        start method initiates the WebServer
        '''
        envrionment = self.config.get("webserver").get("environment").upper()
        debug = self.config.get("webserver").get("debug")
        passwd = password.get_password(length=32)
        web_address = self.network.get_ipv4()
        web_port = self.config.get("webserver").get("port")
        
        webapp = Flask(os.getenv("APP_NAME"))
        webapp.secret_key = passwd
        webapp.register_blueprint(blueprint=operation_blueprint)
        webapp.register_blueprint(blueprint=operational_blueprint)
        webapp.register_blueprint(blueprint=configuration_blueprint)
        webapp.register_blueprint(blueprint=error_blueprint)
        webapp.logger = self.logger
        try:
            if envrionment == "PRODUCTION":
                self.logger.info(f"Starting the WebServer in {envrionment} environment")
                webserver = WSGIServer(listener=(web_address, web_port), application=webapp, log=self.logger)
                webserver.serve_forever()
            elif envrionment == "DEVELOPMENT":
                self.logger.info(f"Starting the WebServer in {envrionment} environment")
                webapp.run(host=web_address, port=web_port, debug=debug)
        except Exception as exc:
            self.logger.error(exc)
            raise Exception(f"Failed to start the WebServer: {exc}") from exc
