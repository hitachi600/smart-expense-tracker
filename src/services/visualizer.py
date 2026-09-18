"""
Visualizer Service utilizing Matplotlib for modern, publication-ready financial charts.
Demonstrates: Matplotlib Subplots, Donut Charts, Bar Charts, Line & Fill Area Charts, Custom Aesthetics, Figure Export.
"""

import os
from typing import Optional, List
import matplotlib
# Use Agg backend by default for safe headless rendering and file export
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

from .analytics_engine import AnalyticsEngine
from ..models.budget import Budget
from ..models.category import get_category_color


class Visualizer:
    """
    Renders and exports graphical financial charts from expense data.
    """

    def __init__(self, analytics: AnalyticsEngine, charts_dir: str = "charts"):
        self.analytics = analytics
        self.charts_dir = charts_dir
        self._ensure_charts_directory()
        self._setup_style()

    def _ensure_charts_directory(self) -> None:
        """Ensures output charts folder exists."""
        if not os.path.exists(self.charts_dir):
            os.makedirs(self.charts_dir, exist_ok=True)

    def _setup_style(self) -> None:
        """Configures clean, modern Matplotlib plot typography and grid aesthetics."""
        plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
        plt.rcParams["font.sans-serif"] = ["Segoe UI", "DejaVu Sans", "Arial", "Helvetica"]
        plt.rcParams["axes.edgecolor"] = "#E0E0E0"
        plt.rcParams["axes.linewidth"] = 0.8

    # =========================================================================
    # 1. Category Distribution (Donut / Pie Chart)
    # =========================================================================

    def plot_category_pie(self, filename: str = "category_pie.png", show: bool = False) -> str:
        """
        Renders a modern Donut Chart showing spending by Category.
        """
        cat_df = self.analytics.get_category_summary()
        if cat_df.empty:
            return ""

        fig, ax = plt.subplots(figsize=(8, 6), subplot_kw=dict(aspect="equal"))

        categories = cat_df["Category"].tolist()
        values = cat_df["Total Spent"].tolist()
        colors = [get_category_color(c) for c in categories]

        # Donut chart wedges
        wedges, texts, autotexts = ax.pie(
            values,
            labels=None,
            autopct="%1.1f%%",
            pctdistance=0.75,
            startangle=140,
            colors=colors,
            wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2)
        )

        for autotext in autotexts:
            autotext.set_color("#2C3E50")
            autotext.set_fontsize(10)
            autotext.set_weight("bold")

        ax.legend(
            wedges,
            [f"{cat}: ₹{val:,.2f}" for cat, val in zip(categories, values)],
            title="Categories",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1),
            frameon=True,
            facecolor="#F8F9FA",
            edgecolor="#E2E8F0"
        )

        total_spent = sum(values)
        ax.text(0, 0, f"Total\n₹{total_spent:,.2f}", ha="center", va="center", fontsize=12, fontweight="bold", color="#2C3E50")
        ax.set_title("Expense Breakdown by Category (INR)", fontsize=14, fontweight="bold", pad=20, color="#1A202C")

        plt.tight_layout()
        output_path = os.path.join(self.charts_dir, filename)
        fig.savefig(output_path, dpi=200, bbox_inches="tight")
        if show:
            plt.show()
        plt.close(fig)
        return output_path

    # =========================================================================
    # 2. Monthly Spending (Bar Chart)
    # =========================================================================

    def plot_monthly_bar(self, filename: str = "monthly_trend.png", show: bool = False) -> str:
        """
        Renders a Bar Chart for Month-over-Month total expenses.
        """
        month_df = self.analytics.get_monthly_summary()
        if month_df.empty:
            return ""

        fig, ax = plt.subplots(figsize=(9, 5.5))

        months = month_df["Month"].tolist()
        totals = month_df["Total Spent"].tolist()

        bars = ax.bar(months, totals, color="#3B82F6", width=0.55, edgecolor="#1D4ED8", linewidth=1.2, zorder=3)
        ax.grid(axis="y", linestyle="--", alpha=0.7, zorder=0)

        # Average reference line
        avg_monthly = np.mean(totals)
        ax.axhline(avg_monthly, color="#EF4444", linestyle=":", linewidth=1.8, label=f"Monthly Average (₹{avg_monthly:,.2f})", zorder=4)

        # Value labels above bars
        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f"₹{height:,.0f}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=10,
                fontweight="semibold",
                color="#1F2937"
            )

        ax.set_title("Monthly Spending Overview (INR)", fontsize=14, fontweight="bold", pad=15, color="#111827")
        ax.set_xlabel("Billing Period (Month)", fontsize=11, labelpad=10)
        ax.set_ylabel("Total Spent (₹)", fontsize=11, labelpad=10)
        ax.legend(loc="upper right", frameon=True)

        plt.tight_layout()
        output_path = os.path.join(self.charts_dir, filename)
        fig.savefig(output_path, dpi=200, bbox_inches="tight")
        if show:
            plt.show()
        plt.close(fig)
        return output_path

    # =========================================================================
    # 3. Daily Trend & Cumulative Spending (Line / Area Chart)
    # =========================================================================

    def plot_daily_trend(self, filename: str = "daily_trend.png", show: bool = False) -> str:
        """
        Renders Daily Transactions and Cumulative Spending Trend line/area chart.
        """
        daily_df = self.analytics.get_daily_trend()
        if daily_df.empty:
            return ""

        fig, ax1 = plt.subplots(figsize=(10, 5.5))

        dates = daily_df["Date"]
        daily_amt = daily_df["Daily Total"]
        cum_amt = daily_df["Cumulative Sum"]
        moving_avg = daily_df["7-Day Moving Avg"]

        # Daily bar spikes
        ax1.bar(dates, daily_amt, color="#93C5FD", alpha=0.5, label="Daily Spending (₹)", width=0.8, zorder=2)
        ax1.plot(dates, moving_avg, color="#2563EB", linewidth=2.2, label="7-Day Moving Avg", zorder=3)
        ax1.set_ylabel("Daily Expenses (₹)", color="#1E40AF", fontsize=11)
        ax1.tick_params(axis="y", labelcolor="#1E40AF")

        # Secondary axis for cumulative spending
        ax2 = ax1.twinx()
        ax2.plot(dates, cum_amt, color="#10B981", linewidth=2.5, linestyle="--", label="Cumulative Spent (₹)", zorder=4)
        ax2.fill_between(dates, cum_amt, color="#D1FAE5", alpha=0.3, zorder=1)
        ax2.set_ylabel("Cumulative Spending (₹)", color="#065F46", fontsize=11)
        ax2.tick_params(axis="y", labelcolor="#065F46")
        ax2.grid(False)

        # Date formatting
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
        plt.xticks(rotation=30)

        # Title and legends
        ax1.set_title("Daily Spending Timeline & Cumulative Trajectory (INR)", fontsize=14, fontweight="bold", pad=15)
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", frameon=True)

        plt.tight_layout()
        output_path = os.path.join(self.charts_dir, filename)
        fig.savefig(output_path, dpi=200, bbox_inches="tight")
        if show:
            plt.show()
        plt.close(fig)
        return output_path

    # =========================================================================
    # 4. Budget vs. Actual (Horizontal Comparison Bar Chart)
    # =========================================================================

    def plot_budget_vs_actual(self, budget: Budget, filename: str = "budget_vs_actual.png", show: bool = False) -> str:
        """
        Renders a comparison bar chart between allocated Budget Limits and Actual Spending per category.
        """
        spending_map = self.analytics.get_category_spending_map()
        budget_eval = budget.evaluate_spending(spending_map)

        if not budget_eval:
            return ""

        # Filter categories that have either budget or spending
        relevant = [b for b in budget_eval if b["limit"] > 0 or b["spent"] > 0]
        if not relevant:
            return ""

        categories = [r["category"] for r in relevant]
        limits = [r["limit"] for r in relevant]
        spent = [r["spent"] for r in relevant]

        y = np.arange(len(categories))
        height = 0.35

        fig, ax = plt.subplots(figsize=(10, max(5.5, len(categories) * 0.55)))

        bars_limit = ax.barh(y - height/2, limits, height, label="Budget Limit (₹)", color="#CBD5E1", edgecolor="#94A3B8")
        
        # Color spent bars by status (green for safe, red for exceeded)
        spent_colors = ["#EF4444" if s > l else "#10B981" for s, l in zip(spent, limits)]
        bars_spent = ax.barh(y + height/2, spent, height, label="Actual Spent (₹)", color=spent_colors, edgecolor="#0F172A", alpha=0.85)

        ax.set_yticks(y)
        ax.set_yticklabels(categories, fontsize=10)
        ax.invert_yaxis()  # top-down
        ax.set_xlabel("Amount (₹)", fontsize=11, labelpad=10)
        ax.set_title("Budget Allocation vs. Actual Spending (INR)", fontsize=14, fontweight="bold", pad=15)
        ax.legend(loc="lower right", frameon=True)

        plt.tight_layout()
        output_path = os.path.join(self.charts_dir, filename)
        fig.savefig(output_path, dpi=200, bbox_inches="tight")
        if show:
            plt.show()
        plt.close(fig)
        return output_path

    # =========================================================================
    # 5. Master 4-in-1 Executive Financial Dashboard
    # =========================================================================

    def plot_dashboard(self, budget: Optional[Budget] = None, filename: str = "master_dashboard.png", show: bool = False) -> str:
        """
        Creates a comprehensive 4-panel executive dashboard combining:
        1. Category Donut Chart
        2. Monthly Spending Bar Chart
        3. Payment Method Distribution
        4. Budget vs Actual Comparison
        """
        fig, axs = plt.subplots(2, 2, figsize=(16, 11))
        fig.suptitle("Smart Personal Expense & Financial Analytics Dashboard (INR)", fontsize=18, fontweight="bold", y=0.98, color="#0F172A")

        # 1. Top-Left: Category Breakdown
        cat_df = self.analytics.get_category_summary()
        if not cat_df.empty:
            ax1 = axs[0, 0]
            cats = cat_df["Category"].tolist()
            vals = cat_df["Total Spent"].tolist()
            colors = [get_category_color(c) for c in cats]
            ax1.pie(vals, labels=cats, autopct="%1.1f%%", colors=colors, startangle=140, textprops={'fontsize': 9})
            ax1.set_title("Spending by Category", fontsize=12, fontweight="bold")
        else:
            axs[0, 0].text(0.5, 0.5, "No Category Data", ha="center", va="center")

        # 2. Top-Right: Monthly Trends
        month_df = self.analytics.get_monthly_summary()
        if not month_df.empty:
            ax2 = axs[0, 1]
            months = month_df["Month"].tolist()
            totals = month_df["Total Spent"].tolist()
            ax2.bar(months, totals, color="#3B82F6", width=0.5, edgecolor="#1D4ED8")
            ax2.grid(axis="y", linestyle="--", alpha=0.7)
            ax2.set_title("Monthly Total Expenses", fontsize=12, fontweight="bold")
            ax2.set_ylabel("Spent (₹)")
            for i, val in enumerate(totals):
                ax2.text(i, val + (max(totals)*0.02), f"₹{val:,.0f}", ha="center", fontsize=9, fontweight="bold")
        else:
            axs[0, 1].text(0.5, 0.5, "No Monthly Data", ha="center", va="center")

        # 3. Bottom-Left: Payment Methods
        pay_df = self.analytics.get_payment_method_summary()
        if not pay_df.empty:
            ax3 = axs[1, 0]
            methods = pay_df["Payment Method"].tolist()
            shares = pay_df["Total Spent"].tolist()
            ax3.barh(methods, shares, color="#8B5CF6", height=0.55, edgecolor="#6D28D9")
            ax3.set_title("Spending by Payment Method", fontsize=12, fontweight="bold")
            ax3.set_xlabel("Total (₹)")
            ax3.grid(axis="x", linestyle="--", alpha=0.7)
        else:
            axs[1, 0].text(0.5, 0.5, "No Payment Method Data", ha="center", va="center")

        # 4. Bottom-Right: Budget vs Actual or Daily Trend
        b = budget or Budget()
        spending_map = self.analytics.get_category_spending_map()
        budget_eval = b.evaluate_spending(spending_map)
        relevant = [r for r in budget_eval if r["limit"] > 0 or r["spent"] > 0]

        if relevant:
            ax4 = axs[1, 1]
            cat_names = [r["category"] for r in relevant][:6]  # top 6
            lims = [r["limit"] for r in relevant][:6]
            spents = [r["spent"] for r in relevant][:6]
            x = np.arange(len(cat_names))
            width = 0.35
            ax4.bar(x - width/2, lims, width, label="Budget Limit", color="#CBD5E1")
            ax4.bar(x + width/2, spents, width, label="Actual Spent", color="#10B981")
            ax4.set_xticks(x)
            ax4.set_xticklabels(cat_names, rotation=25, ha="right", fontsize=8.5)
            ax4.set_title("Budget vs. Actual (Key Categories)", fontsize=12, fontweight="bold")
            ax4.legend(loc="upper right", fontsize=8.5)
            ax4.grid(axis="y", linestyle="--", alpha=0.7)
        else:
            axs[1, 1].text(0.5, 0.5, "No Budget Data", ha="center", va="center")

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        output_path = os.path.join(self.charts_dir, filename)
        fig.savefig(output_path, dpi=220, bbox_inches="tight")
        if show:
            plt.show()
        plt.close(fig)
        return output_path
