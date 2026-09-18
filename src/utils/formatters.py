"""
Formatting utilities for CLI output, currency, and ASCII tables.
Demonstrates: String manipulation, ANSI Escape Sequences, Defensive formatting with fallback.
"""

from typing import List, Dict, Any, Optional

# ANSI Color codes for rich terminal styling
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    DIM = '\033[2m'
    RESET = '\033[0m'


def colorize(text: str, color_code: str) -> str:
    """Wraps text in ANSI color codes with auto-reset."""
    return f"{color_code}{text}{Colors.RESET}"


def format_currency(amount: float | int, currency_symbol: str = "₹") -> str:
    """
    Formats a numeric amount as currency with commas and 2 decimals.
    Example: 12500.5 -> '₹12,500.50'
    """
    try:
        val = float(amount)
        return f"{currency_symbol}{val:,.2f}"
    except (ValueError, TypeError):
        return f"{currency_symbol}0.00"


def format_table(headers: List[str], rows: List[List[Any]], title: Optional[str] = None) -> str:
    """
    Renders a clean ASCII table with headers, borders, and aligned columns.
    Uses tabulate if installed, with a robust built-in fallback.
    """
    if not rows:
        return "No data to display."

    try:
        from tabulate import tabulate
        table_output = tabulate(rows, headers=headers, tablefmt="fancy_grid")
    except ImportError:
        # Built-in ASCII table renderer
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                cell_str = str(cell)
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(cell_str))
                else:
                    col_widths.append(len(cell_str))

        # Build border lines
        border_top = "┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐"
        border_mid = "├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
        border_bot = "└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘"

        header_line = "│" + "│".join(f" {h:<{col_widths[i]}} " for i, h in enumerate(headers)) + "│"
        row_lines = []
        for row in rows:
            row_str = "│" + "│".join(f" {str(row[i]) if i < len(row) else '':<{col_widths[i]}} " for i in range(len(col_widths))) + "│"
            row_lines.append(row_str)

        table_output = "\n".join([border_top, header_line, border_mid] + row_lines + [border_bot])

    if title:
        header_banner = f"\n{Colors.BOLD}{Colors.CYAN}=== {title} ==={Colors.RESET}\n"
        return header_banner + table_output
    return table_output
