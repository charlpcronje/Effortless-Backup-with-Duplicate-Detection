# src/core/backup_manager.py
"""
This file contains the BackupManager class, which is responsible for
managing the backup process.
"""
import os
import shutil
import logging
import time
from core.progress_reporter import ProgressReporter

class BackupManager:
    """
    Manages the backup process.
    """
    def __init__(self, config, db_manager):
        """
        Initializes the BackupManager with the application configuration and database manager.

        Args:
            config (dict): A dictionary containing the application configuration.
            db_manager (DatabaseManager): An instance of the DatabaseManager class.
        """
        self.config = config
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        self.logger.debug("BackupManager initialized")

    def get_free_space(self, path):
        """
        Gets the free space in bytes of the given path.

        Args:
            path (str): The path to check.

        Returns:
            int: The free space in bytes.
        """
        self.logger.debug(f"Getting free space for path: {path}")
        try:
            total, used, free = shutil.disk_usage(path)
            self.logger.debug(f"Free space: {free} bytes")
            return free
        except Exception as e:
            self.logger.error(f"Error getting free space: {e}")
            return 0

    def backup_files(self, files, progress_bar):
        """
        Backs up the selected files and folders to the backup destination.

        Args:
            files (list): A list of dictionaries, each representing a file or folder.
            progress_bar (ProgressBar): An instance of the ProgressBar class.
        """
        self.logger.info("Starting backup process")
        backup_destination = self.config.get("BACKUP_DESTINATION")
        total_files = len(files)
        progress_reporter = ProgressReporter(progress_bar, total_files, "Backing Up Files")

        for i, file in enumerate(files):
            progress_reporter.update_progress(i + 1, f"Copying: {file['name']}")
            self.backup_file(file, backup_destination)
            time.sleep(0.1) # Simulate work
        progress_reporter.finish()
        self.logger.info("Backup process completed")

    def backup_file(self, file, backup_destination):
        """
        Backs up a single file or folder to the backup destination.

        Args:
            file (dict): A dictionary representing the file or folder.
            backup_destination (str): The path to the backup destination.
        """
        self.logger.debug(f"Backing up file: {file['name']}")
        file_path = file["path"]
        dest_path = os.path.join(backup_destination, os.path.relpath(file_path, self.config.get("MOUNTED_PATH")))
        self.db_manager.update_file_status(file["id"], "copying")
        try:
            if file["type"] == "file":
                self.copy_file(file, file_path, dest_path, backup_destination)
            elif file["type"] == "folder":
                self.copy_folder(file, file_path, dest_path)
            elif file["type"] == "symlink":
                self.create_symlink(file, file_path, dest_path)
            self.db_manager.update_file_status(file["id"], "success")
            self.logger.debug(f"File backed up successfully: {file['name']}")
        except Exception as e:
            self.db_manager.update_file_status(file["id"], "failed")
            self.logger.error(f"Error backing up file {file['name']}: {e}")

    def copy_file(self, file, file_path, dest_path, backup_destination):
        """
        Copies a file to the backup destination.

        Args:
            file (dict): A dictionary representing the file.
            file_path (str): The path to the source file.
            dest_path (str): The path to the destination file.
            backup_destination (str): The path to the backup destination.
        """
        self.logger.debug(f"Copying file: {file['name']} from {file_path} to {dest_path}")
        try:
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            if file.get("content_owner_id"):
                original_file = self.db_manager.get_file_by_path(file_path)
                if original_file:
                    original_dest_path = os.path.join(backup_destination, os.path.relpath(original_file["path"], self.config.get("MOUNTED_PATH")))
                    self.create_symlink(file, original_dest_path, dest_path)
                else:
                    shutil.copy2(file_path, dest_path)
            else:
                shutil.copy2(file_path, dest_path)
            self.logger.debug(f"File copied successfully: {file['name']}")
        except Exception as e:
            self.logger.error(f"Error copying file {file['name']}: {e}")
            raise

    def copy_folder(self, file, file_path, dest_path):
        """
        Copies a folder to the backup destination.

        Args:
            file (dict): A dictionary representing the folder.
            file_path (str): The path to the source folder.
            dest_path (str): The path to the destination folder.
        """
        self.logger.debug(f"Copying folder: {file['name']} from {file_path} to {dest_path}")
        try:
            os.makedirs(dest_path, exist_ok=True)
            self.logger.debug(f"Folder copied successfully: {file['name']}")
        except Exception as e:
            self.logger.error(f"Error copying folder {file['name']}: {e}")
            raise

    def create_symlink(self, file, target_path, link_path):
        """
        Creates a symbolic link at the destination path pointing to the target path.

        Args:
            file (dict): A dictionary representing the file.
            target_path (str): The path to the target file.
            link_path (str): The path where the symlink should be created.
        """
        self.logger.debug(f"Creating symlink: {link_path} -> {target_path}")
        try:
            os.makedirs(os.path.dirname(link_path), exist_ok=True)
            os.symlink(target_path, link_path)
            self.logger.debug(f"Symlink created successfully: {link_path} -> {target_path}")
        except OSError as e:
            self.logger.error(f"Error creating symlink {link_path} -> {target_path}: {e}, falling back to copying")
            self.copy_file(file, target_path, link_path, self.config.get("BACKUP_DESTINATION"))
        except Exception as e:
            self.logger.error(f"Error creating symlink {link_path} -> {target_path}: {e}")
            raise
