'''
config module loads global configuration to the application
'''

import os
import dotenv
import yaml

GLOBAL_CONFIG_FILE_NAME = "config.yaml"
GLOBAL_CONFIG_FILE_DIR = os.path.join("config")

class Config:
    '''
    Config class provides methods to load global configuration
    '''

    def __init__(self) -> None:
        pass

    def __get_application_root(self) -> str:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        application_root = "/".join(str(current_dir).split("/")[0:-1])
        os.environ["APP_DIRECTORY"] = application_root
        return application_root   

    def __check_file_exists(self) -> bool:
        application_root = self.__get_application_root()
        config_file_path = os.path.join(application_root, GLOBAL_CONFIG_FILE_DIR, GLOBAL_CONFIG_FILE_NAME)
        config_file_exists = os.path.exists(path=config_file_path)
        return config_file_exists

    def __load_config_file(self):
        try:
            if self.__check_file_exists():
                config_file_path = os.path.join(os.getenv("APP_DIRECTORY"), GLOBAL_CONFIG_FILE_DIR, GLOBAL_CONFIG_FILE_NAME)
                with open(file=config_file_path, mode="r", encoding="utf-8") as config_file:
                    config = yaml.safe_load(stream=config_file)
                    return config
            raise Exception("Global config file does not exist")
        except Exception as exc:
            raise Exception(f"Failed to load global config file: {exc}")

    def __load_env_vars(self):
        try:
            dotenv.find_dotenv(raise_error_if_not_found=False)
        except:
            raise Exception(f"Failed to find '.env' in the application")
        else:
            dotenv.load_dotenv()
    
    def __check_env_vars(self):
        if os.environ.get("APP_NAME") is None:
            raise Exception("Environment variables not set")

    def get_global_config(self) -> dict:
        '''
        get_global_config returns global configuration in JSON format
        '''
        global_config = self.__load_config_file()
        if global_config.get("application").get("environment") == "DEVELOPMENT":
            self.__load_env_vars()
            self.__check_env_vars()
        return self.__load_config_file()
