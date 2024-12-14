# src/gui/progress_bar.py
"""
This file contains the ProgressBar class, which is responsible for
displaying the progress bar in the GUI.
"""
import tkinter as tk
from tkinter import ttk
import logging

class ProgressBar(ttk.Frame):
    """
    Displays the progress bar in the GUI.
    """
    def __init__(self, parent, config):
        """
        Initializes the ProgressBar with the parent widget and configuration.

        Args:
            parent (tk.Widget): The parent widget.
            config (dict): A dictionary containing the application configuration.
        """
        super().__init__(parent)
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.logger.debug("ProgressBar initialized")

        self.progress = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)
        self.progress_label = ttk.Label(self, text="Progress: 0%")
        self.progress_label.pack()
        self.current_file_label = ttk.Label(self, text="")
        self.current_file_label.pack()
        self.pack(fill=tk.X, padx=10)

    def update_progress(self, percentage, message):
        """
        Updates the progress bar with the current percentage and message.

        Args:
            percentage (float): The current percentage of progress.
            message (str): The message to display.
        """
        self.progress["value"] = percentage
        self.progress_label.config(text=f"Progress: {percentage:.2f}%")
        self.current_file_label.config(text=message)
        self.update_idletasks()
        self.logger.debug(f"Progress updated: {percentage:.2f}%, Message: {message}")
