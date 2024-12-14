# Effortless Backup with Duplicate Detection

This application provides a GUI for backing up files from a mounted drive, with features for duplicate detection and handling.

## Setup Instructions

1. **Clone the repository:**
```bash
git clone https://github.com/charlpcronje/Effortless-Backup-with-Duplicate-Detection.git
cd Effortless-Backup-with-Duplicate-Detection
```

2. **Create a virtual environment (optional but recommended):**
```bash
python -m venv venv
source venv/bin/activate  # On Linux/macOS
venv\Scripts\activate  # On Windows
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure the application:**
- Create a `.env` file in the root directory of the project.
- Add the following environment variables to the `.env` file:
```
MOUNTED_PATH=/mnt/phone_storage  # The root path of the mounted directory to scan.
BACKUP_DESTINATION=/mnt/backup_destination  # The directory where the files will be backed up.
APP_THEME=light  # Light or dark theme colors for the app (light or dark).
PRIMARY_COLOR=#ffffff  # Primary color for the app.
SECONDARY_COLOR=#000000  # Secondary color for the app.
PROGRESS_BAR_COLOR=#00ff00  # The color of the progress bar.
LOG_LEVEL=DEBUG # Logging level (DEBUG, INFO, ERROR)
LOG_FILE_PATH=app.log # Path to the log file
```
 - Modify the values to match your desired settings.

1. **Run the application:**
```bash
python src/main.py
```

## Features

- **File Tree with Checkboxes:** Displays a file tree of the mounted directory with checkboxes for selection.
- **File and Folder Details:** Displays the size of each file and folder, as well as the total size of selected and unselected items.
- **Settings from .env File:** Reads settings from a `.env` file for customization.
- **Backup Process:** Copies selected files and folders to the specified backup destination with a progress bar.
- **Database Integration:** Uses a SQLite database to store file information and backup progress.
- **Duplicate Detection:** Detects duplicate files using SHA-256 hashes and creates symbolic links for duplicates.
- **GUI Features:** Uses tkinter to create a user interface with a file tree, progress bar, and buttons.
- **Error Handling:** Displays errors in the GUI and logs them in the database and log file.
- **Performance Optimization:** Uses the SQLite database as the source of truth for fast loading and dynamic calculations.

## Advanced Features

- **Pausing and Resuming:** (Not yet implemented)
- **Summary Report:** (Not yet implemented)

## File Structure

```
Effortless-Backup-with-Duplicate-Detection/
├── .env
├── README.md
├── requirements.txt
├── src/
│   ├── main.py
│   ├── core/
│   │   ├── file_scanner.py
│   │   ├── backup_manager.py
│   │   ├── progress_reporter.py
│   ├── database/
│   │   ├── database_manager.py
│   ├── gui/
│   │   ├── main_window.py
│   │   ├── file_tree.py
│   │   ├── progress_bar.py
│   ├── utils/
│   │   ├── config_loader.py
│   │   ├── hash_calculator.py
```

## Programming Rules

1.  **File Organization**:
-   Each file must start with a comment on the first line indicating its **relative path and filename** (e.g., `# src/gui/file_tree.py`).
-   The app must be **modular**:
    -   Split the code into **small files** with one class per file.
    -   Group related features into appropriate directories.

2.  **Class-Based Design**:
-   The entire app must use **class-based programming**, not function-based programming.
-   Each feature or component should have its own class.
-   Avoid global variables or tightly coupled code.

3.  **Comprehensive Comments**:
-   Add comments at:
    -   **File level**: Briefly explain the purpose of the file.
    -   **Class level**: Explain what the class does and why it exists.
    -   **Method level**: Document the purpose of the method, its parameters, return values, and any exceptions it might raise.

4.  **Error Checking and Handling**:
-   All methods and operations must include **full error checking and handling**.
-   Use Python's built-in exceptions (e.g., `FileNotFoundError`, `PermissionError`) or custom exceptions where appropriate.
-   Ensure the app gracefully handles unexpected errors without crashing.

5.  **Logging**:
-   Implement logging with the following features:
    -   Write logs to both the **terminal** and a **log file**.
    -   Include at least **one log entry per method** to trace the app’s execution flow.
    -   Make logging configurable via the `.env` file with settings for:
        -   `LOG_LEVEL` (e.g., `DEBUG`, `INFO`, `ERROR`).
        -   `LOG_FILE_PATH` for the location of the log file.
-   Use Python's `logging` module for consistent and structured log messages.

6.  **Production-Ready Code**:
-   The app must be fully **production-ready**, with no placeholders or omissions.
-   If a feature cannot be implemented (e.g., unsupported by Python), explain why and suggest an alternative.

7.  **Deliverables**:
-   Provide all files with **complete code**—do not omit sections or leave incomplete placeholders.
-   Give a `requirements.txt` file with a `README.md` file.
