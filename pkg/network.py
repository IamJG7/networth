'''
network module defines network layer methods for the application
'''

import socket
from pkg.logger import Logger

class Network:
     
    def __init__(self, logger: Logger) -> None:
        self.logger = logger
          
          
    def get_ipv4(self, dns='4.2.2.2', port=80) -> str:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.connect((dns, port))
                ipv4 = sock.getsockname()[0]
                return str(ipv4)
        except socket.error as err:
            self.logger.error(err)
            raise Exception(f"Failed to get the network address: {err}")
    
    def get_hostname(self) -> str:
        try:
            return socket.gethostbyname(socket.gethostname())
        except socket.error as err:
            self.logger.error(err)
            raise Exception(f"Failed to get the hostname: {err}")