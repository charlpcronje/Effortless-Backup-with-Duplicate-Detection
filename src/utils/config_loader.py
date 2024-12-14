# src/utils/config_loader.py
"""
This file contains the ConfigLoader class, which is responsible for loading
configuration settings from the .env file.
"""
import os
from dotenv import load_dotenv
import logging

class ConfigLoader:
    """
    Loads configuration settings from the .env file.
    """
    def __init__(self):
        """
        Initializes the ConfigLoader by loading the .env file.
        """
        load_dotenv()
        self.logger = logging.getLogger(__name__)
        self.logger.debug("ConfigLoader initialized")

    def load_config(self):
        """
        Loads all configuration settings from the .env file.

        Returns:
            dict: A dictionary containing all the configuration settings.
        """
        self.logger.debug("Loading configuration from .env file")
        config = {
            "MOUNTED_PATH": os.getenv("MOUNTED_PATH"),
            "BACKUP_DESTINATION": os.getenv("BACKUP_DESTINATION"),
            "APP_THEME": os.getenv("APP_THEME", "light"),
            "PRIMARY_COLOR": os.getenv("PRIMARY_COLOR", "#ffffff"),
            "SECONDARY_COLOR": os.getenv("SECONDARY_COLOR", "#000000"),
            "PROGRESS_BAR_COLOR": os.getenv("PROGRESS_BAR_COLOR", "#00ff00"),
            "LOG_LEVEL": os.getenv("LOG_LEVEL", "DEBUG"),
            "LOG_FILE_PATH": os.getenv("LOG_FILE_PATH", "app.log")
        }
        self.logger.debug(f"Configuration loaded: {config}")
        return config
