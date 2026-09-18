"""
Interactive CLI Terminal Interface for Smart Personal Expense Tracker & Analyzer.
Demonstrates: User input loops, Error resilience, Formatted Menus, Visual Feedback, ANSI Colors.
"""

import sys
import os
from datetime import datetime
from typing import List, Optional

# Enable UTF-8 encoding for Windows console to handle emojis cleanly
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from ..services.expense_manager import ExpenseManager
from ..services.analytics_engine import AnalyticsEngine
from ..services.visualizer import Visualizer
from ..services.report_generator import ReportGenerator
from ..models.category import DEFAULT_CATEGORIES, get_category_names, get_category_icon
from ..utils.validators import ALLOWED_PAYMENT_METHODS, ValidationError, ExpenseNotFoundError
from ..utils.formatters import Colors, colorize, format_currency, format_table


class ExpenseTrackerCLI:
    """
    Main Terminal UI controller for interactive user operations.
    """

    def __init__(self, manager: Optional[ExpenseManager] = None):
        self.manager = manager or ExpenseManager()
        self.analytics = AnalyticsEngine(self.manager.get_all_expenses())
        self.visualizer = Visualizer(self.analytics)
        self.reporter = ReportGenerator(self.analytics)

    def _sync_analytics(self) -> None:
        """Synchronizes analytics engine with current manager state."""
        self.analytics.set_expenses(self.manager.get_all_expenses())

    # --- Banner & Display Helpers ---

    def print_banner(self) -> None:
        """Prints application header banner."""
        banner = f"""
{Colors.CYAN}{Colors.BOLD}========================================================================
       🚀 SMART PERSONAL EXPENSE TRACKER & FINANCIAL ANALYZER
========================================================================{Colors.RESET}"""
        print(banner)

    def print_menu(self) -> None:
        """Prints main options menu."""
        count = self.manager.count()
        total = self.manager.get_total_spent()
        status_line = f"{Colors.DIM}Current Database: {count} transactions | Total Spent: {format_currency(total)}{Colors.RESET}"

        menu = f"""
{status_line}

{Colors.BOLD}--- MAIN MENU ---{Colors.RESET}
  {Colors.GREEN} 1.{Colors.RESET} Add Expense
  {Colors.GREEN} 2.{Colors.RESET} View All Expenses
  {Colors.GREEN} 3.{Colors.RESET} Update Expense
  {Colors.GREEN} 4.{Colors.RESET} Delete Expense
  {Colors.GREEN} 5.{Colors.RESET} Search Expenses
  {Colors.GREEN} 6.{Colors.RESET} Filter Expenses (Category / Date / Amount)
  {Colors.CYAN} 7.{Colors.RESET} Expense Summary & NumPy Statistics
  {Colors.CYAN} 8.{Colors.RESET} Category Breakdown (Pandas)
  {Colors.CYAN} 9.{Colors.RESET} Monthly Trend Analysis (Pandas)
  {Colors.BLUE}10.{Colors.RESET} Generate Charts (Matplotlib Visualizations)
  {Colors.BLUE}11.{Colors.RESET} Export Reports (.txt, .md, .csv)
  {Colors.YELLOW}12.{Colors.RESET} Budget Management & Target Alerts
  {Colors.YELLOW}13.{Colors.RESET} Load Realistic Sample Dataset
  {Colors.RED}14.{Colors.RESET} Clear All Data
  {Colors.RED} 0.{Colors.RESET} Exit Application
"""
        print(menu)

    # --- Input Prompt Helpers ---

    def _prompt_category(self, current: Optional[str] = None) -> str:
        """Prompts user to select category from a numbered list."""
        categories = get_category_names()
        print(f"\n{Colors.BOLD}Select Category:{Colors.RESET}")
        for idx, cat in enumerate(categories, start=1):
            icon = get_category_icon(cat)
            print(f"  {idx:2d}. {icon} {cat}")

        while True:
            prompt = f"Enter choice (1-{len(categories)})" + (f" [Enter for '{current}']" if current else "") + ": "
            user_in = input(prompt).strip()
            if not user_in and current:
                return current
            if user_in.isdigit():
                val = int(user_in)
                if 1 <= val <= len(categories):
                    return categories[val - 1]
            print(colorize("Invalid selection. Please choose a number from the list.", Colors.RED))

    def _prompt_payment_method(self, current: Optional[str] = None) -> str:
        """Prompts user to select payment method from list."""
        methods = ALLOWED_PAYMENT_METHODS
        print(f"\n{Colors.BOLD}Select Payment Method:{Colors.RESET}")
        for idx, m in enumerate(methods, start=1):
            print(f"  {idx}. {m}")

        while True:
            prompt = f"Enter choice (1-{len(methods)})" + (f" [Enter for '{current}']" if current else "") + ": "
            user_in = input(prompt).strip()
            if not user_in and current:
                return current
            if user_in.isdigit():
                val = int(user_in)
                if 1 <= val <= len(methods):
                    return methods[val - 1]
            print(colorize("Invalid choice. Please choose a number from the list.", Colors.RED))

    def _prompt_date(self, current: Optional[str] = None) -> str:
        """Prompts for date in YYYY-MM-DD format, defaults to today or current."""
        today_str = datetime.now().strftime("%Y-%m-%d")
        default = current or today_str
        while True:
            val = input(f"Date (YYYY-MM-DD) [Default: {default}]: ").strip()
            if not val:
                return default
            try:
                from ..utils.validators import validate_date
                return validate_date(val)
            except ValidationError as err:
                print(colorize(f"Error: {err}", Colors.RED))

    def _prompt_amount(self, current: Optional[float] = None) -> float:
        """Prompts for valid positive monetary amount."""
        while True:
            prompt = f"Amount ($)" + (f" [Default: {current:.2f}]" if current is not None else "") + ": "
            val = input(prompt).strip()
            if not val and current is not None:
                return current
            try:
                from ..utils.validators import validate_amount
                return validate_amount(val)
            except ValidationError as err:
                print(colorize(f"Error: {err}", Colors.RED))

    # --- Menu Action Handlers ---

    def handle_add_expense(self) -> None:
        """Handles adding a new expense record."""
        print(f"\n{Colors.BOLD}{Colors.GREEN}>>> ADD NEW EXPENSE <<<{Colors.RESET}")
        
        title = input("Expense Title / Item Description: ").strip()
        while not title:
            print(colorize("Title cannot be empty.", Colors.RED))
            title = input("Expense Title / Item Description: ").strip()

        amount = self._prompt_amount()
        category = self._prompt_category()
        date = self._prompt_date()
        method = self._prompt_payment_method()
        notes = input("Optional Notes: ").strip()

        try:
            exp = self.manager.add_expense(
                title=title,
                amount=amount,
                category=category,
                date=date,
                payment_method=method,
                notes=notes
            )
            self._sync_analytics()
            print(colorize(f"\n✅ Successfully added expense #{exp.id}: '{exp.title}' for {format_currency(exp.amount)}", Colors.GREEN))

            # Budget alert check
            limit = self.manager.budget.get_category_limit(category)
            spending = self.analytics.get_category_spending_map().get(category, 0.0)
            if limit > 0 and spending > limit:
                print(colorize(f"⚠️  ALERT: Total spending for '{category}' ({format_currency(spending)}) exceeds monthly budget ({format_currency(limit)})!", Colors.YELLOW))
        except Exception as err:
            print(colorize(f"Failed to add expense: {err}", Colors.RED))

    def handle_view_expenses(self, expenses: Optional[List] = None, title: str = "ALL RECORDED EXPENSES") -> None:
        """Displays list of expenses in a structured ASCII table."""
        exp_list = expenses if expenses is not None else self.manager.get_all_expenses()
        if not exp_list:
            print(colorize("\nℹ️  No expenses recorded yet. Use Option 1 or Option 13 to load sample data.", Colors.YELLOW))
            return

        headers = ["ID", "Date", "Category", "Title", "Amount", "Method", "Notes"]
        rows = []
        for e in exp_list:
            rows.append([
                f"#{e.id}",
                e.date,
                f"{e.icon} {e.category}",
                e.title[:25],
                format_currency(e.amount),
                e.payment_method,
                e.notes[:20] if e.notes else "-"
            ])

        print(format_table(headers, rows, title=title))
        total = sum(e.amount for e in exp_list)
        print(f"{Colors.BOLD}Total: {format_currency(total)} across {len(exp_list)} record(s).{Colors.RESET}")

    def handle_update_expense(self) -> None:
        """Handles updating an existing expense."""
        print(f"\n{Colors.BOLD}{Colors.GREEN}>>> UPDATE EXPENSE <<<{Colors.RESET}")
        val = input("Enter Expense ID to update: ").strip()
        if not val.isdigit():
            print(colorize("ID must be a number.", Colors.RED))
            return

        exp_id = int(val)
        try:
            exp = self.manager.get_expense(exp_id)
        except ExpenseNotFoundError as err:
            print(colorize(str(err), Colors.RED))
            return

        print(f"\nEditing: {exp}")
        print(f"{Colors.DIM}(Press Enter on any field to keep current value){Colors.RESET}")

        new_title = input(f"Title [{exp.title}]: ").strip() or exp.title
        new_amount = self._prompt_amount(current=exp.amount)
        new_category = self._prompt_category(current=exp.category)
        new_date = self._prompt_date(current=exp.date)
        new_method = self._prompt_payment_method(current=exp.payment_method)
        new_notes = input(f"Notes [{exp.notes}]: ").strip()
        if not new_notes:
            new_notes = exp.notes

        try:
            self.manager.update_expense(
                exp_id,
                title=new_title,
                amount=new_amount,
                category=new_category,
                date=new_date,
                payment_method=new_method,
                notes=new_notes
            )
            self._sync_analytics()
            print(colorize(f"\n✅ Expense #{exp_id} updated successfully!", Colors.GREEN))
        except Exception as err:
            print(colorize(f"Update failed: {err}", Colors.RED))

    def handle_delete_expense(self) -> None:
        """Handles deleting an expense record."""
        print(f"\n{Colors.BOLD}{Colors.RED}>>> DELETE EXPENSE <<<{Colors.RESET}")
        val = input("Enter Expense ID to delete: ").strip()
        if not val.isdigit():
            print(colorize("ID must be a number.", Colors.RED))
            return

        exp_id = int(val)
        try:
            exp = self.manager.get_expense(exp_id)
            confirm = input(f"Are you sure you want to delete #{exp.id} '{exp.title}' (${exp.amount:.2f})? (y/N): ").strip().lower()
            if confirm == "y":
                self.manager.delete_expense(exp_id)
                self._sync_analytics()
                print(colorize(f"✅ Expense #{exp_id} deleted successfully.", Colors.GREEN))
            else:
                print("Deletion cancelled.")
        except ExpenseNotFoundError as err:
            print(colorize(str(err), Colors.RED))

    def handle_search(self) -> None:
        """Handles keyword searching."""
        print(f"\n{Colors.BOLD}>>> SEARCH EXPENSES <<<{Colors.RESET}")
        query = input("Enter search keyword (matches Title, Category, Notes, Method): ").strip()
        if not query:
            print("Empty query.")
            return

        results = self.manager.search_expenses(query)
        self.handle_view_expenses(results, title=f"SEARCH RESULTS FOR: '{query}'")

    def handle_filter(self) -> None:
        """Handles multi-criteria filtering."""
        print(f"\n{Colors.BOLD}>>> FILTER EXPENSES <<<{Colors.RESET}")
        print("Leave any filter blank to skip.")

        cat_choice = input("Filter by Category name (or blank for all): ").strip()
        min_amt_str = input("Min Amount ($): ").strip()
        max_amt_str = input("Max Amount ($): ").strip()
        start_d = input("Start Date (YYYY-MM-DD): ").strip()
        end_d = input("End Date (YYYY-MM-DD): ").strip()

        min_amt = float(min_amt_str) if min_amt_str else None
        max_amt = float(max_amt_str) if max_amt_str else None

        filtered = self.manager.filter_expenses(
            category=cat_choice if cat_choice else None,
            min_amount=min_amt,
            max_amount=max_amt,
            start_date=start_d if start_d else None,
            end_date=end_d if end_d else None
        )
        self.handle_view_expenses(filtered, title="FILTERED EXPENSES")

    def handle_summary_stats(self) -> None:
        """Displays descriptive statistics calculated via NumPy."""
        self._sync_analytics()
        stats = self.analytics.compute_numpy_statistics()

        if stats["count"] == 0:
            print(colorize("No data to analyze.", Colors.YELLOW))
            return

        headers = ["Statistical Metric (NumPy Engine)", "Computed Value"]
        rows = [
            ["Total Transactions", str(stats["count"])],
            ["Total Spending", format_currency(stats["total"])],
            ["Mean (Average)", format_currency(stats["mean"])],
            ["Median (50th Percentile)", format_currency(stats["median"])],
            ["Minimum Expense", format_currency(stats["min"])],
            ["Maximum Expense", format_currency(stats["max"])],
            ["Standard Deviation", format_currency(stats["std_dev"])],
            ["Variance", f"{stats['variance']:,.2f}"],
            ["25th Percentile (Q1)", format_currency(stats["p25"])],
            ["75th Percentile (Q3)", format_currency(stats["p75"])],
            ["90th Percentile", format_currency(stats["p90"])],
            ["Interquartile Range (IQR)", format_currency(stats["iqr"])]
        ]
        print(format_table(headers, rows, title="DESCRIPTIVE FINANCIAL METRICS (NumPy)"))

    def handle_category_analysis(self) -> None:
        """Displays category aggregations via Pandas."""
        self._sync_analytics()
        cat_df = self.analytics.get_category_summary()
        if cat_df.empty:
            print(colorize("No data for category analysis.", Colors.YELLOW))
            return

        headers = ["Category", "Total Spent", "Count", "Average", "% Share"]
        rows = []
        for _, r in cat_df.iterrows():
            rows.append([
                r["Category"],
                format_currency(r["Total Spent"]),
                int(r["Count"]),
                format_currency(r["Average"]),
                f"{r['% of Total']}%"
            ])
        print(format_table(headers, rows, title="CATEGORY BREAKDOWN & AGGREGATIONS (Pandas)"))

    def handle_monthly_analysis(self) -> None:
        """Displays monthly spending trends via Pandas."""
        self._sync_analytics()
        month_df = self.analytics.get_monthly_summary()
        if month_df.empty:
            print(colorize("No data for monthly analysis.", Colors.YELLOW))
            return

        headers = ["Month", "Total Spent", "Txns", "Avg/Txn", "Top Category"]
        rows = []
        for _, r in month_df.iterrows():
            rows.append([
                r["Month"],
                format_currency(r["Total Spent"]),
                int(r["Transactions"]),
                format_currency(r["Avg per Txn"]),
                str(r["Top Category"])
            ])
        print(format_table(headers, rows, title="MONTHLY SPENDING ANALYSIS (Pandas)"))

    def handle_generate_charts(self) -> None:
        """Generates and exports Matplotlib charts."""
        self._sync_analytics()
        if self.manager.count() == 0:
            print(colorize("No expense records available to plot.", Colors.YELLOW))
            return

        print(f"\n{Colors.BOLD}Select Chart to Generate:{Colors.RESET}")
        print("  1. Category Breakdown (Donut Chart)")
        print("  2. Monthly Trend (Bar Chart)")
        print("  3. Daily Timeline & Cumulative Growth (Line/Area Chart)")
        print("  4. Budget vs. Actual Comparison")
        print("  5. Master 4-Panel Executive Dashboard")
        print("  6. Generate ALL Charts at once")

        choice = input("Enter choice (1-6): ").strip()
        print("\nRendering chart(s) with Matplotlib...")

        paths = []
        if choice == "1":
            paths.append(self.visualizer.plot_category_pie())
        elif choice == "2":
            paths.append(self.visualizer.plot_monthly_bar())
        elif choice == "3":
            paths.append(self.visualizer.plot_daily_trend())
        elif choice == "4":
            paths.append(self.visualizer.plot_budget_vs_actual(self.manager.budget))
        elif choice == "5":
            paths.append(self.visualizer.plot_dashboard(self.manager.budget))
        elif choice == "6":
            paths.append(self.visualizer.plot_category_pie())
            paths.append(self.visualizer.plot_monthly_bar())
            paths.append(self.visualizer.plot_daily_trend())
            paths.append(self.visualizer.plot_budget_vs_actual(self.manager.budget))
            paths.append(self.visualizer.plot_dashboard(self.manager.budget))
        else:
            print(colorize("Invalid option.", Colors.RED))
            return

        for p in paths:
            if p:
                print(colorize(f"📊 Chart successfully saved: {p}", Colors.GREEN))

    def handle_export_reports(self) -> None:
        """Exports reports in txt, markdown, or csv format."""
        self._sync_analytics()
        if self.manager.count() == 0:
            print(colorize("No data to export.", Colors.YELLOW))
            return

        print(f"\n{Colors.BOLD}Select Export Format:{Colors.RESET}")
        print("  1. Formatted Plain Text Report (.txt)")
        print("  2. Rich Markdown Report (.md)")
        print("  3. Raw CSV Data Export (.csv)")
        print("  4. Export All Formats")

        choice = input("Enter choice (1-4): ").strip()
        if choice == "1":
            path = self.reporter.export_text_report(self.manager.budget)
            print(colorize(f"📄 Text report generated at: {path}", Colors.GREEN))
        elif choice == "2":
            path = self.reporter.export_markdown_report(self.manager.budget)
            print(colorize(f"📑 Markdown report generated at: {path}", Colors.GREEN))
        elif choice == "3":
            path = self.manager.export_to_csv()
            print(colorize(f"📁 CSV dataset exported to: {path}", Colors.GREEN))
        elif choice == "4":
            p1 = self.reporter.export_text_report(self.manager.budget)
            p2 = self.reporter.export_markdown_report(self.manager.budget)
            p3 = self.manager.export_to_csv()
            print(colorize(f"✅ All reports exported successfully:\n  - {p1}\n  - {p2}\n  - {p3}", Colors.GREEN))
        else:
            print(colorize("Invalid choice.", Colors.RED))

    def handle_budget_management(self) -> None:
        """Manages monthly category limits and inspects status."""
        self._sync_analytics()
        spending_map = self.analytics.get_category_spending_map()
        eval_list = self.manager.budget.evaluate_spending(spending_map)

        headers = ["Category", "Monthly Limit", "Actual Spent", "Remaining", "% Used", "Status"]
        rows = []
        for b in eval_list:
            status_str = colorize(b["status"], Colors.RED if b["severity"] == "danger" else (Colors.YELLOW if b["severity"] == "warning" else Colors.GREEN))
            rows.append([
                b["category"],
                format_currency(b["limit"]),
                format_currency(b["spent"]),
                format_currency(b["remaining"]),
                f"{b['percent_used']}%",
                status_str
            ])
        print(format_table(headers, rows, title="BUDGET LIMITS & STATUS EVALUATION"))

        print("\nOptions:")
        print("  1. Update Category Monthly Budget")
        print("  2. Return to Main Menu")
        c = input("Choice: ").strip()
        if c == "1":
            cat = self._prompt_category()
            limit = self._prompt_amount(current=self.manager.budget.get_category_limit(cat))
            self.manager.budget.set_category_limit(cat, limit)
            print(colorize(f"✅ Updated budget limit for '{cat}' to {format_currency(limit)}", Colors.GREEN))

    def handle_load_samples(self) -> None:
        """Populates realistic sample expenses."""
        confirm = input("Populate 40 realistic sample transactions spanning 90 days? (y/N): ").strip().lower()
        if confirm == "y":
            count = self.manager.populate_sample_data(count=40, days_back=90)
            self._sync_analytics()
            print(colorize(f"\n🎉 Loaded {count} sample expense transactions successfully!", Colors.GREEN))
            self.handle_view_expenses()

    def handle_clear_all(self) -> None:
        """Clears all data."""
        confirm = input("⚠️ WARNING: This will delete ALL stored expenses. Are you sure? (type 'DELETE'): ").strip()
        if confirm == "DELETE":
            self.manager.clear_all()
            self._sync_analytics()
            print(colorize("Database has been reset.", Colors.YELLOW))
        else:
            print("Operation aborted.")

    # --- Main Application Loop ---

    def run(self) -> None:
        """Starts interactive CLI application loop."""
        self.print_banner()
        while True:
            try:
                self.print_menu()
                choice = input(f"{Colors.BOLD}Enter your choice (0-14): {Colors.RESET}").strip()

                if choice == "1":
                    self.handle_add_expense()
                elif choice == "2":
                    self.handle_view_expenses()
                elif choice == "3":
                    self.handle_update_expense()
                elif choice == "4":
                    self.handle_delete_expense()
                elif choice == "5":
                    self.handle_search()
                elif choice == "6":
                    self.handle_filter()
                elif choice == "7":
                    self.handle_summary_stats()
                elif choice == "8":
                    self.handle_category_analysis()
                elif choice == "9":
                    self.handle_monthly_analysis()
                elif choice == "10":
                    self.handle_generate_charts()
                elif choice == "11":
                    self.handle_export_reports()
                elif choice == "12":
                    self.handle_budget_management()
                elif choice == "13":
                    self.handle_load_samples()
                elif choice == "14":
                    self.handle_clear_all()
                elif choice in ("0", "exit", "quit", "q"):
                    print(f"\n{Colors.CYAN}Thank you for using Smart Expense Tracker! Happy budgeting! 💰{Colors.RESET}\n")
                    break
                else:
                    print(colorize("Invalid selection. Please choose an option from 0 to 14.", Colors.RED))

            except KeyboardInterrupt:
                print(f"\n\n{Colors.YELLOW}Session interrupted. Exiting gracefully.{Colors.RESET}")
                break
            except Exception as err:
                print(colorize(f"\nAn unexpected error occurred: {err}", Colors.RED))
