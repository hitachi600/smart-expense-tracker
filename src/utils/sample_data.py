"""
Sample realistic expense dataset generator for demonstrations and tests.
Demonstrates: Randomization, Datetime arithmetic, List comprehensions, Batch entity creation.
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any


SAMPLE_TRANSACTIONS = [
    # Food & Dining
    ("Food & Dining", "Grocery Supermarket", (35.0, 180.0), ["Credit Card", "Debit Card", "UPI / Online"]),
    ("Food & Dining", "Starbucks Coffee", (4.5, 15.0), ["UPI / Online", "Cash", "Credit Card"]),
    ("Food & Dining", "Italian Bistro Dinner", (45.0, 120.0), ["Credit Card", "Debit Card"]),
    ("Food & Dining", "UberEats Delivery", (18.0, 45.0), ["UPI / Online", "Credit Card"]),
    ("Food & Dining", "Farmers Market Fresh Produce", (20.0, 65.0), ["Cash", "UPI / Online"]),

    # Transportation
    ("Transportation", "Gas Station Fuel", (40.0, 75.0), ["Credit Card", "Debit Card"]),
    ("Transportation", "Monthly Subway Pass", (85.0, 110.0), ["Debit Card", "Credit Card"]),
    ("Transportation", "Uber Ride Downtown", (15.0, 38.0), ["UPI / Online", "Credit Card"]),
    ("Transportation", "Car Maintenance & Oil Change", (90.0, 250.0), ["Credit Card", "Debit Card"]),

    # Housing & Utilities
    ("Housing & Utilities", "Apartment Monthly Rent", (950.0, 1500.0), ["Bank Transfer"]),
    ("Housing & Utilities", "Electricity & Power Bill", (65.0, 140.0), ["UPI / Online", "Bank Transfer"]),
    ("Housing & Utilities", "High-Speed Internet Bill", (55.0, 85.0), ["Credit Card", "UPI / Online"]),
    ("Housing & Utilities", "Water & Sewage Utility", (30.0, 60.0), ["Bank Transfer", "UPI / Online"]),

    # Entertainment
    ("Entertainment", "Netflix & Spotify Subscription", (18.0, 28.0), ["Credit Card"]),
    ("Entertainment", "IMAX Movie Tickets", (25.0, 55.0), ["Credit Card", "UPI / Online"]),
    ("Entertainment", "Concert Ticket", (65.0, 180.0), ["Credit Card"]),
    ("Entertainment", "Steam Game Purchase", (15.0, 60.0), ["UPI / Online", "Credit Card"]),

    # Shopping
    ("Shopping", "Amazon Electronics & Gadgets", (35.0, 150.0), ["Credit Card", "UPI / Online"]),
    ("Shopping", "Clothing & Apparel", (45.0, 210.0), ["Credit Card", "Debit Card"]),
    ("Shopping", "Home Decor & Furnishings", (30.0, 140.0), ["Credit Card", "Debit Card"]),

    # Healthcare
    ("Healthcare", "Pharmacy Prescription Refill", (15.0, 65.0), ["Debit Card", "Cash"]),
    ("Healthcare", "Dental Cleaning & Checkup", (80.0, 180.0), ["Credit Card", "Debit Card"]),
    ("Healthcare", "Gym Membership", (40.0, 65.0), ["Credit Card", "Bank Transfer"]),

    # Education
    ("Education", "Python & Data Science Udemy Course", (15.0, 35.0), ["Credit Card", "UPI / Online"]),
    ("Education", "Textbooks & Technical Books", (30.0, 95.0), ["Credit Card", "Debit Card"]),

    # Investments
    ("Investments", "Monthly Index Fund Contribution", (200.0, 500.0), ["Bank Transfer"]),
    ("Investments", "Stock Portfolio Deposit", (150.0, 400.0), ["Bank Transfer"]),

    # Personal Care
    ("Personal Care", "Haircut & Grooming", (25.0, 55.0), ["Cash", "UPI / Online"]),
    ("Personal Care", "Skincare & Toiletries", (20.0, 70.0), ["Credit Card", "Debit Card"]),

    # Miscellaneous
    ("Miscellaneous", "Post Office Shipping", (10.0, 30.0), ["Cash", "Debit Card"]),
    ("Miscellaneous", "Charity Donation", (25.0, 100.0), ["UPI / Online", "Credit Card"]),
]


def generate_sample_expenses(count: int = 40, days_back: int = 90) -> List[Dict[str, Any]]:
    """
    Generates realistic randomized expense entries spanning the last `days_back` days.

    :param count: Total number of records to generate (default: 40)
    :param days_back: Date span going back in days from current date (default: 90)
    :return: List of dictionary representations of expenses
    """
    random.seed(42)  # For deterministic initial dataset
    today = datetime.now()
    records = []

    for i in range(1, count + 1):
        category, title, (min_amt, max_amt), methods = random.choice(SAMPLE_TRANSACTIONS)
        amount = round(random.uniform(min_amt, max_amt), 2)
        payment_method = random.choice(methods)
        
        # Random date in the past
        days_offset = random.randint(0, days_back)
        txn_date = (today - timedelta(days=days_offset)).strftime("%Y-%m-%d")
        
        notes = f"Auto-generated mock expense #{i}"
        
        records.append({
            "id": i,
            "title": title,
            "amount": amount,
            "category": category,
            "date": txn_date,
            "payment_method": payment_method,
            "notes": notes
        })

    # Sort generated records by date ascending
    records.sort(key=lambda r: r["date"])
    
    # Re-assign sequential IDs after sorting
    for idx, item in enumerate(records, start=1):
        item["id"] = idx

    return records
