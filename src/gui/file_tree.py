# src/gui/file_tree.py
"""
This file contains the FileTree class, which is responsible for
displaying the file tree in the GUI.
"""
import tkinter as tk
from tkinter import ttk
import logging
import os

class FileTree(ttk.Treeview):
    """
    Displays the file tree in the GUI.
    """
    def __init__(self, parent, config, db_manager, update_size_labels):
        """
        Initializes the FileTree with the parent widget, configuration, database manager, and update size labels function.

        Args:
            parent (tk.Widget): The parent widget.
            config (dict): A dictionary containing the application configuration.
            db_manager (DatabaseManager): An instance of the DatabaseManager class.
            update_size_labels (function): A function to update the size labels.
        """
        super().__init__(parent, columns=("size", "type"), show="tree", selectmode="none")
        self.config = config
        self.db_manager = db_manager
        self.update_size_labels = update_size_labels
        self.logger = logging.getLogger(__name__)
        self.logger.debug("FileTree initialized")

        self.heading("#0", text="File/Folder")
        self.heading("size", text="Size")
        self.column("size", width=100, anchor="e")
        self.column("type", width=0, stretch=False) # Hidden column for type

        self.bind("<Button-1>", self.on_item_click)
        self.item_checkbox_states = {}
        self.item_sizes = {}

    def load_from_database(self):
        """
        Loads the file tree from the database.
        """
        self.logger.info("Loading file tree from database")
        self.delete(*self.get_children())
        files = self.db_manager.get_all_files()
        self.item_checkbox_states = {}
        self.item_sizes = {}
        self.insert_items(files)
        self.logger.info("File tree loaded from database")

    def insert_items(self, files, parent_id=None, parent_iid=""):
        """
        Recursively inserts items into the file tree.

        Args:
            files (list): A list of dictionaries, each representing a file or folder.
            parent_id (int, optional): The ID of the parent folder. Defaults to None.
            parent_iid (str, optional): The IID of the parent item. Defaults to "".
        """
        for file in files:
            if file["parent_id"] == parent_id:
                file_name = file["name"]
                file_size = file["size"]
                file_type = file["type"]
                file_id = file["id"]
                iid = self.insert(parent_iid, "end", text=file_name, values=(file_size, file_type), open=False)
                self.item_checkbox_states[iid] = False
                self.item_sizes[iid] = file_size
                self.insert_items(files, file_id, iid)

    def on_item_click(self, event):
        """
        Handles the click event on a file tree item.

        Args:
            event (tk.Event): The click event.
        """
        item_iid = self.identify_row(event.y)
        if item_iid:
            self.toggle_checkbox(item_iid)
            self.update_size_labels()

    def toggle_checkbox(self, item_iid):
        """
        Toggles the checkbox state of a file tree item.

        Args:
            item_iid (str): The IID of the item.
        """
        self.item_checkbox_states[item_iid] = not self.item_checkbox_states[item_iid]
        if self.item_checkbox_states[item_iid]:
            self.item(item_iid, tags=("selected",))
        else:
            self.item(item_iid, tags=("unselected",))
        self.tag_configure("selected", background="#a0ffa0")
        self.tag_configure("unselected", background="#ffffff")
        self.logger.debug(f"Toggled checkbox for item: {item_iid}, state: {self.item_checkbox_states[item_iid]}")

    def calculate_total_sizes(self):
        """
        Calculates the total size of selected and unselected files and folders.

        Returns:
            tuple: A tuple containing the total selected size and total unselected size.
        """
        self.logger.debug("Calculating total sizes")
        selected_size = 0
        unselected_size = 0
        for iid, is_selected in self.item_checkbox_states.items():
            if is_selected:
                selected_size += self.item_sizes[iid]
            else:
                unselected_size += self.item_sizes[iid]
        self.logger.debug(f"Total sizes calculated: Selected: {selected_size}, Unselected: {unselected_size}")
        return selected_size, unselected_size

    def get_selected_files(self):
        """
        Gets a list of selected files and folders.

        Returns:
            list: A list of dictionaries, each representing a selected file or folder.
        """
        self.logger.debug("Getting selected files")
        selected_files = []
        for iid, is_selected in self.item_checkbox_states.items():
            if is_selected:
                item_values = self.item(iid)
                file_name = item_values["text"]
                file_size = item_values["values"][0]
                file_type = item_values["values"][1]
                file_path = self.get_file_path_from_iid(iid)
                file_data = self.db_manager.get_file_by_path(file_path)
                if file_data:
                    selected_files.append(file_data)
        self.logger.debug(f"Found {len(selected_files)} selected files")
        return selected_files

    def get_file_path_from_iid(self, iid):
        """
        Gets the file path from the item IID.

        Args:
            iid (str): The IID of the item.

        Returns:
            str: The file path.
        """
        self.logger.debug(f"Getting file path from iid: {iid}")
        item_values = self.item(iid)
        file_name = item_values["text"]
        parent_iid = self.parent(iid)
        if parent_iid:
            parent_path = self.get_file_path_from_iid(parent_iid)
            file_path = os.path.join(parent_path, file_name)
        else:
            file_path = os.path.join(self.config.get("MOUNTED_PATH"), file_name)
        self.logger.debug(f"File path found: {file_path}")
        return file_path
