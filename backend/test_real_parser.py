import sys
import os

# Add parent directory to path so app can be imported
sys.path.append(os.path.dirname(__file__))

from app.parser import HDFCPDFParser
from app.classifier import run_categorization, compute_analytics

def main():
    pdf_path = r"C:\Users\siddh\Downloads\HDFC BANK.pdf"
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return
        
    print(f"Parsing {pdf_path}...")
    parser = HDFCPDFParser(pdf_path)
    metadata, transactions = parser.parse()
    
    print("\n=== METADATA ===")
    for k, v in metadata.items():
        print(f"{k}: {v}")
        
    print(f"\nParsed {len(transactions)} transactions.")
    
    # Run categorization
    transactions = run_categorization(transactions)
    analytics = compute_analytics(transactions)
    
    print("\n=== ANALYTICS ===")
    print(f"Total Transactions: {analytics['total_transactions']}")
    print(f"Percentage Categorized: {analytics['percentage_categorized']}%")
    print(f"Deposits (credits): {metadata['total_credits_amount']}")
    print(f"Withdrawals (debits): {metadata['total_debits_amount']}")
    
    # Print the top 5 largest transactions
    print("\n=== TOP 5 LARGEST TRANSACTIONS ===")
    for idx, tx in enumerate(analytics['top_5_transactions']):
        print(f"{idx+1}. {tx['date']} | {tx['description']} | Amount: {tx['amount']} | Type: {tx['type']} | Category: {tx['category']}")

if __name__ == "__main__":
    main()
