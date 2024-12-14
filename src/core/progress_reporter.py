# src/core/progress_reporter.py
"""
This file contains the ProgressReporter class, which is responsible for
reporting progress during long-running operations.
"""
import logging

class ProgressReporter:
    """
    Reports progress during long-running operations.
    """
    def __init__(self, progress_bar, total_steps, operation_name):
        """
        Initializes the ProgressReporter with the progress bar, total steps, and operation name.

        Args:
            progress_bar (ProgressBar): An instance of the ProgressBar class.
            total_steps (int): The total number of steps in the operation.
            operation_name (str): The name of the operation.
        """
        self.progress_bar = progress_bar
        self.total_steps = total_steps
        self.current_step = 0
        self.operation_name = operation_name
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"ProgressReporter initialized for {operation_name}")

    def update_progress(self, step, message):
        """
        Updates the progress bar with the current step and message.

        Args:
            step (int): The current step in the operation.
            message (str): The message to display.
        """
        self.current_step = step
        percentage = (step / self.total_steps) * 100 if self.total_steps > 0 else 0
        self.progress_bar.update_progress(percentage, message)
        self.logger.debug(f"{self.operation_name} progress: {percentage:.2f}%, Step: {step}/{self.total_steps}, Message: {message}")

    def finish(self):
        """
        Finishes the progress reporting and updates the progress bar to 100%.
        """
        self.update_progress(self.total_steps, f"{self.operation_name} completed")
        self.logger.debug(f"{self.operation_name} finished")
