import os
import sys

sys.path.append(os.path.dirname(__file__))

from app.database import init_db, save_statement

def seed():
    print("Seeding database with sample statement...")
    init_db()
    
    metadata = {
        "filename": "HDFC_Statement_April2024_Sample.pdf",
        "account_holder": "JOHN DOE",
        "account_number": "50100098765432",
        "bank_name": "HDFC Bank",
        "branch": "KORAMANGALA",
        "ifsc": "HDFC0000123",
        "start_date": "2024-04-01",
        "end_date": "2024-04-30",
        "opening_balance": 10000.0,
        "closing_balance": 41103.0,
        "total_credits_count": 2,
        "total_credits_amount": 75500.0,
        "total_debits_count": 11,
        "total_debits_amount": 44397.0
    }
    
    transactions = [
        {
            "date": "2024-04-01",
            "value_date": "2024-04-01",
            "description": "NEFT CR SALARY FOR APR 2024",
            "ref_no": "N20240401001",
            "debit": 0.0,
            "credit": 75000.0,
            "balance": 85000.0,
            "category": "Salary"
        },
        {
            "date": "2024-04-03",
            "value_date": "2024-04-03",
            "description": "UPI-ZOMATO-ORDER-443@OKSBI FOOD ORDER",
            "ref_no": "U20240403002",
            "debit": 450.0,
            "credit": 0.0,
            "balance": 84550.0,
            "category": "Food & Dining"
        },
        {
            "date": "2024-04-05",
            "value_date": "2024-04-05",
            "description": "CASH WDL SELF FROM KORAMANGALA ATM",
            "ref_no": "A20240405003",
            "debit": 5000.0,
            "credit": 0.0,
            "balance": 79550.0,
            "category": "Cash Withdrawal"
        },
        {
            "date": "2024-04-07",
            "value_date": "2024-04-07",
            "description": "NACH DR HDFC LOAN EMI AC 9982",
            "ref_no": "E20240407004",
            "debit": 12000.0,
            "credit": 0.0,
            "balance": 67550.0,
            "category": "EMI / Loan"
        },
        {
            "date": "2024-04-10",
            "value_date": "2024-04-10",
            "description": "AMAZON IN-RETAIL ORDER 928340",
            "ref_no": "S20240410005",
            "debit": 2300.0,
            "credit": 0.0,
            "balance": 65250.0,
            "category": "Shopping"
        },
        {
            "date": "2024-04-12",
            "value_date": "2024-04-12",
            "description": "NETFLIX MOVIE SUBSCRIPTION",
            "ref_no": "ET2024041206",
            "debit": 649.0,
            "credit": 0.0,
            "balance": 64601.0,
            "category": "Entertainment"
        },
        {
            "date": "2024-04-15",
            "value_date": "2024-04-15",
            "description": "AIRTEL POSTPAID MOBILE RECHARGE",
            "ref_no": "T20240415007",
            "debit": 799.0,
            "credit": 0.0,
            "balance": 63802.0,
            "category": "Telecom"
        },
        {
            "date": "2024-04-18",
            "value_date": "2024-04-18",
            "description": "APOLLO PHARMACY MEDICINES",
            "ref_no": "H20240418008",
            "debit": 1200.0,
            "credit": 0.0,
            "balance": 62602.0,
            "category": "Healthcare"
        },
        {
            "date": "2024-04-20",
            "value_date": "2024-04-20",
            "description": "UDEMY COURSE FEES PYTHON",
            "ref_no": "ED2024042009",
            "debit": 499.0,
            "credit": 0.0,
            "balance": 62103.0,
            "category": "Education"
        },
        {
            "date": "2024-04-22",
            "value_date": "2024-04-22",
            "description": "GROWW SECURITIES MUTUAL FUND SIP",
            "ref_no": "I20240422010",
            "debit": 5000.0,
            "credit": 0.0,
            "balance": 57103.0,
            "category": "Investments"
        },
        {
            "date": "2024-04-25",
            "value_date": "2024-04-25",
            "description": "RENT FOR APR 2024 TRANSFER TO LANDLORD",
            "ref_no": "R20240425011",
            "debit": 15000.0,
            "credit": 0.0,
            "balance": 42103.0,
            "category": "Rent"
        },
        {
            "date": "2024-04-28",
            "value_date": "2024-04-28",
            "description": "UPI-PHONEPE-TRANSFER TO FRIEND",
            "ref_no": "U20240428012",
            "debit": 1500.0,
            "credit": 0.0,
            "balance": 40603.0,
            "category": "UPI / Transfer"
        },
        {
            "date": "2024-04-29",
            "value_date": "2024-04-29",
            "description": "REFUND FOR FAILED RETAIL TRANSACTION",
            "ref_no": "CR2024042913",
            "debit": 0.0,
            "credit": 500.0,
            "balance": 41103.0,
            "category": "Other"
        }
    ]
    
    save_statement(metadata, transactions)
    print("Database seeded successfully with sample statement!")

if __name__ == "__main__":
    seed()
