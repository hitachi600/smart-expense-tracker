"""
Budget and Financial Target Models.
Demonstrates: OOP, Dataclasses, Financial Threshold Calculations, Aggregations.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..utils.formatters import format_currency


@dataclass
class CategoryBudget:
    """Represents a budget limit for a specific category."""
    category_name: str
    monthly_limit: float

    def calculate_status(self, actual_spent: float) -> Dict[str, Any]:
        """
        Calculates spending metrics against budget limit.
        """
        spent = round(float(actual_spent), 2)
        limit = round(float(self.monthly_limit), 2)
        remaining = round(limit - spent, 2)
        percent_used = round((spent / limit * 100), 1) if limit > 0 else 0.0

        if limit == 0:
            status = "No Limit"
            severity = "normal"
        elif spent > limit:
            status = "EXCEEDED"
            severity = "danger"
        elif percent_used >= 85.0:
            status = "WARNING (85%+)"
            severity = "warning"
        else:
            status = "ON TRACK"
            severity = "success"

        return {
            "category": self.category_name,
            "limit": limit,
            "spent": spent,
            "remaining": remaining,
            "percent_used": percent_used,
            "status": status,
            "severity": severity
        }


class Budget:
    """
    Manages budget plans, category allocations, and alerts.
    """

    def __init__(self, overall_monthly_limit: float = 3000.0, category_limits: Optional[Dict[str, float]] = None):
        self.overall_monthly_limit = float(overall_monthly_limit)
        self.category_limits: Dict[str, float] = category_limits or {
            "Food & Dining": 600.0,
            "Transportation": 300.0,
            "Housing & Utilities": 1400.0,
            "Entertainment": 150.0,
            "Shopping": 250.0,
            "Healthcare": 200.0,
            "Education": 100.0,
            "Investments": 500.0,
            "Personal Care": 100.0,
            "Miscellaneous": 150.0
        }

    def set_category_limit(self, category: str, limit: float) -> None:
        """Sets or updates a monthly limit for a specific category."""
        if limit < 0:
            raise ValueError("Budget limit cannot be negative.")
        self.category_limits[category.strip().title()] = round(float(limit), 2)

    def get_category_limit(self, category: str) -> float:
        """Retrieves limit for category, returns 0.0 if not set."""
        return self.category_limits.get(category.strip().title(), 0.0)

    def evaluate_spending(self, category_spending_map: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Evaluates a dict of {CategoryName: ActualSpent} against budget limits.
        """
        results = []
        for cat_name, limit in self.category_limits.items():
            actual = category_spending_map.get(cat_name, 0.0)
            cb = CategoryBudget(cat_name, limit)
            results.append(cb.calculate_status(actual))
        return results

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_monthly_limit": self.overall_monthly_limit,
            "category_limits": self.category_limits
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Budget":
        return cls(
            overall_monthly_limit=float(data.get("overall_monthly_limit", 3000.0)),
            category_limits=data.get("category_limits", {})
        )
