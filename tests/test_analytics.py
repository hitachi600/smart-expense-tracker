"""
Unit tests for NumPy and Pandas computations in AnalyticsEngine.
"""

import pytest
import numpy as np
import pandas as pd
from src.models.expense import Expense
from src.services.analytics_engine import AnalyticsEngine


@pytest.fixture
def sample_expenses():
    return [
        Expense(1, "Groceries", 100.0, "Food & Dining", "2026-01-10"),
        Expense(2, "Dinner", 50.0, "Food & Dining", "2026-01-15"),
        Expense(3, "Subway", 20.0, "Transportation", "2026-01-20"),
        Expense(4, "Rent", 1000.0, "Housing & Utilities", "2026-02-01"),
        Expense(5, "Groceries 2", 80.0, "Food & Dining", "2026-02-10"),
        Expense(6, "Movie", 30.0, "Entertainment", "2026-02-15")
    ]


class TestAnalyticsEngine:
    def test_numpy_statistics_calculation(self, sample_expenses):
        engine = AnalyticsEngine(sample_expenses)
        stats = engine.compute_numpy_statistics()

        amounts = [100.0, 50.0, 20.0, 1000.0, 80.0, 30.0]

        assert stats["count"] == 6
        assert stats["total"] == pytest.approx(sum(amounts))
        assert stats["mean"] == pytest.approx(np.mean(amounts), 0.01)
        assert stats["median"] == pytest.approx(np.median(amounts), 0.01)
        assert stats["min"] == 20.0
        assert stats["max"] == 1000.0
        assert stats["std_dev"] == pytest.approx(np.std(amounts), 0.01)

    def test_empty_analytics(self):
        engine = AnalyticsEngine([])
        stats = engine.compute_numpy_statistics()
        assert stats["count"] == 0
        assert stats["total"] == 0.0
        assert stats["mean"] == 0.0

        cat_df = engine.get_category_summary()
        assert cat_df.empty

        month_df = engine.get_monthly_summary()
        assert month_df.empty

    def test_pandas_category_aggregation(self, sample_expenses):
        engine = AnalyticsEngine(sample_expenses)
        cat_df = engine.get_category_summary()

        assert not cat_df.empty
        assert "Category" in cat_df.columns
        assert "Total Spent" in cat_df.columns
        assert "Count" in cat_df.columns

        # Food & Dining total should be 100 + 50 + 80 = 230
        food_row = cat_df[cat_df["Category"] == "Food & Dining"].iloc[0]
        assert food_row["Total Spent"] == 230.0
        assert food_row["Count"] == 3

    def test_pandas_monthly_aggregation(self, sample_expenses):
        engine = AnalyticsEngine(sample_expenses)
        month_df = engine.get_monthly_summary()

        assert not month_df.empty
        assert "Month" in month_df.columns
        assert "Total Spent" in month_df.columns

        # 2026-01 total: 100 + 50 + 20 = 170
        jan_row = month_df[month_df["Month"] == "2026-01"].iloc[0]
        assert jan_row["Total Spent"] == 170.0
        assert jan_row["Transactions"] == 3

    def test_outlier_detection(self, sample_expenses):
        engine = AnalyticsEngine(sample_expenses)
        outliers = engine.get_outliers()

        # Rent ($1000) is a clear outlier relative to 20, 30, 50, 80, 100
        assert len(outliers) >= 1
        assert any(o.title == "Rent" for o in outliers)
