"""
Script to generate the comprehensive PROJECT_EXPLANATION_GUIDE.pdf using ReportLab.
"""

import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch


def generate_pdf(filename="PROJECT_EXPLANATION_GUIDE.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Custom Styles
    primary_color = colors.HexColor("#1E3A8A")   # Deep Blue
    secondary_color = colors.HexColor("#0D9488") # Teal
    dark_neutral = colors.HexColor("#1F2937")    # Dark Gray
    light_bg = colors.HexColor("#F8FAFC")        # Slate light
    accent_green = colors.HexColor("#059669")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=primary_color,
        alignment=1, # Center
        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=secondary_color,
        alignment=1,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=primary_color,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=secondary_color,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=dark_neutral,
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3
    )

    qa_q_style = ParagraphStyle(
        'QA_Question',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=primary_color,
        spaceBefore=6,
        spaceAfter=2,
        keepWithNext=True
    )

    qa_a_style = ParagraphStyle(
        'QA_Answer',
        parent=body_style,
        fontName='Helvetica',
        leftIndent=10,
        spaceAfter=6
    )

    script_style = ParagraphStyle(
        'Script_Text',
        parent=body_style,
        fontName='Helvetica-Oblique',
        textColor=colors.HexColor("#334155"),
        leftIndent=10,
        spaceAfter=4
    )

    story = []

    # Title Header
    story.append(Paragraph("Smart Personal Expense Tracker & Financial Analyzer", title_style))
    story.append(Paragraph("Complete Project Explanation, Architecture, Technology Justification & Viva Guide", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceAfter=12))

    # 1. Executive Summary
    story.append(Paragraph("1. Project Overview & Objective", h1_style))
    story.append(Paragraph(
        "<b>Smart Personal Expense Tracker & Financial Analyzer</b> is a production-ready, object-oriented financial management system and data science suite written in Python. Unlike typical beginner CRUD projects that simply record numbers, this application incorporates <b>industry-standard software engineering practices</b>: modular OOP architecture, vectorized statistical computation using <b>NumPy</b>, multi-dimensional time-series aggregation via <b>Pandas</b>, financial data visualization with <b>Matplotlib</b>, resilient atomic file storage with automated backups, dynamic budget compliance tracking, and a 25-case automated test suite with <b>PyTest</b>.",
        body_style
    ))

    # 2. What I Gave NEW (Novelty & Upgrades)
    story.append(Paragraph("2. What Makes This Project Unique (What I Added NEW)", h1_style))
    story.append(Paragraph("To make this project stand out from standard academic submissions, the following enterprise-grade features were engineered:", body_style))

    new_features = [
        ("Advanced OOP & Dependency Inversion:", "Utilized Python's <code>abc.ABC</code> (Abstract Base Classes) to decouple business logic from storage, allowing seamless swapping between JSON and CSV persistence."),
        ("NumPy Statistical Engine:", "Computes Mean, Median, Standard Deviation, Variance, 25th/75th/90th percentiles, and statistical anomaly (outlier) detection using the Interquartile Range (IQR) method."),
        ("Pandas Analytics Suite:", "Performs multi-level <code>groupby</code> aggregations, percentage budget shares, monthly trend pivots, and 7-day moving averages."),
        ("Publication-Ready Visualizations:", "Automatically renders high-resolution charts in <code>charts/</code>: Donut breakdown chart, Monthly expenditure bar chart, Daily timeline & cumulative growth chart, and a 4-in-1 Master Dashboard."),
        ("Proactive Budget Health Alerts:", "Monitors category spending thresholds with real-time feedback: <i>ON TRACK</i> (&lt;85%), <i>WARNING</i> (85%-100%), and <i>EXCEEDED</i> (&gt;100%)."),
        ("Resilient File Persistence:", "Implements atomic file writing (staging to <code>.tmp</code> before replacing) and automated timestamped backups to prevent database corruption."),
        ("Localized Indian Rupee (INR - ₹) Context:", "Tailored with authentic Indian transactions (UPI, Swiggy, Zomato, DMart, Metro passes, Rent) and realistic Indian price ranges."),
        ("Automated PyTest Suite:", "Includes 25 comprehensive unit tests verifying data models, persistence, calculations, and error resilience with 100% pass rate.")
    ]

    for title, desc in new_features:
        story.append(Paragraph(f"• <b>{title}</b> {desc}", bullet_style))

    story.append(Spacer(1, 8))

    # 3. Technologies Used and WHY
    story.append(Paragraph("3. Technology Stack & Technical Justifications (Why I Used Them)", h1_style))
    
    tech_data = [
        [Paragraph("<b>Technology</b>", body_style), Paragraph("<b>Where It Is Used</b>", body_style), Paragraph("<b>Why It Was Chosen (Technical Reason)</b>", body_style)],
        [
            Paragraph("<b>Core Python & OOP</b>", body_style),
            Paragraph("<code>Expense</code>, <code>Category</code>, <code>Budget</code> models", body_style),
            Paragraph("Encapsulation via <code>@property</code> setters ensures strict data validation. Prevents negative amounts, invalid dates, and corrupted state.", body_style)
        ],
        [
            Paragraph("<b>abc.ABC (Interfaces)</b>", body_style),
            Paragraph("<code>StorageInterface</code>", body_style),
            Paragraph("Applies the <b>Dependency Inversion Principle</b> (SOLID). Decouples persistence from business logic, making the code extensible.", body_style)
        ],
        [
            Paragraph("<b>NumPy</b>", body_style),
            Paragraph("<code>AnalyticsEngine</code> statistics", body_style),
            Paragraph("Performs high-speed vectorized C-level math for standard deviation, percentiles (Q1, Q3), and IQR anomaly detection.", body_style)
        ],
        [
            Paragraph("<b>Pandas</b>", body_style),
            Paragraph("Category & Monthly summaries", body_style),
            Paragraph("Provides declarative data manipulation (<code>groupby</code>, <code>agg</code>, <code>rolling</code>) for time-series aggregation without messy loops.", body_style)
        ],
        [
            Paragraph("<b>Matplotlib</b>", body_style),
            Paragraph("<code>Visualizer</code> service", body_style),
            Paragraph("Renders modern, styled financial charts and multi-panel dashboards exported directly to high-res PNG files.", body_style)
        ],
        [
            Paragraph("<b>PyTest</b>", body_style),
            Paragraph("<code>tests/</code> directory (25 tests)", body_style),
            Paragraph("Ensures regression safety, test-driven validation, and guarantees 100% correctness of all mathematical formulas.", body_style)
        ]
    ]

    t = Table(tech_data, colWidths=[1.3*inch, 1.8*inch, 3.8*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ('TEXTCOLOR', (0, 0), (-1, 0), primary_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, light_bg]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t)

    story.append(PageBreak())

    # 4. Step-by-Step Presentation Script
    story.append(Paragraph("4. Step-by-Step Presentation Script (What to Say to Your Professor)", h1_style))
    story.append(Paragraph("Use this 2-minute structured walkthrough during your project demonstration:", body_style))

    story.append(Paragraph("<b>Step 1: Introduction (30 Seconds)</b>", h2_style))
    story.append(Paragraph(
        '"Good morning/afternoon Professor. Today I am presenting my final Python project: <b>Smart Personal Expense Tracker & Financial Analyzer</b>. '
        'Instead of building a simple console tracker, I developed a complete financial analytics system. It combines Object-Oriented Architecture, '
        'data persistence with JSON and CSV, deep statistical computations using <b>NumPy</b>, time-series aggregations with <b>Pandas</b>, and automated financial chart generation with <b>Matplotlib</b>."',
        script_style
    ))

    story.append(Paragraph("<b>Step 2: Live Demonstration of Core Features (45 Seconds)</b>", h2_style))
    story.append(Paragraph(
        '"Let me demonstrate the application live. I run <code>python main.py</code> in the terminal. '
        'By choosing <b>Option 2</b>, we see all recorded expenses formatted in a structured ASCII table in Indian Rupees (₹). '
        'In <b>Option 7</b>, we calculate descriptive statistics using NumPy—including Mean, Median, Standard Deviation, and IQR Percentiles. '
        'In <b>Option 8 & 9</b>, Pandas groups expenses by category and monthly billing periods to reveal spending patterns."',
        script_style
    ))

    story.append(Paragraph("<b>Step 3: Visual Dashboards & Reports (30 Seconds)</b>", h2_style))
    story.append(Paragraph(
        '"When we select <b>Option 10</b>, Matplotlib automatically generates high-resolution charts in the <code>charts/</code> folder—including '
        'a Category Donut chart, a Monthly Bar chart, a Daily Cumulative trendline, and a 4-in-1 Executive Financial Dashboard. '
        'Additionally, <b>Option 11</b> exports formatted Markdown, Plain Text, and CSV reports for easy sharing."',
        script_style
    ))

    story.append(Paragraph("<b>Step 4: Quality & Testing (15 Seconds)</b>", h2_style))
    story.append(Paragraph(
        '"Finally, the codebase is validated with a 25-case automated test suite using <b>PyTest</b>, achieving a 100% pass rate. '
        'The entire project is version-controlled and published on GitHub."',
        script_style
    ))

    story.append(Spacer(1, 6))

    # 5. Top Viva & Interview Questions
    story.append(Paragraph("5. Top 10 Viva & Interview Questions & Model Answers", h1_style))
    
    viva_qa = [
        ("Q1: How is Object-Oriented Programming (OOP) implemented in your project?",
         "We used OOP in three key ways: 1) <b>Encapsulation</b> in <code>Expense</code> using <code>@property</code> getters/setters to validate amounts, dates, and titles; 2) <b>Abstraction & Polymorphism</b> via <code>StorageInterface</code> (using <code>abc.ABC</code>) which decouples storage from business logic; 3) <b>Magic Methods</b> such as <code>__eq__</code> for entity equality, <code>__lt__</code> for natural date sorting, and <code>__str__</code> for clean formatting."),

        ("Q2: Why did you use NumPy instead of standard Python math functions?",
         "Standard Python lists store references to objects, which incurs pointer overhead and slow iteration in dynamic loops. NumPy stores numbers in contiguous C-level memory buffers and executes vectorized SIMD operations. This enables computing standard deviation, variance, percentiles (25th, 75th, 90th), and IQR with superior execution speed and mathematical precision."),

        ("Q3: How does Pandas improve your data analysis pipeline?",
         "Instead of writing complex nested loops and dictionary accumulators, Pandas allows declarative data operations. We convert expenses into a <code>pd.DataFrame</code> and use <code>df.groupby('category')['amount'].agg(...)</code> to compute net spending, average transaction size, and percentage budget share in a single, highly readable operation."),

        ("Q4: What is the purpose of the StorageInterface (Abstract Base Class)?",
         "The <code>StorageInterface</code> follows the <b>Dependency Inversion Principle</b> from SOLID design. It establishes an abstract contract with <code>load()</code>, <code>save()</code>, and <code>create_backup()</code> methods. Because <code>ExpenseManager</code> depends on this abstraction, we can switch from JSON to CSV, SQLite, or cloud storage without changing a single line of business logic."),

        ("Q5: How does your application prevent database corruption?",
         "In <code>JSONStorage</code>, we implemented <b>atomic writes</b>. When saving, data is first written to a temporary file (<code>expenses.json.tmp</code>). Once write verification succeeds, it performs an atomic rename/replace over the target file. If a power cut or crash occurs mid-save, the original data remains undamaged."),

        ("Q6: How does the outlier / anomaly detection work?",
         "We use the statistical <b>Interquartile Range (IQR)</b> method. We calculate Q1 (25th percentile) and Q3 (75th percentile) using NumPy. The IQR is (Q3 - Q1). Any expense exceeding <b>Q3 + (1.5 * IQR)</b> is statistically classified as an anomaly/outlier and flagged in the executive report."),

        ("Q7: How do you handle exceptions and bad user input?",
         "We built a domain-specific custom exception hierarchy inheriting from <code>ExpenseTrackerError</code> (e.g., <code>ValidationError</code>, <code>InvalidExpenseError</code>, <code>ExpenseNotFoundError</code>, <code>StorageError</code>). Every input prompt validates dates (ISO YYYY-MM-DD), positive numeric amounts, and recognized categories before entity creation."),

        ("Q8: How did you test your application?",
         "We used <b>PyTest</b> to create 25 automated unit tests in <code>tests/</code> covering model validation, JSON/CSV persistence, CRUD manager operations, and NumPy/Pandas calculation accuracy. All 25 tests pass in ~1.1 seconds."),

        ("Q9: What happens when a category exceeds its budget?",
         "The <code>Budget</code> model evaluates actual spending against monthly limits. If spending reaches &ge;85%, it triggers a <i>WARNING</i>. If spending exceeds 100%, it flags an <i>EXCEEDED</i> status and alerts the user in the CLI, reports, and visual comparison charts."),

        ("Q10: What future enhancements can be added to this project?",
         "Future extensions include adding a SQLite / PostgreSQL relational database, building an interactive Streamlit or FastAPI web dashboard, and integrating OCR receipt scanning via computer vision.")
    ]

    for q, a in viva_qa:
        story.append(Paragraph(q, qa_q_style))
        story.append(Paragraph(a, qa_a_style))

    # Build PDF
    doc.build(story)
    return filename


if __name__ == "__main__":
    out = generate_pdf()
    print(f"Generated PDF: {out}")
