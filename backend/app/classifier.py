import re
from collections import defaultdict
from datetime import datetime

# Category Keywords mapping, ordered by priority.
# Keywords starting with \b use regex word boundaries, others use substring matching.
CATEGORY_KEYWORDS = {
    "Salary": [
        "SALARY", r"\bSAL\b", "PAYROLL", "STIPEND", "WAGES", "NEFT CR-SALARY", 
        "SALARY CR", "NEFT CR SALARY", "CREDIT-SALARY", "MONTHLY SAL", "BONUS"
    ],
    "EMI / Loan": [
        r"\bEMI\b", r"\bLOAN\b", "HDFC LOAN", "BAJAJ FIN", "NACH DR", "ECS DR", "REPAY", 
        "FINSERV", "CREDITVIDYA", "L&T FINANCE", "LIC HOUSING", "CHOLA", "NACH-DR",
        "UGRO", "POONAWALLA", "TATA CAPITAL", "ADITYA BIRLA",
        "LOAN DR", "LOAN CR", "INSTALLMENT"
    ],
    "Investments": [
        "MUTUAL FUND", r"\bSIP\b", "ZERODHA", "GROWW", "UPSTOX", "NSDL", "CDSL", 
        "DEMAT", "MUTUALFUND", "SECURITIES", "BROKING", "COIN", "INDMONEY", 
        "ANGEL ONE", "5PAISA", "PPF", "NPS", "TREASURY"
    ],
    "Insurance": [
        r"\bLIC\b", "ICICI PRU", "HDFC LIFE", "SBI LIFE", "MAX LIFE", "PREMIUM", 
        "POLICY", "INSURANCE", "LOMBARD", "NIA", "HDFC ERGO", "STAR HEALTH", "ACKO"
    ],
    "Utilities": [
        "ELECTRICITY", "BESCOM", "MSEB", "BSES", "TATA POWER", "GAS", "WATER BILL", 
        "WATERBILL", "POWER", "UTILITY", "KSEB", "UPPCL", "MAHAVITARAN", "MGL", "IGL",
        "ELECTRICITY BILL", "BESCOM BILL", "EB BILL", r"\bGST\b", r"\bTDS\b", r"\bTAX\b",
        "BANK CHARGES", r"\bCHG\b", r"\bCHARGE\b", r"\bFEE\b", "COMMISSION", "SERVICE CHARGE",
        "CONVENIENCE FEE", "DUTY", "SURCHARGE"
    ],
    "Telecom": [
        "AIRTEL", "JIO", "VODAFONE", "BSNL", "RECHARGE", "POSTPAID", "BROADBAND", 
        "WIFI", "TELECOM", "ACT FIBER", "ACTFIBER", "IDEA", "VI RECHARGE"
    ],
    "Entertainment": [
        "NETFLIX", "HOTSTAR", "AMAZON PRIME", "SPOTIFY", "BOOKMYSHOW", "ZEE5", 
        "DISNEY", "YOUTUBE PREMIUM", "MOVIE", "CINEMA", "PLAYSTATION", "STEAM", 
        "SONYLIV", "JIOSAAVN", "PRIME MEMB"
    ],
    "Education": [
        "SCHOOL FEE", "COLLEGE", "UDEMY", "COURSERA", "BYJU", "UNACADEMY", 
        "TUITION", "ACADEMY", "FEES", "INSTRUCTURE", "SCHOOL", "UNIVERSITY", 
        "EDUTECH", "CLASS", "CAMPUS"
    ],
    "Healthcare": [
        "PHARMACY", "APOLLO", "MEDPLUS", "HOSPITAL", "CLINIC", "DIAGNOSTIC", 
        "DENTIST", "PHARMA", "CHEMIST", "DR.", "DOCTOR", "PATHLAB", "MAX HEALTH", 
        "FORTIS", "MEDICINE", "LABS", "HEALTHCARE"
    ],
    "Rent": [
        "RENT", "HOUSE RENT", "RENTAL", "TENANT", "LEASE", "LANDLORD", 
        "SOCIETY DUES", "MYGATE", "NOBROKER", "HOUSING.COM", "FLAT RENT"
    ],
    "Cash Withdrawal": [
        r"\bATM\b", "CASH WDL", "ATM WDL", "WITHDRAWAL", "CASH WITHDRAWAL", 
        "ATM DEBIT", "ATM-WDL", "SELF WDL"
    ],
    "Food & Dining": [
        "SWIGGY", "ZOMATO", "REST", "CAFE", "DOMINOS", "MCDONALD", "HOTEL", 
        "SWEETS", "PIZZA", "BURGER", "FOOD", "KITCHEN", "EATERY", "DINING", 
        "STARBUCKS", "SUBWAY", "HALDIRAM", "DINESOUT", "BARBEQUE", "PIZZAHUT",
        "TAPROOM", "BAKERY", "COFFEE"
    ],
    "Travel": [
        "IRCTC", "UBER", "OLA", "RAPIDO", "IXIGO", "MAKEMYTRIP", "REDBUS", 
        "PETROL", "FUEL", "SHELL", "HPCL", "BPCL", "IOCL", "RAILWAY", "METRO", 
        "CAB", "FLIGHT", "AIRWAYS", "INDIGO", "TICKET", "AUTO", "TOLL", "FASTAG",
        "PAYTM FASTAG", "PARKING"
    ],
    "Shopping": [
        "AMAZON", "FLIPKART", "MYNTRA", "AJIO", "MEESHO", "NYKAA", "RETAIL", 
        "DMART", "RELIANCE DIGITAL", "DECATHLON", "SUPERMARKET", "GROCERY", 
        "MART", "LIFESTYLE", "SPENCERS", "EASYDAY", "MORE RETAIL", "BIGBASKET", 
        "ZEPTO", "BLINKIT", "INSTAMART", "JIO MART", "TATA 1MG", "MAX FASHION",
        "ZARA", "H&M", "D-MART"
    ],
    "UPI / Transfer": [
        "UPI", "BHIM", "PHONEPE", "GPAY", "PAYTM", "NEFT", "IMPS", "RTGS", 
        "TRANSFER", "IMPS-FRM", "IMPS-TO", "IMPS CR", "IMPS DR", "NEFT CR", 
        "NEFT DR", "SENT TO", "RECEIVED FROM", "FUND TRANSFER", "FT-", "FT -",
        "IMPS REF", "INTERNAL TRANSFER", "TPT", "IFT", "INTERNAL", "FUND",
        "NET BANKING", "NETBANKING", "MOBILE BANKING", "DIRECT DEP", "EBA",
        "NWD", "INF", r"\bFT\b", "RTGS CR", "RTGS DR", "NEFT CR", "NEFT DR",
        "IMPS CR", "IMPS DR", "RTGS-", "NEFT-", "IMPS-", "ACH", "ACH-",
        "ACH DR", "ACH CR", "AUTOPAY", "AUTO PAY", "MAB", "TPT DR", "TPT CR",
        "IB DR", "IB CR", "NETBANK", "NET BANK", "DEBIT CARD", "CREDIT CARD",
        "CC Autopay", "CC AUTOPAY", "CC-AUTOPAY", "CREDIT CARD DR", "CREDIT CARD CR"
    ]
}

