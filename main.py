"""
Main Application Entry Point for Smart Personal Expense Tracker & Financial Analyzer.
Run this script via terminal or VS Code:
    python main.py
"""

import sys
import os
import argparse

# Enable UTF-8 encoding for Windows console to handle emojis cleanly
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure current project directory is in python search path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ui.cli_menu import ExpenseTrackerCLI
from src.services.expense_manager import ExpenseManager
from src.services.analytics_engine import AnalyticsEngine
from src.services.visualizer import Visualizer
from src.services.report_generator import ReportGenerator


def parse_args():
    parser = argparse.ArgumentParser(
        description="Smart Personal Expense Tracker & Financial Analyzer"
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Pre-populate 40 realistic sample expense transactions before launch"
    )
    parser.add_argument(
        "--generate-charts",
        action="store_true",
        help="Automatically generate all 4 visual charts & master dashboard"
    )
    parser.add_argument(
        "--generate-reports",
        action="store_true",
        help="Automatically export text, markdown, and CSV financial reports"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    manager = ExpenseManager()

    if args.sample or manager.count() == 0:
        # If database is completely empty on first launch or sample flag is set, populate realistic demo data
        if manager.count() == 0:
            print("📦 First run detected: Pre-populating sample transaction data for immediate exploration...")
            manager.populate_sample_data(count=40, days_back=90)

    if args.generate_charts or args.generate_reports:
        analytics = AnalyticsEngine(manager.get_all_expenses())
        
        if args.generate_charts:
            print("🎨 Generating visual charts in 'charts/' directory...")
            vis = Visualizer(analytics)
            vis.plot_category_pie()
            vis.plot_monthly_bar()
            vis.plot_daily_trend()
            vis.plot_budget_vs_actual(manager.budget)
            dashboard_path = vis.plot_dashboard(manager.budget)
            print(f"✅ Master dashboard generated at: {dashboard_path}")

        if args.generate_reports:
            print("📑 Generating reports in 'reports/' directory...")
            rep = ReportGenerator(analytics)
            t_path = rep.export_text_report(manager.budget)
            m_path = rep.export_markdown_report(manager.budget)
            c_path = manager.export_to_csv()
            print(f"✅ Reports saved:\n  - {t_path}\n  - {m_path}\n  - {c_path}")

        return

    # Start interactive terminal UI
    cli = ExpenseTrackerCLI(manager)
    cli.run()


if __name__ == "__main__":
    main()
