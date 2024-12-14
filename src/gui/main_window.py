# src/gui/main_window.py
"""
This file contains the MainWindow class, which is responsible for
creating and managing the main GUI window of the application.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import logging
import os
from core.file_scanner import FileScanner
from core.backup_manager import BackupManager
from utils.hash_calculator import HashCalculator
from gui.file_tree import FileTree
from gui.progress_bar import ProgressBar
import subprocess

class MainWindow(tk.Tk):
    """
    Creates and manages the main GUI window of the application.
    """
    def __init__(self, config, db_manager):
        """
        Initializes the main window with the application configuration and database manager.

        Args:
            config (dict): A dictionary containing the application configuration.
            db_manager (DatabaseManager): An instance of the DatabaseManager class.
        """
        super().__init__()
        self.config = config
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        self.logger.debug("MainWindow initialized")

        self.title("Effortless Backup")
        self.geometry("800x600")
        self.configure(bg=self.config.get("PRIMARY_COLOR", "#ffffff"))

        self.file_scanner = FileScanner(self.config, self.db_manager)
        self.backup_manager = BackupManager(self.config, self.db_manager)
        self.hash_calculator = HashCalculator()
        self.progress_bar = ProgressBar(self, self.config)

        self.file_tree = None
        self.total_selected_size_label = None
        self.total_unselected_size_label = None
        self.create_widgets()
        self.check_previous_backup()

    def create_widgets(self):
        """
        Creates all the widgets for the main window.
        """
        self.logger.debug("Creating widgets")
        # File Tree Frame
        tree_frame = ttk.Frame(self)
        tree_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # File Tree
        self.file_tree = FileTree(tree_frame, self.config, self.db_manager, self.update_size_labels)
        self.file_tree.pack(fill=tk.BOTH, expand=True)

        # Summary Frame
        summary_frame = ttk.Frame(self)
        summary_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        # Total Selected Size Label
        self.total_selected_size_label = ttk.Label(summary_frame, text="Total Selected Size: 0 bytes", font=("Arial", 10))
        self.total_selected_size_label.pack(pady=5)

        # Total Unselected Size Label
        self.total_unselected_size_label = ttk.Label(summary_frame, text="Total Unselected Size: 0 bytes", font=("Arial", 10))
        self.total_unselected_size_label.pack(pady=5)

        # Browse Button
        browse_button = ttk.Button(summary_frame, text="Browse", command=self.browse_folder)
        browse_button.pack(pady=10)

        # Scan Device Button
        scan_device_button = ttk.Button(summary_frame, text="Scan Device", command=self.scan_device)
        scan_device_button.pack(pady=10)

        # Start Backup Button
        start_backup_button = ttk.Button(summary_frame, text="Start Backup", command=self.start_backup)
        start_backup_button.pack(pady=10)

        # Find Duplicates Button
        find_duplicates_button = ttk.Button(summary_frame, text="Find Duplicates", command=self.find_duplicates)
        find_duplicates_button.pack(pady=10)

        # Size Threshold Input
        self.size_threshold_entry = ttk.Entry(summary_frame)
        self.size_threshold_entry.insert(0, "10")  # Default value of 10 MB
        self.size_threshold_entry.pack(pady=5)
        size_threshold_label = ttk.Label(summary_frame, text="Size Threshold (MB)")
        size_threshold_label.pack(pady=5)

        self.logger.debug("Widgets created successfully")

    def browse_folder(self):
        """
        Lists connected devices using ADB and allows the user to select one.
        """
        self.logger.info("Listing connected devices using ADB")
        try:
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, check=True)
            devices = result.stdout.strip().split('\n')[1:]  # Skip the "List of devices attached" line
            if not devices:
                messagebox.showerror("Error", "No devices found using ADB.")
                self.logger.error("No devices found using ADB.")
                return

            device_names = [device.split('\t')[0] for device in devices]
            selected_device = simpledialog.askstring("Input", "Select a device:", initialvalue=device_names[0] if device_names else "")
            if not selected_device:
                self.logger.warning("No device selected.")
                return

            if selected_device not in device_names:
                messagebox.showerror("Error", "Invalid device selected.")
                self.logger.error(f"Invalid device selected: {selected_device}")
                return

            self.logger.info(f"Device selected: {selected_device}")
            
            # Get the device's external storage path
            result = subprocess.run(['adb', '-s', selected_device, 'shell', 'echo $EXTERNAL_STORAGE'], capture_output=True, text=True, check=True)
            device_path = result.stdout.strip()
            self.logger.info(f"Device path: {device_path}")
            self.config["MOUNTED_PATH"] = device_path
            messagebox.showinfo("Device Selected", f"Selected device: {selected_device}, Path: {device_path}")

        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"ADB command failed: {e}")
            self.logger.error(f"ADB command failed: {e}")
        except Exception as e:
             messagebox.showerror("Error", f"An unexpected error occurred: {e}")
             self.logger.error(f"An unexpected error occurred: {e}")

    def check_previous_backup(self):
        """
        Checks if a previous backup was in progress and prompts the user to continue or start fresh.
        """
        self.logger.debug("Checking for previous backup")
        if self.db_manager.check_previous_backup():
            response = messagebox.askyesno(
                "Previous Backup", 
                "A previous backup was in progress. Do you want to continue or start fresh?"
            )
            if response:
                self.logger.info("Continuing previous backup")
                self.db_manager.clear_previous_backup()
            else:
                self.logger.info("Starting fresh backup")
                self.db_manager.clear_previous_backup()
        else:
            self.logger.info("No previous backup found")

    def update_size_labels(self):
        """
        Updates the total selected and unselected size labels.
        """
        self.logger.debug("Updating size labels")
        selected_size, unselected_size = self.db_manager.calculate_total_sizes()
        if self.total_selected_size_label:
            self.total_selected_size_label.config(text=f"Total Selected Size: {selected_size} bytes")
        if self.total_unselected_size_label:
            self.total_unselected_size_label.config(text=f"Total Unselected Size: {unselected_size} bytes")
        self.logger.debug(f"Size labels updated: Selected: {selected_size}, Unselected: {unselected_size}")

    def start_backup(self):
        """
        Starts the backup process.
        """
        self.logger.info("Starting backup process")
        selected_files = self.db_manager.get_selected_files()
        if not selected_files:
            messagebox.showinfo("No Files Selected", "Please select files to backup.")
            return

        total_size = sum(file["size"] for file in selected_files)
        backup_destination = self.config.get("BACKUP_DESTINATION")
        free_space = self.backup_manager.get_free_space(backup_destination)

        if free_space < total_size:
            messagebox.showerror(
                "Insufficient Space", 
                f"Not enough free space in the backup destination. Required: {total_size} bytes, Available: {free_space} bytes"
            )
            return

        self.backup_manager.backup_files(selected_files, self.progress_bar)
        self.logger.info("Backup process completed")

    def find_duplicates(self):
        """
        Starts the duplicate detection process.
        """
        self.logger.info("Starting duplicate detection process")
        try:
            size_threshold_mb = int(self.size_threshold_entry.get())
            size_threshold_bytes = size_threshold_mb * 1024 * 1024
            self.file_scanner.find_duplicates(size_threshold_bytes, self.progress_bar, self.hash_calculator)
            messagebox.showinfo("Duplicate Detection", "Duplicate detection completed.")
            self.logger.info("Duplicate detection completed")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for the size threshold.")
            self.logger.error("Invalid size threshold input")

    def scan_device(self):
        """
        Starts the device scanning process.
        """
        self.logger.info("Starting device scanning process")
        mounted_path = self.config.get("MOUNTED_PATH")
        if not mounted_path or not os.path.exists(mounted_path):
            self.logger.error("MOUNTED_PATH is not set or invalid. Please select a folder.")
            messagebox.showerror("Error", "Please select a valid folder to scan.")
            return

        self.file_scanner.scan_directory(mounted_path)
        if self.file_tree:
            self.file_tree.load_from_database()
        else:
            self.logger.error("FileTree is not initialized. Cannot load from database.")
            messagebox.showerror("Error`", "File tree is not initialized. Please restart the application.")
            self.logger.info("Device scanning process completed")
