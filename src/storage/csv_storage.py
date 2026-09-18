"""
CSV Storage and Export/Import Implementation.
Demonstrates: CSV DictReader/DictWriter, File handling, Data transformation, Error Handling.
"""

import csv
import os
import shutil
from datetime import datetime
from typing import List, Dict, Any
from .storage_interface import StorageInterface
from ..utils.validators import StorageError


class CSVStorage(StorageInterface):
    """
    Handles CSV persistence and export/import operations.
    """

    CSV_HEADERS = ["ID", "Date", "Title", "Category", "Amount", "Payment Method", "Notes"]

    def __init__(self, file_path: str = "data/expenses.csv"):
        self.file_path = file_path
        self._ensure_directory_exists()

    def _ensure_directory_exists(self) -> None:
        directory = os.path.dirname(self.file_path)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except OSError as err:
                raise StorageError(f"Failed to create directory '{directory}': {err}") from err

    def load(self) -> List[Dict[str, Any]]:
        """
        Loads expense records from CSV.
        """
        if not os.path.exists(self.file_path):
            return []

        records = []
        try:
            with open(self.file_path, "r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if not row.get("ID"):
                        continue
                    records.append({
                        "id": int(row["ID"]),
                        "date": row["Date"],
                        "title": row["Title"],
                        "category": row["Category"],
                        "amount": float(row["Amount"]),
                        "payment_method": row.get("Payment Method", "UPI / Online"),
                        "notes": row.get("Notes", "")
                    })
            return records
        except (csv.Error, ValueError, KeyError, OSError) as err:
            raise StorageError(f"Failed to load CSV file '{self.file_path}': {err}") from err

    def save(self, data: List[Dict[str, Any]]) -> bool:
        """
        Writes list of expense dictionaries into CSV format.
        """
        self._ensure_directory_exists()
        try:
            with open(self.file_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.CSV_HEADERS)
                writer.writeheader()
                for item in data:
                    writer.writerow({
                        "ID": item.get("id"),
                        "Date": item.get("date"),
                        "Title": item.get("title"),
                        "Category": item.get("category"),
                        "Amount": f"{float(item.get('amount', 0)):.2f}",
                        "Payment Method": item.get("payment_method", "UPI / Online"),
                        "Notes": item.get("notes", "")
                    })
            return True
        except (csv.Error, OSError) as err:
            raise StorageError(f"Failed to save CSV file '{self.file_path}': {err}") from err

    def create_backup(self) -> str:
        """
        Creates a timestamped CSV backup in `data/backups/`.
        """
        if not os.path.exists(self.file_path):
            raise StorageError(f"Cannot backup non-existent file '{self.file_path}'.")

        backup_dir = os.path.join(os.path.dirname(self.file_path), "backups")
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"expenses_backup_{timestamp}.csv")

        try:
            shutil.copy2(self.file_path, backup_path)
            return backup_path
        except OSError as err:
            raise StorageError(f"Backup failed: {err}") from err
