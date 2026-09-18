"""
Expense Entity Model.
Demonstrates: OOP, Encapsulation, Properties, Data Validation, Magic Methods (__str__, __repr__, __eq__, __lt__), Serialization.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from ..utils.validators import (
    validate_date,
    validate_amount,
    validate_category,
    validate_payment_method,
    validate_id,
    ValidationError,
    InvalidExpenseError
)
from .category import get_category_icon


class Expense:
    """
    Represents an individual financial expense transaction.
    Encapsulates transaction ID, title, amount, category, date, payment method, and optional notes.
    """

    def __init__(
        self,
        expense_id: int,
        title: str,
        amount: float,
        category: str,
        date: Optional[str] = None,
        payment_method: str = "UPI / Online",
        notes: str = ""
    ):
        """
        Initializes an Expense object with validated data.

        :param expense_id: Positive integer unique identifier
        :param title: Name / description of the expense
        :param amount: Numeric monetary value (> 0)
        :param category: Expense category
        :param date: ISO Date string (YYYY-MM-DD), defaults to today
        :param payment_method: Payment mode (Cash, Credit Card, UPI, etc.)
        :param notes: Optional supplementary remarks
        """
        self._id = validate_id(expense_id)
        self.title = title
        self.amount = amount
        self.category = category
        self.date = date if date else datetime.now().strftime("%Y-%m-%d")
        self.payment_method = payment_method
        self.notes = notes

    # --- Property Getters & Setters (Encapsulation) ---

    @property
    def id(self) -> int:
        """Unique expense identifier (read-only after creation)."""
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise InvalidExpenseError("Expense title cannot be empty.")
        self._title = value.strip()

    @property
    def amount(self) -> float:
        return self._amount

    @amount.setter
    def amount(self, value: float | int | str):
        try:
            self._amount = validate_amount(value)
        except ValidationError as err:
            raise InvalidExpenseError(str(err)) from err

    @property
    def category(self) -> str:
        return self._category

    @category.setter
    def category(self, value: str):
        try:
            self._category = validate_category(value)
        except ValidationError as err:
            raise InvalidExpenseError(str(err)) from err

    @property
    def date(self) -> str:
        return self._date

    @date.setter
    def date(self, value: str):
        try:
            self._date = validate_date(value)
        except ValidationError as err:
            raise InvalidExpenseError(str(err)) from err

    @property
    def payment_method(self) -> str:
        return self._payment_method

    @payment_method.setter
    def payment_method(self, value: str):
        try:
            self._payment_method = validate_payment_method(value)
        except ValidationError as err:
            raise InvalidExpenseError(str(err)) from err

    @property
    def notes(self) -> str:
        return self._notes

    @notes.setter
    def notes(self, value: Optional[str]):
        self._notes = str(value).strip() if value is not None else ""

    # --- Helper Properties ---

    @property
    def year(self) -> int:
        return int(self.date.split("-")[0])

    @property
    def month(self) -> int:
        return int(self.date.split("-")[1])

    @property
    def year_month(self) -> str:
        """Returns 'YYYY-MM' for grouping."""
        return self.date[:7]

    @property
    def icon(self) -> str:
        return get_category_icon(self.category)

    # --- Serialization & Deserialization ---

    def to_dict(self) -> Dict[str, Any]:
        """Serializes expense object into a clean dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "amount": self.amount,
            "category": self.category,
            "date": self.date,
            "payment_method": self.payment_method,
            "notes": self.notes
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Expense":
        """Constructs an Expense instance from a dictionary."""
        return cls(
            expense_id=data.get("id"),
            title=data.get("title", ""),
            amount=data.get("amount", 0.0),
            category=data.get("category", "Miscellaneous"),
            date=data.get("date"),
            payment_method=data.get("payment_method", "UPI / Online"),
            notes=data.get("notes", "")
        )

    def to_csv_row(self) -> Dict[str, Any]:
        """Converts expense to flat CSV column dictionary."""
        return {
            "ID": self.id,
            "Date": self.date,
            "Title": self.title,
            "Category": self.category,
            "Amount": f"{self.amount:.2f}",
            "Payment Method": self.payment_method,
            "Notes": self.notes
        }

    @classmethod
    def from_csv_row(cls, row: Dict[str, Any]) -> "Expense":
        """Creates an Expense instance from a CSV dictionary row."""
        return cls(
            expense_id=int(row.get("ID", 1)),
            title=str(row.get("Title", "")),
            amount=float(row.get("Amount", 0.0)),
            category=str(row.get("Category", "Miscellaneous")),
            date=str(row.get("Date", "")),
            payment_method=str(row.get("Payment Method", "UPI / Online")),
            notes=str(row.get("Notes", ""))
        )

    # --- Python Magic Methods ---

    def __str__(self) -> str:
        return f"[{self.date}] #{self.id:03d} | {self.icon} {self.category:<18} | {self.title:<24} | ${self.amount:>8.2f} ({self.payment_method})"

    def __repr__(self) -> str:
        return (
            f"Expense(id={self.id}, title='{self.title}', amount={self.amount}, "
            f"category='{self.category}', date='{self.date}', payment_method='{self.payment_method}')"
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Expense):
            return False
        return self.id == other.id

    def __lt__(self, other: "Expense") -> bool:
        """Enables natural sorting by date, then by amount."""
        if not isinstance(other, Expense):
            return NotImplemented
        if self.date == other.date:
            return self.amount > other.amount  # Higher amount first on same day
        return self.date < other.date
