# src/database/database_manager.py
"""
This file contains the DatabaseManager class, which is responsible for
managing the SQLite database for the application.
"""
import sqlite3
import logging
import os

class DatabaseManager:
    """
    Manages the SQLite database for the application.
    """
    def __init__(self, config):
        """
        Initializes the DatabaseManager with the application configuration.

        Args:
            config (dict): A dictionary containing the application configuration.
        """
        self.config = config
        self.db_path = "backup.db"
        self.logger = logging.getLogger(__name__)
        self.logger.debug("DatabaseManager initialized")

    def initialize_database(self):
        """
        Initializes the database by creating the necessary tables if they don't exist.
        """
        self.logger.info("Initializing database")
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    path TEXT NOT NULL UNIQUE,
                    size INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    parent_id INTEGER,
                    hash TEXT,
                    is_symlink INTEGER,
                    content_owner_id INTEGER,
                    FOREIGN KEY (parent_id) REFERENCES files(id),
                    FOREIGN KEY (content_owner_id) REFERENCES files(id)
                )
            """)

            conn.commit()
            self.logger.info("Database initialized successfully")
        except sqlite3.Error as e:
            self.logger.error(f"Error initializing database: {e}")
        finally:
            if conn:
                conn.close()

    def check_previous_backup(self):
        """
        Checks if a previous backup was in progress.

        Returns:
            bool: True if a previous backup was in progress, False otherwise.
        """
        self.logger.debug("Checking for previous backup")
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM files WHERE status IN ('pending', 'failed', 'copying')")
            count = cursor.fetchone()[0]
            self.logger.debug(f"Found {count} files with pending, failed, or copying status")
            return count > 0
        except sqlite3.Error as e:
            self.logger.error(f"Error checking previous backup: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def get_files_by_status(self, status_list):
        """
        Retrieves files from the database based on their status.

        Args:
            status_list (list): A list of status values to filter by.

        Returns:
            list: A list of dictionaries, each representing a file.
        """
        self.logger.debug(f"Getting files with status in {status_list}")
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            placeholders = ', '.join('?' for _ in status_list)
            cursor.execute(f"SELECT * FROM files WHERE status IN ({placeholders})", status_list)
            rows = cursor.fetchall()
            files = []
            for row in rows:
                file = {
                    "id": row[0],
                    "name": row[1],
                    "path": row[2],
                    "size": row[3],
                    "type": row[4],
                    "status": row[5],
                    "parent_id": row[6],
                    "hash": row[7],
                    "is_symlink": row[8],
                    "content_owner_id": row[9]
                }
                files.append(file)
            self.logger.debug(f"Found {len(files)} files with status in {status_list}")
            return files
        except sqlite3.Error as e:
            self.logger.error(f"Error getting files by status: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def insert_file(self, name, path, size, file_type, status, parent_id, hash_value=None, is_symlink=0, content_owner_id=None):
        """
        Inserts a new file or folder into the database.

        Args:
            name (str): The name of the file or folder.
            path (str): The absolute path of the file or folder.
            size (int): The size of the file or folder in bytes.
            file_type (str): The type of the entry ('file' or 'folder').
            status (str): The status of the entry ('pending', 'selected', 'copying', 'success', 'failed').
            parent_id (int): The ID of the parent folder.
            hash_value (str, optional): The hash of the file content. Defaults to None.
            is_symlink (int, optional): 1 if the entry is a symlink, 0 otherwise. Defaults to 0.
            content_owner_id (int, optional): The ID of the original file for duplicates. Defaults to None.
        """
        self.logger.debug(f"Inserting file: {name}, path: {path}, type: {file_type}, status: {status}")
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO files (name, path, size, type, status, parent_id, hash, is_symlink, content_owner_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, path, size, file_type, status, parent_id, hash_value, is_symlink, content_owner_id))
            conn.commit()
            self.logger.debug(f"File inserted successfully: {name}")
        except sqlite3.Error as e:
            self.logger.error(f"Error inserting file: {e}")
        finally:
            if conn:
                conn.close()

    def update_file_status(self, file_id, status):
        """
        Updates the status of a file or folder in the database.

        Args:
            file_id (int): The ID of the file or folder to update.
            status (str): The new status of the file or folder.
        """
        self.logger.debug(f"Updating file status: id: {file_id}, status: {status}")
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE files SET status = ? WHERE id = ?", (status, file_id))
            conn.commit()
            self.logger.debug(f"File status updated successfully: id: {file_id}, status: {status}")
        except sqlite3.Error as e:
            self.logger.error(f"Error updating file status: {e}")
        finally:
            if conn:
                conn.close()

    def update_file_hash(self, file_id, hash_value):
        """
        Updates the hash of a file in the database.

        Args:
            file_id (int): The ID of the file to update.
            hash_value (str): The new hash value of the file.
        """
        self.logger.debug(f"Updating file hash: id: {file_id}")
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE files SET hash = ? WHERE id = ?", (hash_value, file_id))
            conn.commit()
            self.logger.debug(f"File hash updated successfully: id: {file_id}")
        except sqlite3.Error as e:
            self.logger.error(f"Error updating file hash: {e}")
        finally:
            if conn:
                conn.close()

    def update_file_content_owner(self, file_id, content_owner_id):
        """
        Updates the content owner of a file in the database.

        Args:
            file_id (int): The ID of the file to update.
            content_owner_id (int): The ID of the content owner.
        """
        self.logger.debug(f"Updating file content owner: id: {file_id}, content_owner_id: {content_owner_id}")
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE files SET content_owner_id = ? WHERE id = ?", (content_owner_id, file_id))
            conn.commit()
            self.logger.debug(f"File content owner updated successfully: id: {file_id}, content_owner_id: {content_owner_id}")
        except sqlite3.Error as e:
            self.logger.error(f"Error updating file content owner: {e}")
        finally:
            if conn:
                conn.close()

    def get_file_by_path(self, path):
        """
        Retrieves a file from the database based on its path.

        Args:
            path (str): The path of the file to retrieve.

        Returns:
            dict: A dictionary representing the file, or None if not found.
        """
        self.logger.debug(f"Getting file by path: {path}")
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM files WHERE path = ?", (path,))
            row = cursor.fetchone()
            if row:
                file = {
                    "id": row[0],
                    "name": row[1],
                    "path": row[2],
                    "size": row[3],
                    "type": row[4],
                    "status": row[5],
                    "parent_id": row[6],
                    "hash": row[7],
                    "is_symlink": row[8],
                    "content_owner_id": row[9]
                }
                self.logger.debug(f"File found: {file}")
                return file
            else:
                self.logger.debug(f"File not found: {path}")
                return None
        except sqlite3.Error as e:
            self.logger.error(f"Error getting file by path: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def get_all_files(self):
        """
        Retrieves all files from the database.

        Returns:
            list: A list of dictionaries, each representing a file.
        """
        self.logger.debug("Getting all files")
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM files")
            rows = cursor.fetchall()
            files = []
            for row in rows:
                file = {
                    "id": row[0],
                    "name": row[1],
                    "path": row[2],
                    "size": row[3],
                    "type": row[4],
                    "status": row[5],
                    "parent_id": row[6],
                    "hash": row[7],
                    "is_symlink": row[8],
                    "content_owner_id": row[9]
                }
                files.append(file)
            self.logger.debug(f"Found {len(files)} files")
            return files
        except sqlite3.Error as e:
            self.logger.error(f"Error getting all files: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_children(self, parent_id):
        """
        Retrieves all children of a given parent ID.

        Args:
            parent_id (int): The ID of the parent folder.

        Returns:
            list: A list of dictionaries, each representing a child file or folder.
        """
        self.logger.debug(f"Getting children for parent_id: {parent_id}")
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM files WHERE parent_id = ?", (parent_id,))
            rows = cursor.fetchall()
            children = []
            for row in rows:
                child = {
                    "id": row[0],
                    "name": row[1],
                    "path": row[2],
                    "size": row[3],
                    "type": row[4],
                    "status": row[5],
                    "parent_id": row[6],
                    "hash": row[7],
                    "is_symlink": row[8],
                    "content_owner_id": row[9]
                }
                children.append(child)
            self.logger.debug(f"Found {len(children)} children for parent_id: {parent_id}")
            return children
        except sqlite3.Error as e:
            self.logger.error(f"Error getting children for parent_id: {e}")
            return []
        finally:
            if conn:
                conn.close()
