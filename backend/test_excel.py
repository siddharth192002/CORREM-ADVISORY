import sys
import os
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(__file__))

from app.parser import HDFCPDFParser
from app.classifier import run_categorization, compute_analytics
from app.excel_generator import create_excel_report
from test_parser import get_mock_words

def generate_test_excel():
    print("Generating test Excel report...")
    
    mock_pdf = MagicMock()
    mock_page = MagicMock()
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
        transactions = run_categorization(transactions)
        analytics = compute_analytics(transactions)
        
        # Generate Excel binary
        excel_bytes = create_excel_report(metadata, transactions, analytics)
        
        # Save to disk
        output_path = "test_output.xlsx"
        with open(output_path, "wb") as f:
            f.write(excel_bytes)
            
        print(f"Excel report written successfully to {os.path.abspath(output_path)}")
        assert os.path.exists(output_path)
        print("SUCCESS: Excel verification completed!")

if __name__ == "__main__":
    generate_test_excel()
