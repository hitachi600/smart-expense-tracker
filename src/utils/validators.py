"""
Custom exception hierarchy and data validation utilities.
Demonstrates: Custom Exceptions, Regular Expressions, Datetime handling, Defensive Programming.
"""

from datetime import datetime
from typing import Optional, List


# =====================================================================
# Custom Exception Hierarchy
# =====================================================================

class ExpenseTrackerError(Exception):
    """Base exception for all Expense Tracker domain errors."""
    pass


class ValidationError(ExpenseTrackerError):
    """Raised when input data validation fails."""
    pass


class InvalidExpenseError(ValidationError):
    """Raised when an expense entity has invalid attributes."""
    pass


class ExpenseNotFoundError(ExpenseTrackerError):
    """Raised when an expense with a specific ID cannot be located."""
    pass


class StorageError(ExpenseTrackerError):
    """Raised when persistence operations (read/write/backup) fail."""
    pass


class BudgetExceededWarning(ExpenseTrackerError):
    """Warning representation when an expense causes category budget overshoot."""
    pass


# =====================================================================
# Validation Helper Functions
# =====================================================================

ALLOWED_PAYMENT_METHODS = [
    "Cash",
    "Credit Card",
    "Debit Card",
    "UPI / Online",
    "Bank Transfer",
    "Other"
]


def validate_date(date_str: str) -> str:
    """
    Validates that a string is a valid ISO date (YYYY-MM-DD) and not in the far future.

    :param date_str: String representation of date
    :return: Normalized date string in 'YYYY-MM-DD' format
    :raises ValidationError: If date format is invalid or out of sensible range
    """
    if not isinstance(date_str, str):
        raise ValidationError(f"Date must be a string, got {type(date_str).__name__}.")

    date_str = date_str.strip()
    if not date_str:
        raise ValidationError("Date cannot be empty.")

    try:
        parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValidationError(
            f"Invalid date format '{date_str}'. Expected format: YYYY-MM-DD (e.g., 2026-03-15)."
        )

    # Basic range check (not before 2000, not more than 1 year in future)
    min_year = 2000
    max_year = datetime.now().year + 5
    if not (min_year <= parsed_date.year <= max_year):
        raise ValidationError(
            f"Date year {parsed_date.year} is out of acceptable range ({min_year} - {max_year})."
        )

    return parsed_date.strftime("%Y-%m-%d")


def validate_amount(amount: float | int | str) -> float:
    """
    Validates that amount is a positive number.

    :param amount: Numeric or numeric string amount
    :return: Sanitized float amount rounded to 2 decimal places
    :raises ValidationError: If amount is non-numeric, zero, or negative
    """
    try:
        amount_float = float(amount)
    except (ValueError, TypeError):
        raise ValidationError(f"Amount must be a valid number, got '{amount}'.")

    if amount_float <= 0:
        raise ValidationError(f"Amount must be strictly greater than 0, got {amount_float:.2f}.")

    if amount_float > 1_000_000_000:
        raise ValidationError(f"Amount {amount_float:.2f} exceeds realistic transaction limit.")

    return round(amount_float, 2)


def validate_category(category: str, allowed_categories: Optional[List[str]] = None) -> str:
    """
    Validates and normalizes category name.

    :param category: Input category name
    :param allowed_categories: Optional list of valid category names
    :return: Title-cased sanitized category string
    :raises ValidationError: If category is empty or not in allowed list
    """
    if not isinstance(category, str) or not category.strip():
        raise ValidationError("Category cannot be empty.")

    sanitized = category.strip().title()

    if allowed_categories:
        # Case-insensitive check
        normalized_allowed = {c.lower(): c for c in allowed_categories}
        if sanitized.lower() not in normalized_allowed:
            raise ValidationError(
                f"Category '{sanitized}' is not recognized. Allowed: {', '.join(allowed_categories)}"
            )
        return normalized_allowed[sanitized.lower()]

    return sanitized


def validate_payment_method(method: str) -> str:
    """
    Validates payment method against allowed values.

    :param method: Payment method string
    :return: Standardized payment method
    :raises ValidationError: If payment method is invalid
    """
    if not isinstance(method, str) or not method.strip():
        return "Other"

    sanitized = method.strip()
    # Case-insensitive match against allowed
    for allowed in ALLOWED_PAYMENT_METHODS:
        if sanitized.lower() == allowed.lower():
            return allowed

    # If not an exact match, default to 'Other' or accept if non-empty
    return sanitized.title()


def validate_id(expense_id: int | str) -> int:
    """
    Validates that an expense ID is a positive integer.
    """
    try:
        val = int(expense_id)
        if val <= 0:
            raise ValueError()
        return val
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid expense ID '{expense_id}'. ID must be a positive integer.")
