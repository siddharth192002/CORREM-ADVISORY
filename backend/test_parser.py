import sys
import os
from unittest.mock import patch, MagicMock

# Add app to path
sys.path.append(os.path.dirname(__file__))

from app.parser import HDFCPDFParser
from app.classifier import run_categorization, compute_analytics

def get_mock_words():
    # Helper to generate word dicts with positions
    words = []
    
    # ----------------------------------------------------
    # PAGE 1: HEADERS
    # ----------------------------------------------------
    # Let's add Account Details at top of page 1
    # Account Name: "JOHN DOE"
    words.append({"text": "STATEMENT", "x0": 20, "x1": 80, "top": 40, "bottom": 50})
    words.append({"text": "OF", "x0": 85, "x1": 100, "top": 40, "bottom": 50})
    words.append({"text": "ACCOUNT", "x0": 105, "x1": 155, "top": 40, "bottom": 50})
    words.append({"text": "FOR", "x0": 160, "x1": 180, "top": 40, "bottom": 50})
    words.append({"text": "THE", "x0": 185, "x1": 205, "top": 40, "bottom": 50})
    words.append({"text": "PERIOD", "x0": 210, "x1": 250, "top": 40, "bottom": 50})
    words.append({"text": "FROM", "x0": 255, "x1": 285, "top": 40, "bottom": 50})
    words.append({"text": "01-APR-2024", "x0": 290, "x1": 350, "top": 40, "bottom": 50})
    words.append({"text": "TO", "x0": 355, "x1": 370, "top": 40, "bottom": 50})
    words.append({"text": "30-APR-2024", "x0": 375, "x1": 435, "top": 40, "bottom": 50})
    
    # Account holder
    words.append({"text": "JOHN", "x0": 20, "x1": 50, "top": 70, "bottom": 80})
    words.append({"text": "DOE", "x0": 55, "x1": 80, "top": 70, "bottom": 80})
    
    # A/c number and IFSC
    words.append({"text": "Account", "x0": 20, "x1": 70, "top": 100, "bottom": 110})
    words.append({"text": "No", "x0": 75, "x1": 90, "top": 100, "bottom": 110})
    words.append({"text": ":", "x0": 92, "x1": 95, "top": 100, "bottom": 110})
    words.append({"text": "50100098765432", "x0": 100, "x1": 190, "top": 100, "bottom": 110})
    
    words.append({"text": "IFSC", "x0": 300, "x1": 330, "top": 100, "bottom": 110})
    words.append({"text": "Code", "x0": 335, "x1": 360, "top": 100, "bottom": 110})
    words.append({"text": ":", "x0": 362, "x1": 365, "top": 100, "bottom": 110})
    words.append({"text": "HDFC0000123", "x0": 370, "x1": 450, "top": 100, "bottom": 110})
    
    # Branch
    words.append({"text": "Branch", "x0": 20, "x1": 60, "top": 120, "bottom": 130})
    words.append({"text": ":", "x0": 62, "x1": 65, "top": 120, "bottom": 130})
    words.append({"text": "KORAMANGALA", "x0": 70, "x1": 150, "top": 120, "bottom": 130})
    
    # Opening balance text
    words.append({"text": "Opening", "x0": 20, "x1": 70, "top": 150, "bottom": 160})
    words.append({"text": "Balance", "x0": 75, "x1": 120, "top": 150, "bottom": 160})
    words.append({"text": ":", "x0": 122, "x1": 125, "top": 150, "bottom": 160})
    words.append({"text": "10,000.00", "x0": 130, "x1": 180, "top": 150, "bottom": 160})
    
    # Transaction Headers (Standard coordinates)
    # Col Date: ~30, Narration: ~150, Chq/Ref: ~300, Value Date: ~360, Withdrawal: ~430, Deposit: ~500, Balance: ~570
    headers = [
        ("Date", 30),
        ("Narration", 150),
        ("Chq/Ref No.", 300),
        ("Value Date", 360),
        ("Withdrawal Amt.", 430),
        ("Deposit Amt.", 500),
        ("Closing Balance", 570)
    ]
    for h_txt, x in headers:
        words.append({"text": h_txt, "x0": x - 20, "x1": x + 20, "top": 200, "bottom": 210})
        
    # Transaction 1: 01/04/24 - Salary credit
    tx1 = [
        ("01/04/24", 30),
        ("SALARY", 120), ("CREDIT", 160),
        ("REF001", 300),
        ("01/04/24", 360),
        # Deposit
        ("50,000.00", 500),
        ("60,000.00", 570)
    ]
    for txt, x in tx1:
        words.append({"text": txt, "x0": x - 15, "x1": x + 15, "top": 230, "bottom": 240})
        
    # Transaction 2: 05/04/24 - Zomato debit (multiline!)
    # Line 1
    tx2_l1 = [
        ("05/04/24", 30),
        ("UPI-ZOMATO-ZOMATO443@OKSBI", 120),
        ("REF002", 300),
        ("05/04/24", 360),
        # Withdrawal
        ("450.00", 430),
        ("59,550.00", 570)
    ]
    for txt, x in tx2_l1:
        words.append({"text": txt, "x0": x - 15, "x1": x + 15, "top": 260, "bottom": 270})
        
    # Line 2 (Narration continuation only)
    tx2_l2 = [
        ("ZOMATO FOOD DELIVERY", 120)
    ]
    for txt, x in tx2_l2:
        words.append({"text": txt, "x0": x - 15, "x1": x + 15, "top": 275, "bottom": 285})
        
    # Transaction 3: 10/04/24 - HDFC Loan EMI debit
    tx3 = [
        ("10/04/24", 30),
        ("HDFC LOAN EMI DR", 120),
        ("REF003", 300),
        ("10/04/24", 360),
        # Withdrawal
        ("15,000.00", 430),
        ("44,550.00", 570)
    ]
    for txt, x in tx3:
        words.append({"text": txt, "x0": x - 15, "x1": x + 15, "top": 300, "bottom": 310})
        
    return words

