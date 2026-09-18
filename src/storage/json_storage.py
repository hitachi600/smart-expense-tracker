"""
JSON Storage implementation with atomic writes and backup management.
Demonstrates: File Handling, JSON Serialization, Context Managers, Error Handling, Inheritance.
"""

import json
import os
import shutil
from datetime import datetime
from typing import List, Dict, Any
from .storage_interface import StorageInterface
from ..utils.validators import StorageError


class JSONStorage(StorageInterface):
    """
    Handles JSON file storage for expense records and budget configuration.
    """

    def __init__(self, file_path: str = "data/expenses.json"):
        self.file_path = file_path
        self._ensure_directory_exists()

    def _ensure_directory_exists(self) -> None:
        """Creates parent directory if it does not exist."""
        directory = os.path.dirname(self.file_path)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except OSError as err:
                raise StorageError(f"Failed to create storage directory '{directory}': {err}") from err

    def load(self) -> List[Dict[str, Any]]:
        """
        Loads expense records from the JSON file.
        If file does not exist, creates an empty list and returns it.
        """
        if not os.path.exists(self.file_path):
            return []

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []
                data = json.loads(content)
                if not isinstance(data, list):
                    raise StorageError(f"Expected JSON list in '{self.file_path}', got {type(data).__name__}.")
                return data
        except json.JSONDecodeError as err:
            raise StorageError(f"Corrupt JSON data in '{self.file_path}': {err}") from err
        except OSError as err:
            raise StorageError(f"Read error for '{self.file_path}': {err}") from err

    def save(self, data: List[Dict[str, Any]]) -> bool:
        """
        Atomically saves records to the JSON file using a temporary file.
        """
        self._ensure_directory_exists()
        temp_path = f"{self.file_path}.tmp"
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Atomic replacement
            if os.path.exists(self.file_path):
                os.replace(temp_path, self.file_path)
            else:
                os.rename(temp_path, self.file_path)
            return True
        except (OSError, TypeError) as err:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            raise StorageError(f"Failed to write data to '{self.file_path}': {err}") from err

    def create_backup(self) -> str:
        """
        Creates a timestamped snapshot of the current data file in `data/backups/`.
        """
        if not os.path.exists(self.file_path):
            raise StorageError(f"Cannot backup non-existent file '{self.file_path}'.")

        backup_dir = os.path.join(os.path.dirname(self.file_path), "backups")
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.basename(self.file_path)
        name, ext = os.path.splitext(base_name)
        backup_filename = f"{name}_backup_{timestamp}{ext}"
        backup_path = os.path.join(backup_dir, backup_filename)

        try:
            shutil.copy2(self.file_path, backup_path)
            return backup_path
        except OSError as err:
            raise StorageError(f"Backup failed: {err}") from err
