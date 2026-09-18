"""
Unit tests for ExpenseManager CRUD operations, searching, filtering, and sorting.
"""

import pytest
from src.services.expense_manager import ExpenseManager
from src.storage.json_storage import JSONStorage
from src.utils.validators import ExpenseNotFoundError


@pytest.fixture
def manager(tmp_path):
    json_file = str(tmp_path / "expenses_test.json")
    storage = JSONStorage(json_file)
    return ExpenseManager(storage=storage)


class TestExpenseManager:
    def test_add_and_get_expense(self, manager):
        exp = manager.add_expense("Lunch", 15.50, "Food & Dining", date="2026-03-01")
        assert exp.id == 1
        assert exp.title == "Lunch"
        assert exp.amount == 15.50

        fetched = manager.get_expense(1)
        assert fetched.id == exp.id
        assert fetched.title == exp.title

    def test_get_nonexistent_expense_raises_error(self, manager):
        with pytest.raises(ExpenseNotFoundError):
            manager.get_expense(999)

    def test_update_expense(self, manager):
        exp = manager.add_expense("Old Name", 20.00, "Shopping")
        updated = manager.update_expense(exp.id, title="New Name", amount=25.00)
        assert updated.title == "New Name"
        assert updated.amount == 25.00

        refetched = manager.get_expense(exp.id)
        assert refetched.title == "New Name"
        assert refetched.amount == 25.00

    def test_delete_expense(self, manager):
        exp1 = manager.add_expense("Item 1", 10.0, "Food & Dining")
        exp2 = manager.add_expense("Item 2", 20.0, "Transportation")
        assert manager.count() == 2

        deleted = manager.delete_expense(exp1.id)
        assert deleted.id == exp1.id
        assert manager.count() == 1

        with pytest.raises(ExpenseNotFoundError):
            manager.get_expense(exp1.id)

    def test_search_expenses(self, manager):
        manager.add_expense("Netflix Subscription", 15.0, "Entertainment", notes="monthly bill")
        manager.add_expense("Groceries", 60.0, "Food & Dining", notes="vegetables")
        manager.add_expense("Spotify Premium", 10.0, "Entertainment", notes="music")

        # Search by title keyword
        results = manager.search_expenses("netflix")
        assert len(results) == 1
        assert results[0].title == "Netflix Subscription"

        # Search by category
        results_cat = manager.search_expenses("Entertainment")
        assert len(results_cat) == 2

        # Search by notes
        results_notes = manager.search_expenses("vegetables")
        assert len(results_notes) == 1

    def test_filter_expenses(self, manager):
        manager.add_expense("Coffee", 5.0, "Food & Dining", date="2026-03-01", payment_method="Cash")
        manager.add_expense("Dinner", 50.0, "Food & Dining", date="2026-03-05", payment_method="Credit Card")
        manager.add_expense("Train", 30.0, "Transportation", date="2026-03-10", payment_method="Credit Card")

        # Filter by category
        food_only = manager.filter_expenses(category="Food & Dining")
        assert len(food_only) == 2

        # Filter by amount range
        mid_amt = manager.filter_expenses(min_amount=10.0, max_amount=40.0)
        assert len(mid_amt) == 1
        assert mid_amt[0].title == "Train"

        # Filter by date range
        date_filtered = manager.filter_expenses(start_date="2026-03-02", end_date="2026-03-08")
        assert len(date_filtered) == 1
        assert date_filtered[0].title == "Dinner"

    def test_sort_expenses(self, manager):
        manager.add_expense("A", 100.0, "Shopping", date="2026-03-03")
        manager.add_expense("B", 20.0, "Shopping", date="2026-03-01")
        manager.add_expense("C", 50.0, "Shopping", date="2026-03-02")

        # Sort by amount ascending
        sorted_amt = manager.sort_expenses(by="amount", reverse=False)
        assert [e.amount for e in sorted_amt] == [20.0, 50.0, 100.0]

        # Sort by date ascending
        sorted_date = manager.sort_expenses(by="date", reverse=False)
        assert [e.date for e in sorted_date] == ["2026-03-01", "2026-03-02", "2026-03-03"]

    def test_populate_sample_data(self, manager):
        count = manager.populate_sample_data(count=20, days_back=30)
        assert count == 20
        assert manager.count() == 20
        assert manager.get_total_spent() > 0
