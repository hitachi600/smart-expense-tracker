"""
Unit tests for JSON and CSV storage implementations.
"""

import os
import pytest
from src.storage.json_storage import JSONStorage
from src.storage.csv_storage import CSVStorage


@pytest.fixture
def temp_json_file(tmp_path):
    return str(tmp_path / "test_expenses.json")


@pytest.fixture
def temp_csv_file(tmp_path):
    return str(tmp_path / "test_expenses.csv")


class TestJSONStorage:
    def test_save_and_load(self, temp_json_file):
        storage = JSONStorage(temp_json_file)
        sample = [
            {"id": 1, "title": "Coffee", "amount": 4.50, "category": "Food & Dining", "date": "2026-03-01", "payment_method": "UPI / Online", "notes": ""},
            {"id": 2, "title": "Taxi", "amount": 15.00, "category": "Transportation", "date": "2026-03-02", "payment_method": "Cash", "notes": ""}
        ]

        # Save data
        assert storage.save(sample) is True
        assert os.path.exists(temp_json_file)

        # Load data
        loaded = storage.load()
        assert len(loaded) == 2
        assert loaded[0]["title"] == "Coffee"
        assert loaded[1]["amount"] == 15.00

    def test_load_empty_file_returns_empty_list(self, temp_json_file):
        storage = JSONStorage(temp_json_file)
        assert storage.load() == []

    def test_backup_creation(self, temp_json_file):
        storage = JSONStorage(temp_json_file)
        storage.save([{"id": 1, "title": "Gym", "amount": 50.0, "category": "Healthcare", "date": "2026-01-01", "payment_method": "Card", "notes": ""}])

        backup_path = storage.create_backup()
        assert os.path.exists(backup_path)
        assert "backup" in backup_path


class TestCSVStorage:
    def test_csv_save_and_load(self, temp_csv_file):
        storage = CSVStorage(temp_csv_file)
        sample = [
            {"id": 1, "title": "Groceries", "amount": 65.20, "category": "Food & Dining", "date": "2026-03-10", "payment_method": "Credit Card", "notes": "Weekly"},
            {"id": 2, "title": "Subway", "amount": 2.50, "category": "Transportation", "date": "2026-03-11", "payment_method": "Debit Card", "notes": ""}
        ]

        assert storage.save(sample) is True
        assert os.path.exists(temp_csv_file)

        loaded = storage.load()
        assert len(loaded) == 2
        assert loaded[0]["title"] == "Groceries"
        assert loaded[0]["amount"] == 65.20
        assert loaded[1]["category"] == "Transportation"