def classify_transaction(description: str) -> str:
    desc_upper = description.upper()
    
    # Run through category keywords in priority order
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if r"\b" in kw:
                if re.search(kw, desc_upper):
                    return category
            else:
                if kw in desc_upper:
                    return category
                
    return "Other"

def run_categorization(transactions: list) -> list:
    for tx in transactions:
        tx["category"] = classify_transaction(tx["description"])
    return transactions

def detect_salary(transactions: list) -> list:
    """
    Detect salary credit: recurring monthly large credit (same approximate amount, monthly)
    Strictly requires description to contain a salary-related keyword.
    """
    credits = [tx for tx in transactions if tx["credit"] > 0]
    if len(credits) < 2:
        return []
        
    # Group by approximate amount (+-10%)
    amount_groups = []
    visited = set()
    
    for i, tx in enumerate(credits):
        if i in visited:
            continue
            
        group = [tx]
        visited.add(i)
        amt_i = tx["credit"]
        
        for j in range(i + 1, len(credits)):
            if j in visited:
                continue
            amt_j = credits[j]["credit"]
            # Tolerance: 10%
            if abs(amt_i - amt_j) / max(amt_i, amt_j) <= 0.10:
                group.append(credits[j])
                visited.add(j)
                
        if len(group) >= 2:
            amount_groups.append(group)
            
    salaries = []
    for grp in amount_groups:
        dates = []
        for tx in grp:
            try:
                dt = datetime.strptime(tx["date"], "%Y-%m-%d")
                dates.append((dt, tx))
            except ValueError:
                continue
                
        if len(dates) < 2:
            continue
            
        dates.sort(key=lambda x: x[0])
        months_set = {d[0].strftime("%Y-%m") for d in dates}
        
        is_salary = len(months_set) >= 2
        avg_amount = sum(tx["credit"] for tx in grp) / len(grp)
        
        # Check descriptions match salary keywords
        desc_matches = any(
            any(
                (re.search(kw, tx["description"].upper()) if r"\b" in kw else kw in tx["description"].upper())
                for kw in CATEGORY_KEYWORDS["Salary"]
            ) 
            for tx in grp
        )
        
        # In corporate current accounts, restrict salary detection only when explicit keywords match
        if is_salary and desc_matches:
            salaries.append({
                "amount": round(avg_amount, 2),
                "frequency": "Monthly",
                "count": len(grp),
                "pattern": grp[0]["description"],
                "transactions": [
                    {
                        "date": tx["date"],
                        "description": tx["description"],
                        "amount": tx["credit"]
                    } for tx in grp
                ]
            })
            
    return salaries

