"""
ExpenseManager Service.
Demonstrates: CRUD logic, High-level business operations, Filtering, Searching, Dependency Injection.
"""

from typing import List, Dict, Any, Optional
from ..models.expense import Expense
from ..models.budget import Budget
from ..storage.storage_interface import StorageInterface
from ..storage.json_storage import JSONStorage
from ..storage.csv_storage import CSVStorage
from ..utils.validators import (
    ExpenseNotFoundError,
    ValidationError,
    InvalidExpenseError
)
from ..utils.sample_data import generate_sample_expenses


class ExpenseManager:
    """
    Core business service managing the collection of expenses, CRUD operations,
    search/filter queries, budget checks, and persistence synchronization.
    """

    def __init__(self, storage: Optional[StorageInterface] = None):
        """
        Initializes ExpenseManager with a pluggable storage engine (Dependency Injection).
        """
        self.storage: StorageInterface = storage or JSONStorage()
        self._expenses: List[Expense] = []
        self._next_id: int = 1
        self.budget: Budget = Budget()
        self.load_data()

    # --- Persistence Operations ---

    def load_data(self) -> None:
        """Loads data from storage backend into memory."""
        raw_data = self.storage.load()
        self._expenses = []
        max_id = 0
        for item in raw_data:
            try:
                expense = Expense.from_dict(item)
                self._expenses.append(expense)
                if expense.id > max_id:
                    max_id = expense.id
            except (ValidationError, InvalidExpenseError) as err:
                print(f"Warning: Skipping corrupted record: {err}")
        self._next_id = max_id + 1

    def save_data(self) -> bool:
        """Saves current memory records to storage backend."""
        data = [exp.to_dict() for exp in self._expenses]
        return self.storage.save(data)

    def create_backup(self) -> str:
        """Creates a timestamped backup of stored expenses."""
        self.save_data()
        return self.storage.create_backup()

    def export_to_csv(self, file_path: str = "data/expenses.csv") -> str:
        """Exports all current expenses to a CSV file."""
        csv_store = CSVStorage(file_path)
        data = [exp.to_dict() for exp in self._expenses]
        csv_store.save(data)
        return file_path

    def import_from_csv(self, file_path: str = "data/expenses.csv", merge: bool = False) -> int:
        """
        Imports expenses from a CSV file.
        :param file_path: Path to the CSV file
        :param merge: If True, appends to existing records; if False, replaces existing records
        :return: Count of imported records
        """
        csv_store = CSVStorage(file_path)
        imported_data = csv_store.load()
        if not merge:
            self._expenses.clear()
            self._next_id = 1

        count = 0
        for item in imported_data:
            item["id"] = self._next_id
            expense = Expense.from_dict(item)
            self._expenses.append(expense)
            self._next_id += 1
            count += 1

        self.save_data()
        return count

    def populate_sample_data(self, count: int = 40, days_back: int = 90) -> int:
        """
        Generates and loads realistic sample data for instant demonstration.
        """
        sample_records = generate_sample_expenses(count=count, days_back=days_back)
        self._expenses = [Expense.from_dict(rec) for rec in sample_records]
        self._next_id = len(self._expenses) + 1
        self.save_data()
        return len(self._expenses)

    def clear_all(self) -> None:
        """Wipes all expenses from memory and storage."""
        self._expenses.clear()
        self._next_id = 1
        self.save_data()

    # --- CRUD Operations ---

    def add_expense(
        self,
        title: str,
        amount: float,
        category: str,
        date: Optional[str] = None,
        payment_method: str = "UPI / Online",
        notes: str = ""
    ) -> Expense:
        """
        Creates, validates, and stores a new Expense transaction.
        """
        expense = Expense(
            expense_id=self._next_id,
            title=title,
            amount=amount,
            category=category,
            date=date,
            payment_method=payment_method,
            notes=notes
        )
        self._expenses.append(expense)
        self._next_id += 1
        self.save_data()
        return expense

    def get_expense(self, expense_id: int) -> Expense:
        """
        Retrieves a single expense by ID.
        :raises ExpenseNotFoundError: If ID is not found
        """
        for exp in self._expenses:
            if exp.id == expense_id:
                return exp
        raise ExpenseNotFoundError(f"Expense with ID #{expense_id} was not found.")

    def get_all_expenses(self) -> List[Expense]:
        """Returns a shallow copy of all expenses."""
        return list(self._expenses)

    def update_expense(self, expense_id: int, **kwargs) -> Expense:
        """
        Updates fields of an existing expense.
        Supported kwargs: title, amount, category, date, payment_method, notes
        """
        expense = self.get_expense(expense_id)

        if "title" in kwargs and kwargs["title"] is not None:
            expense.title = kwargs["title"]
        if "amount" in kwargs and kwargs["amount"] is not None:
            expense.amount = kwargs["amount"]
        if "category" in kwargs and kwargs["category"] is not None:
            expense.category = kwargs["category"]
        if "date" in kwargs and kwargs["date"] is not None:
            expense.date = kwargs["date"]
        if "payment_method" in kwargs and kwargs["payment_method"] is not None:
            expense.payment_method = kwargs["payment_method"]
        if "notes" in kwargs and kwargs["notes"] is not None:
            expense.notes = kwargs["notes"]

        self.save_data()
        return expense

    def delete_expense(self, expense_id: int) -> Expense:
        """
        Deletes an expense by ID and updates storage.
        """
        expense = self.get_expense(expense_id)
        self._expenses.remove(expense)
        self.save_data()
        return expense

    # --- Search & Filter Queries ---

    def search_expenses(self, query: str) -> List[Expense]:
        """
        Performs a case-insensitive search across title, category, payment method, and notes.
        """
        if not query or not query.strip():
            return self.get_all_expenses()

        q = query.strip().lower()
        return [
            exp for exp in self._expenses
            if q in exp.title.lower()
            or q in exp.category.lower()
            or q in exp.payment_method.lower()
            or q in exp.notes.lower()
            or q == str(exp.id)
        ]

    def filter_expenses(
        self,
        category: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        payment_method: Optional[str] = None
    ) -> List[Expense]:
        """
        Filters expenses by multiple optional constraints.
        """
        results = self._expenses

        if category:
            results = [e for e in results if e.category.lower() == category.strip().lower()]

        if min_amount is not None:
            results = [e for e in results if e.amount >= min_amount]

        if max_amount is not None:
            results = [e for e in results if e.amount <= max_amount]

        if start_date:
            results = [e for e in results if e.date >= start_date]

        if end_date:
            results = [e for e in results if e.date <= end_date]

        if payment_method:
            results = [e for e in results if e.payment_method.lower() == payment_method.strip().lower()]

        return results

    def sort_expenses(self, by: str = "date", reverse: bool = False) -> List[Expense]:
        """
        Sorts expenses by field: 'date', 'amount', 'category', 'title', 'id'.
        """
        key_map = {
            "date": lambda x: (x.date, x.id),
            "amount": lambda x: x.amount,
            "category": lambda x: x.category.lower(),
            "title": lambda x: x.title.lower(),
            "id": lambda x: x.id
        }
        sort_key = key_map.get(by.lower(), key_map["date"])
        return sorted(self._expenses, key=sort_key, reverse=reverse)

    def count(self) -> int:
        """Returns total number of recorded expenses."""
        return len(self._expenses)

    def get_total_spent(self) -> float:
        """Returns sum of all expense amounts."""
        return round(sum(exp.amount for exp in self._expenses), 2)
