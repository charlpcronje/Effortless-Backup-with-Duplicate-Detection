# src/utils/hash_calculator.py
"""
This file contains the HashCalculator class, which is responsible for
calculating the hash of files for duplicate detection.
"""
import hashlib
import logging
import os

class HashCalculator:
    """
    Calculates the hash of files for duplicate detection.
    """
    def __init__(self):
        """
        Initializes the HashCalculator.
        """
        self.logger = logging.getLogger(__name__)
        self.logger.debug("HashCalculator initialized")

    def calculate_hash(self, file_path, file_size):
        """
        Calculates the hash of a file based on its size.

        Args:
            file_path (str): The path to the file.
            file_size (int): The size of the file in bytes.

        Returns:
            str: The calculated hash value.
        """
        self.logger.debug(f"Calculating hash for file: {file_path}")
        try:
            if file_size < 1024 * 1024:  # 1MB
                hash_value = self._calculate_full_hash(file_path)
            else:
                hash_value = self._calculate_partial_hash(file_path)
            self.logger.debug(f"Hash calculated successfully for file: {file_path}")
            return hash_value
        except Exception as e:
            self.logger.error(f"Error calculating hash for file {file_path}: {e}")
            return None

    def _calculate_full_hash(self, file_path):
        """
        Calculates the full SHA-256 hash of a file.

        Args:
            file_path (str): The path to the file.

        Returns:
            str: The full SHA-256 hash value.
        """
        self.logger.debug(f"Calculating full hash for file: {file_path}")
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                hasher.update(chunk)
        self.logger.debug(f"Full hash calculated successfully for file: {file_path}")
        return hasher.hexdigest()

    def _calculate_partial_hash(self, file_path):
        """
        Calculates a partial hash of a file based on the first, middle, and last 100KB.

        Args:
            file_path (str): The path to the file.

        Returns:
            str: The partial hash value.
        """
        self.logger.debug(f"Calculating partial hash for file: {file_path}")
        hasher = hashlib.sha256()
        chunk_size = 100 * 1024
        try:
            with open(file_path, "rb") as f:
                # First 100KB
                hasher.update(f.read(chunk_size))

                # Move to the middle
                f.seek(max(0, (os.path.getsize(file_path) // 2) - (chunk_size // 2)))
                hasher.update(f.read(chunk_size))

                # Move to the end
                f.seek(max(0, os.path.getsize(file_path) - chunk_size))
                hasher.update(f.read(chunk_size))
            self.logger.debug(f"Partial hash calculated successfully for file: {file_path}")
            return hasher.hexdigest()
        except Exception as e:
            self.logger.error(f"Error calculating partial hash for file {file_path}: {e}")
            return None