def test_parsing():
    print("Initializing Synthetic HDFC Statement Parser Test...")
    
    # Mocking pdfplumber
    mock_pdf = MagicMock()
    mock_page = MagicMock()
    
    # Mock page text for metadata extraction
    mock_text = """
    STATEMENT OF ACCOUNT FOR THE PERIOD FROM 01-APR-2024 TO 30-APR-2024
    Account No : 50100098765432
    IFSC Code : HDFC0000123
    Branch : KORAMANGALA Branch
    JOHN DOE
    Opening Balance : 10,000.00
    Closing Balance : 44,550.00
    """
    
    mock_page.extract_text.return_value = mock_text
    mock_page.extract_words.return_value = get_mock_words()
    mock_pdf.pages = [mock_page]
    mock_pdf.__enter__.return_value = mock_pdf
    
    with patch("pdfplumber.open", return_value=mock_pdf):
        parser = HDFCPDFParser("dummy_hdfc.pdf")
        metadata, transactions = parser.parse()
        
        # Categorize
        transactions = run_categorization(transactions)
        analytics = compute_analytics(transactions)
        
        # Assert metadata
        print("\n--- METADATA ---")
        print(f"Holder: {metadata['account_holder']} (Expected: JOHN DOE)")
        print(f"A/c Number: {metadata['account_number']} (Expected: 50100098765432)")
        print(f"IFSC Code: {metadata['ifsc']} (Expected: HDFC0000123)")
        print(f"Branch: {metadata['branch']} (Expected: KORAMANGALA Branch)")
        print(f"Opening Balance: {metadata['opening_balance']} (Expected: 10000.0)")
        print(f"Closing Balance: {metadata['closing_balance']} (Expected: 44550.0)")
        
        assert metadata["account_holder"] == "JOHN DOE"
        assert metadata["account_number"] == "50100098765432"
        assert metadata["ifsc"] == "HDFC0000123"
        assert metadata["opening_balance"] == 10000.0
        assert metadata["closing_balance"] == 44550.0
        
        # Assert transactions
        print("\n--- TRANSACTIONS ---")
        for idx, tx in enumerate(transactions):
            print(f"Tx {idx+1}: {tx['date']} | {tx['description']} | Ref: {tx['ref_no']} | DR: {tx['debit']} | CR: {tx['credit']} | Bal: {tx['balance']} | Cat: {tx['category']}")
            
        assert len(transactions) == 3
        # Tx 1: Salary credit
        assert transactions[0]["credit"] == 50000.0
        assert transactions[0]["category"] == "Salary"
        
        # Tx 2: Zomato debit (multiline narration check!)
        assert transactions[1]["debit"] == 450.0
        assert "ZOMATO FOOD DELIVERY" in transactions[1]["description"]
        assert transactions[1]["category"] == "Food & Dining"
        
        # Tx 3: EMI debit
        assert transactions[2]["debit"] == 15000.0
        assert transactions[2]["category"] == "EMI / Loan"
        
        # Balance chain check
        # Opening (10000) + Tx1 credit (50000) = 60000
        # 60000 - Tx2 debit (450) = 59550
        # 59550 - Tx3 debit (15000) = 44550
        assert transactions[0]["balance"] == 60000.0
        assert transactions[1]["balance"] == 59550.0
        assert transactions[2]["balance"] == 44550.0
        
        print("\n--- ANALYTICS ---")
        print(f"Categorized Rate: {analytics['percentage_categorized']}% (Expected: 100.0%)")
        print(f"Monthly Flow: {analytics['monthly_flow']}")
        assert analytics["percentage_categorized"] == 100.0
        
        print("\nSUCCESS: All parser integration tests passed!")

if __name__ == "__main__":
    test_parsing()
