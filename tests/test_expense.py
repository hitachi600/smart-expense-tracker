"""
Unit tests for Expense model, validation, and serialization.
"""

import pytest
from src.models.expense import Expense
from src.models.category import Category, DEFAULT_CATEGORIES
from src.models.budget import Budget, CategoryBudget
from src.utils.validators import (
    ValidationError,
    InvalidExpenseError,
    validate_date,
    validate_amount,
    validate_category
)


class TestExpenseModel:
    """Test suite for the Expense domain model."""

    def test_valid_expense_creation(self):
        exp = Expense(
            expense_id=1,
            title="Groceries at Whole Foods",
            amount=85.50,
            category="Food & Dining",
            date="2026-03-15",
            payment_method="Credit Card",
            notes="Weekly grocery run"
        )
        assert exp.id == 1
        assert exp.title == "Groceries at Whole Foods"
        assert exp.amount == 85.50
        assert exp.category == "Food & Dining"
        assert exp.date == "2026-03-15"
        assert exp.payment_method == "Credit Card"
        assert exp.notes == "Weekly grocery run"
        assert exp.year == 2026
        assert exp.month == 3
        assert exp.year_month == "2026-03"

    def test_invalid_amount_raises_error(self):
        with pytest.raises(InvalidExpenseError):
            Expense(expense_id=1, title="Coffee", amount=-5.0, category="Food & Dining")

        with pytest.raises(InvalidExpenseError):
            Expense(expense_id=1, title="Coffee", amount=0, category="Food & Dining")

        with pytest.raises(InvalidExpenseError):
            Expense(expense_id=1, title="Coffee", amount="invalid_number", category="Food & Dining")

    def test_invalid_title_raises_error(self):
        with pytest.raises(InvalidExpenseError):
            Expense(expense_id=1, title="", amount=10.0, category="Food & Dining")

        with pytest.raises(InvalidExpenseError):
            Expense(expense_id=1, title="   ", amount=10.0, category="Food & Dining")

    def test_invalid_date_raises_error(self):
        with pytest.raises(InvalidExpenseError):
            Expense(expense_id=1, title="Coffee", amount=5.0, category="Food & Dining", date="15-03-2026")

        with pytest.raises(InvalidExpenseError):
            Expense(expense_id=1, title="Coffee", amount=5.0, category="Food & Dining", date="2026-13-40")

    def test_to_dict_and_from_dict(self):
        exp = Expense(
            expense_id=42,
            title="Internet Subscription",
            amount=60.0,
            category="Housing & Utilities",
            date="2026-01-10",
            payment_method="UPI / Online",
            notes="Fiber optic"
        )
        d = exp.to_dict()
        assert d["id"] == 42
        assert d["title"] == "Internet Subscription"
        assert d["amount"] == 60.0
        assert d["category"] == "Housing & Utilities"

        restored = Expense.from_dict(d)
        assert restored.id == exp.id
        assert restored.title == exp.title
        assert restored.amount == exp.amount
        assert restored.category == exp.category
        assert restored.date == exp.date
        assert restored.notes == exp.notes

    def test_csv_serialization(self):
        exp = Expense(
            expense_id=10,
            title="Book Purchase",
            amount=29.99,
            category="Education",
            date="2026-02-20",
            payment_method="Debit Card"
        )
        csv_row = exp.to_csv_row()
        assert csv_row["ID"] == 10
        assert csv_row["Amount"] == "29.99"
        assert csv_row["Category"] == "Education"

        restored = Expense.from_csv_row(csv_row)
        assert restored.id == 10
        assert restored.amount == 29.99
        assert restored.title == "Book Purchase"

    def test_magic_methods(self):
        exp1 = Expense(expense_id=1, title="A", amount=10.0, category="Food & Dining", date="2026-01-01")
        exp2 = Expense(expense_id=1, title="B", amount=20.0, category="Shopping", date="2026-01-02")
        exp3 = Expense(expense_id=2, title="C", amount=30.0, category="Shopping", date="2026-01-03")

        # __eq__ based on ID
        assert exp1 == exp2
        assert exp1 != exp3

        # __str__ and __repr__
        assert "🍔" in str(exp1)
        assert "Expense(id=1" in repr(exp1)

        # __lt__ sorting by date
        assert exp1 < exp3


class TestBudgetModel:
    """Test suite for Budget calculations."""

    def test_category_budget_status(self):
        cb = CategoryBudget("Food & Dining", 500.0)

        # Normal spending
        status_normal = cb.calculate_status(250.0)
        assert status_normal["status"] == "ON TRACK"
        assert status_normal["percent_used"] == 50.0
        assert status_normal["remaining"] == 250.0

        # Warning threshold (85%+)
        status_warning = cb.calculate_status(450.0)
        assert "WARNING" in status_warning["status"]
        assert status_warning["percent_used"] == 90.0

        # Exceeded threshold (> 100%)
        status_exceeded = cb.calculate_status(550.0)
        assert status_exceeded["status"] == "EXCEEDED"
        assert status_exceeded["percent_used"] == 110.0
        assert status_exceeded["remaining"] == -50.0
