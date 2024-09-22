'''
http module defines HTTP(s) request/response methods for the application
'''

import json
import os
from requests import Response, Session
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from config.config import Config

SSL_CERT_FILE_NAME = "http.crt"
SSL_CERT_FILE_DIR = os.path.join("src","lib", "http")
DOWNLOAD_DIR = os.path.join("artifacts","downloads")

class HTTP:
    '''
    HTTP
    '''

    def __init__(self, config: Config) -> None:
        self.config = config

    def make_request(self, method: str, url: str, data: dict = None, session: Session= None, stream: bool= False) -> dict:
        '''
        make_request
        '''
        timeout = self.config.get('timeout')
        try:
            if session is None:
                session = self.get_session()
            timeout = self.config.get('timeout')
            if stream:
                response = session.request(method=method.upper(), url=url, data=data, timeout=timeout, stream=stream)
                response.raise_for_status()
            else:
                response = session.request(method=method.upper(), url=url, data=data, timeout=timeout)
                response.raise_for_status()
        except Exception as err:
            raise Exception(f"Failed to make a HTTP request: {err}")
        else:
            return self.__make_response(response=response)
        finally:
            if response:
                response.close()
      
    def get_session(self, authentication: bool= False, header: dict= None, proxy: dict= None) -> Session:
        '''
        get_session
        '''
        try:
            session = Session()
            if self.config.get("ssl_verification"):
                application_root = os.getenv("APP_DIRECTORY")
                ssl_cert_file_path = os.path.join(application_root, SSL_CERT_FILE_DIR, SSL_CERT_FILE_NAME)
                self.__update_ssl_cert(session=session, cert=ssl_cert_file_path)
            if authentication:
                username = os.getenv("HTTPS_USERNAME")
                password = os.getenv("HTTPS_PASSWORD")
                self.__update_authentication(session=session, username=username, password=password)
            if header is not None:
                self.__update_header(session=session, header=header)
            if proxy is not None:
                proxies = {
                    "http": self.config.get("http_proxy"),
                    "https": self.config.get("https_proxy")
                }
                self.__update_proxy(session=session, proxy=proxies)
            self.__enable_retries(session=session)
        except Exception as err:
            raise Exception(f"Failed to configure a session: {err}")
        else:
            return session

    def __update_ssl_cert(self, session: Session, cert: str) -> None:
        try:
            session.verify = cert
        except Exception as err:
            raise Exception(f"Failed to configure a SSL certificate: {err}")

    def __update_header(self, session: Session, header: dict) -> None:
        try:
            session.headers.update(header)
        except Exception as err:
            raise Exception(f"Failed to configure a header: {err}")

    def __update_authentication(self, session: Session, username: str, password: str) -> None:
        try:
            session.auth = (username, password)
        except Exception as err:
            raise Exception(f"Failed to configure an authentication: {err}")

    def __update_proxy(self, session: Session, proxy: dict) -> None:
        try:
            session.proxies.update(proxy)
        except Exception as err:
            raise Exception(f"Failed to configure a proxy: {err}")

    def __enable_retries(self, session: Session) -> None:
        try:
            retries = Retry(
                total=self.config.get("retries"),
                backoff_factor=self.config.get("backoff_factor"),
                status_forcelist=self.config.get("retry_forcelist"),
                allowed_methods=self.config.get("retry_allowed_methods"),
            )
            session.mount("https://", HTTPAdapter(max_retries=retries))
        except Exception as err:
            raise Exception(f"Failed tp configure a retries: {err}")
      
    def __make_response(self, response: Response) -> dict:
        try:
            if response.encoding is None:
                response.encoding = "utf-8"
            response_header = response.headers
            request_header = response.request.headers
            status_code = response.status_code
            if "application/json" in response_header.get("Content-Type"):
                content = json.loads(response.text)
            else:
                self.__download_file(response=response)
        except Exception as err:
            raise Exception(f"Failed to make a response: {err}")
        else:
            return {"status_code": status_code, "content": content}
    
    def __download_file(self, response: Response) -> None:
        try:
            response_content_threshold = self.config.get("max_response_body_download_size")
            response_content_chunk = self.config.get("download_chunk_size")
            response_header = response.headers
            if "content-disposition" in response_header:
                filename = response_header.get("content-disposition").split(";")[1].split("=")[1].replace("\"", "")
            else:
                content_type = response_header.get("Content-Type").split("/")[1]
                filename = f"download.{content_type}"
            download_dir = os.path.join(os.getenv("APP_DIRECTORY"), DOWNLOAD_DIR)
            download_path = os.path.join(download_dir, filename)
            if "Content-Length" in response_header:
                if int(response_header.get("Content-Length")) > response_content_threshold:
                    with open(file=download_path, mode="wb") as download_stream:
                        for content in response.iter_content(chunk_size=response_content_chunk, decode_unicode=False):
                            download_stream.write(content)
        except Exception as err:
            raise Exception(f"Failed to download file: {err}")
