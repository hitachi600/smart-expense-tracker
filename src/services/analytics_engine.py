"""
Analytics Engine utilizing NumPy and Pandas for deep financial computation.
Demonstrates: NumPy array math, Pandas DataFrames, GroupBy, Aggregations, Rolling Windows, Outlier Detection.
"""

from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from ..models.expense import Expense


class AnalyticsEngine:
    """
    Computes statistical summaries, aggregations, trends, and breakdowns
    from expense records using NumPy and Pandas.
    """

    def __init__(self, expenses: Optional[List[Expense]] = None):
        self.expenses: List[Expense] = expenses or []

    def set_expenses(self, expenses: List[Expense]) -> None:
        """Updates internal expense list for analysis."""
        self.expenses = expenses

    def to_dataframe(self) -> pd.DataFrame:
        """
        Converts the list of Expense objects into a Pandas DataFrame with typed columns.
        """
        if not self.expenses:
            return pd.DataFrame(columns=["id", "date", "title", "category", "amount", "payment_method", "notes", "year_month"])

        data = [exp.to_dict() for exp in self.expenses]
        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"])
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
        df["year_month"] = df["date"].dt.strftime("%Y-%m")
        df["day_of_week"] = df["date"].dt.day_name()
        return df

    # =========================================================================
    # 1. NumPy Statistical Computations
    # =========================================================================

    def compute_numpy_statistics(self) -> Dict[str, Any]:
        """
        Uses NumPy array operations to calculate core descriptive statistics.
        """
        if not self.expenses:
            return {
                "count": 0,
                "total": 0.0,
                "mean": 0.0,
                "median": 0.0,
                "min": 0.0,
                "max": 0.0,
                "std_dev": 0.0,
                "variance": 0.0,
                "p25": 0.0,
                "p75": 0.0,
                "p90": 0.0,
                "iqr": 0.0
            }

        amounts = np.array([exp.amount for exp in self.expenses], dtype=np.float64)

        total = float(np.sum(amounts))
        mean = float(np.mean(amounts))
        median = float(np.median(amounts))
        min_val = float(np.min(amounts))
        max_val = float(np.max(amounts))
        std_dev = float(np.std(amounts))
        variance = float(np.var(amounts))
        p25 = float(np.percentile(amounts, 25))
        p75 = float(np.percentile(amounts, 75))
        p90 = float(np.percentile(amounts, 90))
        iqr = float(p75 - p25)

        return {
            "count": len(amounts),
            "total": round(total, 2),
            "mean": round(mean, 2),
            "median": round(median, 2),
            "min": round(min_val, 2),
            "max": round(max_val, 2),
            "std_dev": round(std_dev, 2),
            "variance": round(variance, 2),
            "p25": round(p25, 2),
            "p75": round(p75, 2),
            "p90": round(p90, 2),
            "iqr": round(iqr, 2)
        }

    # =========================================================================
    # 2. Pandas Aggregations & Groupings
    # =========================================================================

    def get_category_summary(self) -> pd.DataFrame:
        """
        Computes category-level aggregation: Total Spent, Count, Mean, Percentage of Total.
        """
        df = self.to_dataframe()
        if df.empty:
            return pd.DataFrame(columns=["Category", "Total Spent", "Count", "Average", "% of Total"])

        total_spending = df["amount"].sum()
        grouped = df.groupby("category")["amount"].agg(
            Total_Spent="sum",
            Count="count",
            Average="mean"
        ).reset_index()

        grouped["Percentage"] = (grouped["Total_Spent"] / total_spending * 100).round(1) if total_spending > 0 else 0.0
        grouped["Total_Spent"] = grouped["Total_Spent"].round(2)
        grouped["Average"] = grouped["Average"].round(2)

        grouped = grouped.sort_values(by="Total_Spent", ascending=False).reset_index(drop=True)
        grouped.columns = ["Category", "Total Spent", "Count", "Average", "% of Total"]
        return grouped

    def get_monthly_summary(self) -> pd.DataFrame:
        """
        Computes monthly aggregation: Month (YYYY-MM), Total Spent, Count, Daily Average, Top Category.
        """
        df = self.to_dataframe()
        if df.empty:
            return pd.DataFrame(columns=["Month", "Total Spent", "Transactions", "Avg per Txn", "Top Category"])

        # Group by Month
        monthly = df.groupby("year_month")["amount"].agg(
            Total_Spent="sum",
            Transactions="count",
            Avg_Txn="mean"
        ).reset_index()

        # Find top category for each month
        top_cats = {}
        for ym, group in df.groupby("year_month"):
            top_cat = group.groupby("category")["amount"].sum().idxmax()
            top_cats[ym] = top_cat

        monthly["Top Category"] = monthly["year_month"].map(top_cats)
        monthly["Total_Spent"] = monthly["Total_Spent"].round(2)
        monthly["Avg_Txn"] = monthly["Avg_Txn"].round(2)
        monthly = monthly.sort_values(by="year_month", ascending=True).reset_index(drop=True)
        monthly.columns = ["Month", "Total Spent", "Transactions", "Avg per Txn", "Top Category"]
        return monthly

    def get_payment_method_summary(self) -> pd.DataFrame:
        """
        Computes spending breakdown across payment methods.
        """
        df = self.to_dataframe()
        if df.empty:
            return pd.DataFrame(columns=["Payment Method", "Total Spent", "Count", "% Share"])

        total = df["amount"].sum()
        grouped = df.groupby("payment_method")["amount"].agg(
            Total_Spent="sum",
            Count="count"
        ).reset_index()

        grouped["Share"] = (grouped["Total_Spent"] / total * 100).round(1) if total > 0 else 0.0
        grouped["Total_Spent"] = grouped["Total_Spent"].round(2)
        grouped = grouped.sort_values(by="Total_Spent", ascending=False).reset_index(drop=True)
        grouped.columns = ["Payment Method", "Total Spent", "Count", "% Share"]
        return grouped

    def get_daily_trend(self) -> pd.DataFrame:
        """
        Computes daily spending totals with cumulative sum and 7-day rolling average.
        """
        df = self.to_dataframe()
        if df.empty:
            return pd.DataFrame(columns=["Date", "Daily Total", "Cumulative Sum", "7-Day Moving Avg"])

        daily = df.groupby(df["date"].dt.date)["amount"].sum().reset_index()
        daily.columns = ["Date", "Daily Total"]
        daily["Date"] = pd.to_datetime(daily["Date"])
        daily = daily.sort_values("Date").reset_index(drop=True)

        daily["Cumulative Sum"] = daily["Daily Total"].cumsum().round(2)
        daily["7-Day Moving Avg"] = daily["Daily Total"].rolling(window=7, min_periods=1).mean().round(2)
        return daily

    def get_top_expenses(self, n: int = 5) -> List[Expense]:
        """Returns the top N highest value expenses."""
        sorted_exp = sorted(self.expenses, key=lambda x: x.amount, reverse=True)
        return sorted_exp[:n]

    def get_outliers(self, factor: float = 1.5) -> List[Expense]:
        """
        Detects statistical spending outliers using the Interquartile Range (IQR) method.
        """
        if len(self.expenses) < 4:
            return []

        amounts = np.array([e.amount for e in self.expenses])
        q25 = np.percentile(amounts, 25)
        q75 = np.percentile(amounts, 75)
        iqr = q75 - q25
        upper_bound = q75 + (factor * iqr)

        return [e for e in self.expenses if e.amount > upper_bound]

    def get_category_spending_map(self) -> Dict[str, float]:
        """Returns a simple dictionary mapping each Category name to total spent."""
        df = self.to_dataframe()
        if df.empty:
            return {}
        cat_sums = df.groupby("category")["amount"].sum().to_dict()
        return {k: round(float(v), 2) for k, v in cat_sums.items()}
