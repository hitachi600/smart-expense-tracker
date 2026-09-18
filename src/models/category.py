"""
Category management model.
Demonstrates: OOP, Data structures, Dataclasses, Class methods, String representation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Category:
    """
    Represents an expense category with visual icons, color identifiers, and optional default monthly budget.
    """
    name: str
    icon: str = "📁"
    color: str = "#4A90E2"
    description: str = ""
    default_monthly_budget: float = 0.0

    def __post_init__(self):
        self.name = self.name.strip().title()

    def __str__(self) -> str:
        return f"{self.icon} {self.name}"

    def to_dict(self) -> Dict[str, any]:
        return {
            "name": self.name,
            "icon": self.icon,
            "color": self.color,
            "description": self.description,
            "default_monthly_budget": self.default_monthly_budget
        }

    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> "Category":
        return cls(
            name=data.get("name", "Miscellaneous"),
            icon=data.get("icon", "📁"),
            color=data.get("color", "#7F8C8D"),
            description=data.get("description", ""),
            default_monthly_budget=float(data.get("default_monthly_budget", 0.0))
        )


# Default built-in categories with pleasant pastel/vibrant chart colors and icons
DEFAULT_CATEGORIES: Dict[str, Category] = {
    "Food & Dining": Category(
        name="Food & Dining",
        icon="🍔",
        color="#FF6B6B",
        description="Groceries, restaurants, snacks, drinks, food delivery",
        default_monthly_budget=600.0
    ),
    "Transportation": Category(
        name="Transportation",
        icon="🚗",
        color="#4D96FF",
        description="Fuel, public transit, rideshare, parking, maintenance",
        default_monthly_budget=300.0
    ),
    "Housing & Utilities": Category(
        name="Housing & Utilities",
        icon="🏠",
        color="#6BCB77",
        description="Rent/mortgage, power, water, gas, home internet",
        default_monthly_budget=1400.0
    ),
    "Entertainment": Category(
        name="Entertainment",
        icon="🎬",
        color="#FFD93D",
        description="Streaming, movies, concerts, games, events",
        default_monthly_budget=150.0
    ),
    "Shopping": Category(
        name="Shopping",
        icon="🛍️",
        color="#9B59B6",
        description="Clothing, gadgets, electronics, home items",
        default_monthly_budget=250.0
    ),
    "Healthcare": Category(
        name="Healthcare",
        icon="💊",
        color="#1ABC9C",
        description="Medicine, doctor visits, dental, gym, health insurance",
        default_monthly_budget=200.0
    ),
    "Education": Category(
        name="Education",
        icon="📚",
        color="#E67E22",
        description="Tuition, courses, books, learning supplies",
        default_monthly_budget=100.0
    ),
    "Investments": Category(
        name="Investments",
        icon="📈",
        color="#2ECC71",
        description="Stocks, index funds, savings, retirement deposits",
        default_monthly_budget=500.0
    ),
    "Personal Care": Category(
        name="Personal Care",
        icon="💈",
        color="#E84393",
        description="Salons, barbers, cosmetics, spa, personal hygiene",
        default_monthly_budget=100.0
    ),
    "Miscellaneous": Category(
        name="Miscellaneous",
        icon="📦",
        color="#95A5A6",
        description="Uncategorized or one-off miscellaneous expenses",
        default_monthly_budget=150.0
    )
}


def get_category_names() -> List[str]:
    """Returns a list of all standard category names."""
    return list(DEFAULT_CATEGORIES.keys())


def get_category_icon(category_name: str) -> str:
    """Returns emoji icon for a category name, or default folder emoji."""
    cat = DEFAULT_CATEGORIES.get(category_name.strip().title())
    return cat.icon if cat else "📁"


def get_category_color(category_name: str) -> str:
    """Returns hex color code for a category."""
    cat = DEFAULT_CATEGORIES.get(category_name.strip().title())
    return cat.color if cat else "#7F8C8D"
