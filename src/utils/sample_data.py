"""
Sample realistic expense dataset generator for demonstrations and tests.
Demonstrates: Randomization, Datetime arithmetic, List comprehensions, Batch entity creation.
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any


SAMPLE_TRANSACTIONS = [
    # Food & Dining
    ("Food & Dining", "DMart / Reliance Fresh Grocery", (1500.0, 5500.0), ["UPI / Online", "Credit Card", "Debit Card"]),
    ("Food & Dining", "Chai & Snacks at Cafe", (80.0, 350.0), ["UPI / Online", "Cash"]),
    ("Food & Dining", "South Indian Restaurant Lunch", (450.0, 1400.0), ["UPI / Online", "Debit Card", "Credit Card"]),
    ("Food & Dining", "Swiggy / Zomato Order", (250.0, 750.0), ["UPI / Online", "Credit Card"]),
    ("Food & Dining", "Local Vegetable & Fruit Market", (200.0, 800.0), ["UPI / Online", "Cash"]),

    # Transportation
    ("Transportation", "Petrol / Fuel Station", (1200.0, 3500.0), ["UPI / Online", "Credit Card", "Debit Card"]),
    ("Transportation", "Monthly Metro Smart Card Recharge", (800.0, 2000.0), ["UPI / Online", "Debit Card"]),
    ("Transportation", "Uber / Ola Auto Ride", (120.0, 450.0), ["UPI / Online", "Cash"]),
    ("Transportation", "Bike / Car Service & Oil Change", (1500.0, 4500.0), ["UPI / Online", "Debit Card"]),

    # Housing & Utilities
    ("Housing & Utilities", "House Rent Payment", (12000.0, 25000.0), ["Bank Transfer", "UPI / Online"]),
    ("Housing & Utilities", "Electricity Bill (BESCOM/MSEB/TNEB)", (1200.0, 3500.0), ["UPI / Online", "Bank Transfer"]),
    ("Housing & Utilities", "JioFiber / Airtel Broadband", (699.0, 1199.0), ["UPI / Online", "Credit Card"]),
    ("Housing & Utilities", "Piped Gas / LPG Cylinder", (850.0, 1100.0), ["UPI / Online", "Bank Transfer"]),

    # Entertainment
    ("Entertainment", "Netflix & Disney+ Hotstar Subscription", (299.0, 699.0), ["UPI / Online", "Credit Card"]),
    ("Entertainment", "PVR Cinemas Movie Tickets", (350.0, 900.0), ["UPI / Online", "Credit Card"]),
    ("Entertainment", "Standup Comedy / Live Concert Show", (800.0, 2500.0), ["UPI / Online", "Credit Card"]),
    ("Entertainment", "PlayStation / Steam Game Purchase", (499.0, 2999.0), ["UPI / Online", "Credit Card"]),

    # Shopping
    ("Shopping", "Amazon / Flipkart Electronics & Gadgets", (800.0, 4500.0), ["UPI / Online", "Credit Card"]),
    ("Shopping", "Myntra / Ajio Clothing & Footwear", (1200.0, 5000.0), ["UPI / Online", "Credit Card", "Debit Card"]),
    ("Shopping", "Home Decor & Kitchen Appliances", (600.0, 3000.0), ["UPI / Online", "Debit Card"]),

    # Healthcare
    ("Healthcare", "Apollo Pharmacy Medicine Refill", (350.0, 1800.0), ["UPI / Online", "Debit Card", "Cash"]),
    ("Healthcare", "Doctor Consultation & Diagnostic Tests", (600.0, 2000.0), ["UPI / Online", "Credit Card"]),
    ("Healthcare", "Cult.fit / Local Gym Monthly Membership", (1200.0, 2500.0), ["UPI / Online", "Credit Card"]),

    # Education
    ("Education", "Udemy / Coursera Python Course", (499.0, 1299.0), ["UPI / Online", "Credit Card"]),
    ("Education", "Engineering & Computer Science Books", (450.0, 1800.0), ["UPI / Online", "Debit Card"]),

    # Investments
    ("Investments", "Monthly Mutual Fund SIP (Groww/Zerodha)", (2500.0, 10000.0), ["UPI / Online", "Bank Transfer"]),
    ("Investments", "Stock Portfolio Investment", (2000.0, 8000.0), ["Bank Transfer", "UPI / Online"]),

    # Personal Care
    ("Personal Care", "Hair Salon & Grooming", (300.0, 900.0), ["UPI / Online", "Cash"]),
    ("Personal Care", "Skincare & Personal Hygiene Products", (400.0, 1500.0), ["UPI / Online", "Debit Card"]),

    # Miscellaneous
    ("Miscellaneous", "India Post / Courier Charges", (150.0, 450.0), ["UPI / Online", "Cash"]),
    ("Miscellaneous", "Community Donation / Gift Contribution", (500.0, 2000.0), ["UPI / Online", "Credit Card"]),
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
