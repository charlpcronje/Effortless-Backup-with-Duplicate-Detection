# src/core/file_scanner.py
"""
This file contains the FileScanner class, which is responsible for
scanning the file system and populating the database.
"""
import os
import logging
import hashlib
from core.progress_reporter import ProgressReporter

class FileScanner:
    """
    Scans the file system and populates the database.
    """
    def __init__(self, config, db_manager):
        """
        Initializes the FileScanner with the application configuration and database manager.

        Args:
            config (dict): A dictionary containing the application configuration.
            db_manager (DatabaseManager): An instance of the DatabaseManager class.
        """
        self.config = config
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        self.logger.debug("FileScanner initialized")

    def scan_directory(self, path, parent_id=None):
        """
        Recursively scans a directory and adds files and folders to the database.

        Args:
            path (str): The path of the directory to scan.
            parent_id (int, optional): The ID of the parent folder. Defaults to None.
        """
        self.logger.info(f"Scanning directory: {path}")
        try:
            for entry in os.scandir(path):
                if entry.is_dir():
                    file_id = self.add_entry_to_database(entry, "folder", parent_id)
                    self.scan_directory(entry.path, file_id)
                elif entry.is_file():
                    self.add_entry_to_database(entry, "file", parent_id)
                elif entry.is_symlink():
                    self.add_entry_to_database(entry, "symlink", parent_id, is_symlink=1)
        except FileNotFoundError:
            self.logger.error(f"Directory not found: {path}")
        except PermissionError:
            self.logger.error(f"Permission error accessing: {path}")
        except Exception as e:
            self.logger.error(f"Error scanning directory {path}: {e}")

    def add_entry_to_database(self, entry, file_type, parent_id, is_symlink=0):
        """
        Adds a file or folder entry to the database.

        Args:
            entry (os.DirEntry): The directory entry to add.
            file_type (str): The type of the entry ('file', 'folder', 'symlink').
            parent_id (int): The ID of the parent folder.
            is_symlink (int, optional): 1 if the entry is a symlink, 0 otherwise. Defaults to 0.

        Returns:
            int: The ID of the newly added entry.
        """
        self.logger.debug(f"Adding entry to database: {entry.name}, type: {file_type}")
        try:
            file_path = entry.path
            file_size = entry.stat().st_size if file_type != "symlink" else 0
            self.db_manager.insert_file(entry.name, file_path, file_size, file_type, "pending", parent_id, is_symlink=is_symlink)
            file_data = self.db_manager.get_file_by_path(file_path)
            if file_data:
                return file_data["id"]
            else:
                self.logger.error(f"Failed to retrieve file data after insertion: {file_path}")
                return None
        except Exception as e:
            self.logger.error(f"Error adding entry to database: {e}")
            return None

    def find_duplicates(self, size_threshold, progress_bar, hash_calculator):
        """
        Finds duplicate files based on a size threshold and calculates their hashes.

        Args:
            size_threshold (int): The size threshold in bytes for duplicate detection.
            progress_bar (ProgressBar): An instance of the ProgressBar class.
            hash_calculator (HashCalculator): An instance of the HashCalculator class.
        """
        self.logger.info("Starting duplicate detection")
        files = self.db_manager.get_all_files()
        total_files = len(files)
        progress_reporter = ProgressReporter(progress_bar, total_files, "Finding Duplicates")
        hashes = {}
        for i, file in enumerate(files):
            progress_reporter.update_progress(i + 1, f"Processing: {file['name']}")
            if file["type"] == "file" and file["size"] > size_threshold:
                file_path = file["path"]
                try:
                    hash_value = hash_calculator.calculate_hash(file_path, file["size"])
                    self.db_manager.update_file_hash(file["id"], hash_value)
                    if hash_value in hashes:
                        original_file_id = hashes[hash_value]
                        self.db_manager.update_file_content_owner(file["id"], original_file_id)
                        self.logger.info(f"Duplicate found: {file['name']} (original: {original_file_id})")
                    else:
                        hashes[hash_value] = file["id"]
                except Exception as e:
                    self.logger.error(f"Error calculating hash for {file['name']}: {e}")
        progress_reporter.finish()
        self.logger.info("Duplicate detection completed")
