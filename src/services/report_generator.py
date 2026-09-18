"""
Financial Report Generator Service.
Demonstrates: Text formatting, File exports (.txt, .md, .csv), Financial Health Scoring, Automated Insights.
"""

import os
from datetime import datetime
from typing import List, Optional
from .analytics_engine import AnalyticsEngine
from ..models.budget import Budget
from ..utils.formatters import format_currency, format_table


class ReportGenerator:
    """
    Generates structured textual, markdown, and tabular reports for financial tracking.
    """

    def __init__(self, analytics: AnalyticsEngine, reports_dir: str = "reports"):
        self.analytics = analytics
        self.reports_dir = reports_dir
        self._ensure_reports_directory()

    def _ensure_reports_directory(self) -> None:
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir, exist_ok=True)

    # =========================================================================
    # 1. Executive Summary Report (Text / Markdown)
    # =========================================================================

    def generate_executive_report(self, budget: Optional[Budget] = None) -> str:
        """
        Generates a comprehensive executive financial report summarizing all metrics,
        NumPy statistics, category rankings, and budget health.
        """
        stats = self.analytics.compute_numpy_statistics()
        cat_df = self.analytics.get_category_summary()
        month_df = self.analytics.get_monthly_summary()
        pay_df = self.analytics.get_payment_method_summary()
        top_exp = self.analytics.get_top_expenses(5)
        outliers = self.analytics.get_outliers()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lines = [
            "=" * 70,
            "         SMART PERSONAL EXPENSE & FINANCIAL ANALYZER REPORT",
            "=" * 70,
            f"Generated on: {timestamp}",
            f"Total Transactions Logged: {stats['count']}",
            "",
            "-" * 70,
            "1. DESCRIPTIVE STATISTICAL SUMMARY (NumPy Engine)",
            "-" * 70,
            f"• Total Expenditure:        {format_currency(stats['total'])}",
            f"• Mean (Average) Expense:   {format_currency(stats['mean'])}",
            f"• Median Expense:           {format_currency(stats['median'])}",
            f"• Minimum Transaction:      {format_currency(stats['min'])}",
            f"• Maximum Transaction:      {format_currency(stats['max'])}",
            f"• Standard Deviation:       {format_currency(stats['std_dev'])}",
            f"• 25th Percentile (Q1):     {format_currency(stats['p25'])}",
            f"• 75th Percentile (Q3):     {format_currency(stats['p75'])}",
            f"• 90th Percentile:          {format_currency(stats['p90'])}",
            f"• Interquartile Range (IQR): {format_currency(stats['iqr'])}",
            "",
            "-" * 70,
            "2. CATEGORY BREAKDOWN & SHARE (Pandas Aggregation)",
            "-" * 70
        ]

        if not cat_df.empty:
            cat_rows = []
            for _, r in cat_df.iterrows():
                cat_rows.append([
                    r["Category"],
                    format_currency(r["Total Spent"]),
                    int(r["Count"]),
                    format_currency(r["Average"]),
                    f"{r['% of Total']}%"
                ])
            lines.append(format_table(["Category", "Total Spent", "Count", "Average", "% Share"], cat_rows))
        else:
            lines.append("No category spending data available.")

        lines.extend([
            "",
            "-" * 70,
            "3. MONTHLY EXPENDITURE TRAJECTORY",
            "-" * 70
        ])

        if not month_df.empty:
            month_rows = []
            for _, r in month_df.iterrows():
                month_rows.append([
                    r["Month"],
                    format_currency(r["Total Spent"]),
                    int(r["Transactions"]),
                    format_currency(r["Avg per Txn"]),
                    str(r["Top Category"])
                ])
            lines.append(format_table(["Month", "Total Spent", "Txns", "Avg/Txn", "Top Category"], month_rows))
        else:
            lines.append("No monthly trend data available.")

        lines.extend([
            "",
            "-" * 70,
            "4. TOP 5 HIGHEST TRANSACTIONS",
            "-" * 70
        ])

        if top_exp:
            top_rows = [
                [f"#{e.id}", e.date, e.category, e.title, format_currency(e.amount), e.payment_method]
                for e in top_exp
            ]
            lines.append(format_table(["ID", "Date", "Category", "Title", "Amount", "Payment Method"], top_rows))
        else:
            lines.append("No transactions logged.")

        if outliers:
            lines.extend([
                "",
                "-" * 70,
                "5. STATISTICAL OUTLIER TRANSACTIONS (IQR Analysis)",
                "-" * 70,
                f"Found {len(outliers)} transaction(s) exceeding normal spending distribution threshold:"
            ])
            out_rows = [
                [f"#{e.id}", e.date, e.category, e.title, format_currency(e.amount)]
                for e in outliers
            ]
            lines.append(format_table(["ID", "Date", "Category", "Title", "Amount"], out_rows))

        # Budget Check
        if budget:
            spending_map = self.analytics.get_category_spending_map()
            budget_eval = budget.evaluate_spending(spending_map)
            lines.extend([
                "",
                "-" * 70,
                "6. BUDGET COMPLIANCE & THRESHOLD ALERTS",
                "-" * 70
            ])
            b_rows = []
            for b in budget_eval:
                b_rows.append([
                    b["category"],
                    format_currency(b["limit"]),
                    format_currency(b["spent"]),
                    format_currency(b["remaining"]),
                    f"{b['percent_used']}%",
                    b["status"]
                ])
            lines.append(format_table(["Category", "Budget Limit", "Actual Spent", "Remaining", "% Used", "Status"], b_rows))

        lines.extend([
            "",
            "=" * 70,
            "                        END OF REPORT",
            "=" * 70
        ])

        return "\n".join(lines)

    # =========================================================================
    # 2. File Exporters (.txt, .md)
    # =========================================================================

    def export_text_report(self, budget: Optional[Budget] = None, filename: str = "financial_report.txt") -> str:
        """Saves the executive report as a plain text file."""
        report_content = self.generate_executive_report(budget)
        file_path = os.path.join(self.reports_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        return file_path

    def export_markdown_report(self, budget: Optional[Budget] = None, filename: str = "financial_report.md") -> str:
        """Generates and exports an aesthetically formatted Markdown report."""
        stats = self.analytics.compute_numpy_statistics()
        cat_df = self.analytics.get_category_summary()
        month_df = self.analytics.get_monthly_summary()
        top_exp = self.analytics.get_top_expenses(5)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        md_content = f"""# 📊 Smart Financial Analytics & Expense Report

**Generated on:** `{timestamp}`  
**Total Records:** `{stats['count']}`

---

## 📈 1. Statistical Summary (NumPy)

| Metric | Value | Metric | Value |
| :--- | :--- | :--- | :--- |
| **Total Expenditure** | **{format_currency(stats['total'])}** | **Std Deviation** | {format_currency(stats['std_dev'])} |
| **Mean (Average)** | {format_currency(stats['mean'])} | **25th Percentile** | {format_currency(stats['p25'])} |
| **Median** | {format_currency(stats['median'])} | **75th Percentile** | {format_currency(stats['p75'])} |
| **Min Transaction** | {format_currency(stats['min'])} | **90th Percentile** | {format_currency(stats['p90'])} |
| **Max Transaction** | {format_currency(stats['max'])} | **IQR** | {format_currency(stats['iqr'])} |

---

## 🍔 2. Category Breakdown (Pandas)

| Category | Total Spent | Count | Average | % Share |
| :--- | :--- | :--- | :--- | :--- |
"""
        for _, r in cat_df.iterrows():
            md_content += f"| {r['Category']} | {format_currency(r['Total Spent'])} | {int(r['Count'])} | {format_currency(r['Average'])} | {r['% of Total']}% |\n"

        md_content += "\n---\n\n## 📅 3. Monthly Trends\n\n| Month | Total Spent | Transactions | Avg / Txn | Top Category |\n| :--- | :--- | :--- | :--- | :--- |\n"
        for _, r in month_df.iterrows():
            md_content += f"| {r['Month']} | {format_currency(r['Total Spent'])} | {int(r['Transactions'])} | {format_currency(r['Avg per Txn'])} | {r['Top Category']} |\n"

        md_content += "\n---\n\n## 🏆 4. Top 5 Transactions\n\n| ID | Date | Category | Title | Amount | Method |\n| :--- | :--- | :--- | :--- | :--- | :--- |\n"
        for e in top_exp:
            md_content += f"| #{e.id} | {e.date} | {e.category} | {e.title} | **{format_currency(e.amount)}** | {e.payment_method} |\n"

        if budget:
            spending_map = self.analytics.get_category_spending_map()
            budget_eval = budget.evaluate_spending(spending_map)
            md_content += "\n---\n\n## 🎯 5. Budget Health\n\n| Category | Budget Limit | Actual Spent | Remaining | % Used | Status |\n| :--- | :--- | :--- | :--- | :--- | :--- |\n"
            for b in budget_eval:
                badge = "🔴" if b["severity"] == "danger" else ("🟡" if b["severity"] == "warning" else "🟢")
                md_content += f"| {b['category']} | {format_currency(b['limit'])} | {format_currency(b['spent'])} | {format_currency(b['remaining'])} | {b['percent_used']}% | {badge} {b['status']} |\n"

        file_path = os.path.join(self.reports_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        return file_path
