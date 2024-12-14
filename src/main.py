# src/main.py
"""
This is the main entry point for the Effortless Backup application.
It initializes and starts the GUI application.
"""
import os
import logging
from gui.main_window import MainWindow
from utils.config_loader import ConfigLoader
from database.database_manager import DatabaseManager

def main():
    """
    Main function to initialize and run the application.
    """
    # Load configuration from .env file
    config = ConfigLoader()
    config_data = config.load_config()

    # Configure logging
    log_level = config_data.get("LOG_LEVEL", "DEBUG").upper()
    log_file_path = config_data.get("LOG_FILE_PATH", "app.log")
    numeric_level = getattr(logging, log_level, None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file_path)
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info("Application started")

    # Initialize database manager
    db_manager = DatabaseManager(config_data)
    db_manager.initialize_database()

    # Initialize and run the main window
    root = MainWindow(config_data, db_manager)
    root.mainloop()

    logger.info("Application finished")

if __name__ == "__main__":
    main()