def detect_emi_loans(transactions: list) -> list:
    """
    Detect EMI/Loan: recurring fixed debits (same amount, monthly pattern)
    Strictly requires ALL transactions in the group to contain an EMI/loan-related keyword.
    Excludes very large transfers (>10L) to avoid false positives on B2B/P2P transfers.
    """
    # Only consider debits that contain an EMI keyword in their description
    emi_keywords = CATEGORY_KEYWORDS["EMI / Loan"]
    
    def has_emi_keyword(description):
        desc_upper = description.upper()
        return any(
            (re.search(kw, desc_upper) if r"\b" in kw else kw in desc_upper)
            for kw in emi_keywords
        )
    
    # Pre-filter: only debits with EMI keywords and amount <= 10,00,000
    debits = [
        tx for tx in transactions 
        if tx["debit"] > 0 and has_emi_keyword(tx["description"]) and tx["debit"] <= 1000000
    ]
    if len(debits) < 2:
        return []
        
    # Group by approximate amount (+-1.5% tolerance)
    amount_groups = []
    visited = set()
    
    for i, tx in enumerate(debits):
        if i in visited:
            continue
            
        group = [tx]
        visited.add(i)
        amt_i = tx["debit"]
        
        for j in range(i + 1, len(debits)):
            if j in visited:
                continue
            amt_j = debits[j]["debit"]
            # Tolerance: 1.5%
            if abs(amt_i - amt_j) / max(amt_i, amt_j) <= 0.015:
                group.append(debits[j])
                visited.add(j)
                
        if len(group) >= 2:
            amount_groups.append(group)
            
    emis = []
    for grp in amount_groups:
        dates = []
        for tx in grp:
            try:
                dt = datetime.strptime(tx["date"], "%Y-%m-%d")
                dates.append((dt, tx))
            except ValueError:
                continue
                
        if len(dates) < 2:
            continue
            
        dates.sort(key=lambda x: x[0])
        months_set = {d[0].strftime("%Y-%m") for d in dates}
        
        is_emi = len(months_set) >= 2
        avg_amount = sum(tx["debit"] for tx in grp) / len(grp)
        
        if is_emi:
            emis.append({
                "amount": round(avg_amount, 2),
                "frequency": "Monthly",
                "count": len(grp),
                "pattern": grp[0]["description"],
                "transactions": [
                    {
                        "date": tx["date"],
                        "description": tx["description"],
                        "amount": tx["debit"]
                    } for tx in grp
                ]
            })
            
    return emis

def compute_analytics(transactions: list) -> dict:
    if not transactions:
        return {}
        
    # 1. Category Summary
    category_summary = defaultdict(lambda: {"debit": 0.0, "credit": 0.0, "count": 0})
    
    # Ensure all mandatory categories appear in summary (even if 0)
    for cat in CATEGORY_KEYWORDS.keys():
        category_summary[cat] = {"debit": 0.0, "credit": 0.0, "count": 0}
    category_summary["Other"] = {"debit": 0.0, "credit": 0.0, "count": 0}
    
    categorized_count = 0
    total_count = len(transactions)
    
    for tx in transactions:
        cat = tx["category"]
        category_summary[cat]["debit"] += tx["debit"]
        category_summary[cat]["credit"] += tx["credit"]
        category_summary[cat]["count"] += 1
        
        if cat != "Other":
            categorized_count += 1
            
    # Round summary details
    for cat in category_summary:
        category_summary[cat]["debit"] = round(category_summary[cat]["debit"], 2)
        category_summary[cat]["credit"] = round(category_summary[cat]["credit"], 2)
        
    # Percent Categorized
    percentage_categorized = round((categorized_count / total_count) * 100, 2) if total_count > 0 else 0.0
    
    # 2. Month-wise Breakdown (grouped by transaction date)
    monthly_flow = defaultdict(lambda: {"inflow": 0.0, "outflow": 0.0, "count": 0})
    for tx in transactions:
        try:
            month = datetime.strptime(tx["date"], "%Y-%m-%d").strftime("%Y-%m")
        except ValueError:
            month = "Unknown"
        monthly_flow[month]["inflow"] += tx["credit"]
        monthly_flow[month]["outflow"] += tx["debit"]
        monthly_flow[month]["count"] += 1
        
    # Round monthly flow
    formatted_monthly_flow = []
    for month in sorted(monthly_flow.keys()):
        formatted_monthly_flow.append({
            "month": month,
            "inflow": round(monthly_flow[month]["inflow"], 2),
            "outflow": round(monthly_flow[month]["outflow"], 2),
            "count": monthly_flow[month]["count"]
        })
        
    # 3. Top 5 Largest Transactions (Sorted by amount)
    sorted_txs = sorted(
        transactions, 
        key=lambda tx: max(tx["credit"], tx["debit"]), 
        reverse=True
    )
    
    top_5 = []
    for tx in sorted_txs[:5]:
        top_5.append({
            "date": tx["date"],
            "description": tx["description"],
            "amount": max(tx["credit"], tx["debit"]),
            "type": "Credit" if tx["credit"] > 0 else "Debit",
            "category": tx["category"]
        })
        
    # 4. Salary and EMI Detections
    salaries = detect_salary(transactions)
    emis = detect_emi_loans(transactions)
    
    return {
        "category_summary": dict(category_summary),
        "monthly_flow": formatted_monthly_flow,
        "top_5_transactions": top_5,
        "salaries": salaries,
        "emis": emis,
        "percentage_categorized": percentage_categorized,
        "total_transactions": total_count
    }
