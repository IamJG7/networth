'''
email module outlines methods for smtp notifications
'''

import os
from smtplib import SMTP
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import ssl
from src.config.config import Config
from src.lib.logger.logger import logging

class Email:

    def __init__(self, config: Config, logger: logging.Logger) -> None:
        self.config = config
        self.logger = logger

    def send(self, subject: str, body: str, attachment: object=None) -> None:
        sender = self.config.get("sender")
        recipients = self.config.get("recipients")
        server = SMTP
        try:
            server = self.__configure_smtp()
            message = self.__make_email_structure(subject=subject, body=body, attachment=attachment)

            server.login(os.getenv("SMTP_USERNAME"), os.getenv("SMTP_PASSWORD"))
            server.sendmail(from_addr=sender, to_addrs=recipients, msg=message.as_string())
        except Exception as err:
            self.logger.error(err)
            raise Exception(f"Failed to send an email: {err}")
        finally:
            if server:
                server.quit()
        
    def __configure_smtp(self) -> SMTP:
        host = self.config.get("host")
        port = self.config.get("port")
        timeout = self.config.get("timeout")
        debug = self.config.get("debug")
        tls = self.config.get("tls")
        ssl_protocol = self.config.get("ssl_protocol")
        try:
            server = SMTP(host=host, port=port, timeout=timeout)
            if debug:
                server.set_debuglevel(1)
            if tls:
                if ssl_protocol.upper() == "TLS":
                    context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS)
                elif ssl_protocol.upper() == "TLSV1":
                    context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLSv1)
                elif ssl_protocol.upper() == "TLSV1.1":
                    context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLSv1_1)
                elif ssl_protocol.upper() == "TLSV1.2":
                    context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLSv1_2)
                elif ssl_protocol.upper() == "SSLV2":
                    context = ssl.SSLContext(protocol=ssl.PROTOCOL_SSLv2)
                elif ssl_protocol.upper() == "SSLV3":
                    context = ssl.SSLContext(protocol=ssl.PROTOCOL_SSLv3)
                else:
                    context = ssl.create_default_context()
                server.starttls(context=context)
            return server
        except Exception as err:
            self.logger.error(err)
            raise Exception(f"Failed to configure the mail client: {err}")       

    def __make_email_structure(self, subject: str, body: str, attachment: object) -> MIMEMultipart:
        message = MIMEMultipart()
        message['Subject'] = subject
        self.__make_header(message=message)
        self.__make_body(message=message, body=body)
        if attachment is not None:
            self.__make_attachment(message=message, attachment=attachment)
        return message

    def __make_header(self, message: MIMEMultipart) -> None:
        _from = self.config.get("sender")
        _to = self.config.get("recipients")
        _cc = self.config.get("carbon_copies")
        _bcc = self.config.get("blind_carbon_copies")
    
        message['From'] = _from
        message['To'] = ', '.join(_to)
        if self.config.get("carbon_copies"):
            message['Cc'] = ', '.join(_cc)
        if self.config.get("blind_carbon_copies"):
            message['Bcc'] = ', '.join(_bcc)

    def __make_body(self, message: MIMEMultipart, body: object) -> None:
        try:
            if self.config.get("body_type").lower() == "html":
                html_part = MIMEText(body, "html")
            else:
                html_part = MIMEText(body)
            message.attach(html_part)
        except Exception as err:
            self.logger.error(err)
            raise Exception(f"Failed to read and attach the email body: {err}")

    def __make_attachment(self, message: MIMEMultipart, attachment: object) -> None:
        try:
            with open(attachment, "rb") as file:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(file.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {attachment}"
            )
            message.attach(payload=part)
        except Exception as err:
            self.logger.error(err)
            raise Exception(f"Failed to read and attach the email attachment: {err}")
