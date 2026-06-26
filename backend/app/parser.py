import re
import pdfplumber
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Compile regexes
DATE_REGEX = re.compile(r"^\d{2}/\d{2}/\d{2,4}$")
DATE_PATTERN = re.compile(r"\b\d{2}/\d{2}/\d{2,4}\b")
ACC_NUM_REGEX = re.compile(r"(?:A/C|A/c|Account|Acct)\s*(?:No\.?|Number)?\s*:?\s*(\d{10,16})", re.IGNORECASE)
IFSC_REGEX = re.compile(r"IFSC\s*(?:Code)?\s*:?\s*([A-Z]{4}0[A-Z0-9]{6})", re.IGNORECASE)
BRANCH_REGEX = re.compile(r"Branch\s*:\s*([A-Za-z0-9\s,.-]+?)(?=\s*Phone|\s*Fax|\s*Email|\s*Pin|\n|$)", re.IGNORECASE)
PERIOD_REGEX = re.compile(r"(?:STATEMENT\s*OF\s*ACCOUNT\s*FOR\s*THE\s*PERIOD\s*(?:FROM|OF)?|STATEMENT\s*PERIOD\s*:?)\s*([0-9a-zA-Z\s.-]+?)\s*TO\s*([0-9a-zA-Z\s.-]+)", re.IGNORECASE)

def parse_amount(text):
    if not text:
        return 0.0
    # Clean characters
    clean = re.sub(r"[^\d.-]", "", text.strip())
    if not clean:
        return 0.0
    try:
        return float(clean)
    except ValueError:
        return 0.0

def validate_date(date_str):
    if not date_str:
        return None
    for fmt in ("%d/%m/%y", "%d/%m/%Y"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return date_str

class HDFCPDFParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.metadata = {
            "filename": "",
            "account_holder": "",
            "account_number": "",
            "bank_name": "HDFC Bank",
            "branch": "",
            "ifsc": "",
            "start_date": "",
            "end_date": "",
            "opening_balance": 0.0,
            "closing_balance": 0.0,
            "total_credits_count": 0,
            "total_credits_amount": 0.0,
            "total_debits_count": 0,
            "total_debits_amount": 0.0,
        }
        self.transactions = []

    def parse(self):
        try:
            with pdfplumber.open(self.file_path) as pdf:
                if len(pdf.pages) == 0:
                    raise ValueError("The uploaded PDF has no pages.")
                
                # 1. Extract metadata from first page
                first_page = pdf.pages[0]
                text = first_page.extract_text() or ""
                self.extract_metadata_from_text(text)
                
                # If name couldn't be extracted, do a fallback scan
                if not self.metadata["account_holder"]:
                    self.extract_holder_name_fallback(text)
                
                # 2. Extract Transactions
                self.extract_transactions_from_pdf(pdf)
                
                # 3. Post-process: sort transactions and validate chain
                self.post_process_and_validate()
                
                return self.metadata, self.transactions
        except Exception as e:
            logger.error(f"Error parsing PDF: {str(e)}", exc_info=True)
            raise e

    def extract_metadata_from_text(self, text):
        lines = text.split("\n")
        
        # A/C Number
        acct_match = ACC_NUM_REGEX.search(text)
        if acct_match:
            self.metadata["account_number"] = acct_match.group(1).strip()
        else:
            # Fallback direct scan for HDFC 14-digit pattern
            raw_nums = re.findall(r"\b50\d{12}\b", text)
            if raw_nums:
                self.metadata["account_number"] = raw_nums[0]

        # IFSC Code
        ifsc_match = IFSC_REGEX.search(text)
        if ifsc_match:
            self.metadata["ifsc"] = ifsc_match.group(1).strip()
            
        # Branch Name
        branch_match = BRANCH_REGEX.search(text)
        if branch_match:
            self.metadata["branch"] = branch_match.group(1).strip()

        # Period
        period_match = PERIOD_REGEX.search(text)
        if period_match:
            self.metadata["start_date"] = period_match.group(1).strip()
            self.metadata["end_date"] = period_match.group(2).strip()
        else:
            # Look for two dates on the statement header lines
            dates = DATE_PATTERN.findall(text)
            if len(dates) >= 2:
                self.metadata["start_date"] = dates[0]
                self.metadata["end_date"] = dates[1]

        # Scan for balances and summaries in text
        # Opening Balance
        op_match = re.search(r"Opening\s*Balance\s*:?\s*([\d,.-]+)", text, re.IGNORECASE)
        if op_match:
            self.metadata["opening_balance"] = parse_amount(op_match.group(1))

        # Closing Balance
        cl_match = re.search(r"Closing\s*Balance\s*:?\s*([\d,.-]+)", text, re.IGNORECASE)
        if cl_match:
            self.metadata["closing_balance"] = parse_amount(cl_match.group(1))

    def extract_holder_name_fallback(self, text):
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        
        # HDFC Bank statements typically have Account Holder Name in the first 10 lines
        # on the left hand side. Let's find name near address info.
        # We can exclude lines containing bank details, A/C number, dates etc.
        exclude_keywords = [
            "hdfc", "statement of account", "period", "a/c", "account", "ifsc", 
            "branch", "rtgs", "neft", "nomination", "page", "date", "customer care"
        ]
        
        potential_names = []
        for line in lines[:10]:
            if any(kw in line.lower() for kw in exclude_keywords):
                continue
            # Names usually start with capital letters and contain letters and spaces only
            if re.match(r"^[A-Z][A-Z\s.]+$", line):
                potential_names.append(line)
            elif re.match(r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+$", line):
                potential_names.append(line)
                
        if potential_names:
            self.metadata["account_holder"] = potential_names[0]
        else:
            self.metadata["account_holder"] = "Valued Customer"

    def is_noise_line(self, line_str):
        line_lower = line_str.lower()
        noise_keywords = [
            "page no", "hdfc bank", "statement of account", "registered office",
            "depository", "cust care", "customer care", "opening balance",
            "closing balance", "statement period", "value date", "withdrawal amt",
            "deposit amt", "running balance", "cheque/ref", "particulars",
            "narration", "chq/ref", "withdrawals (dr)", "deposits (cr)",
            "statement summary", "total credits", "total debits", "statement of a/c"
        ]
        for kw in noise_keywords:
            if kw in line_lower:
                return True
        # If the line contains only dashed lines or equals signs or stars
        if re.match(r"^[-\s*=_]+$", line_str):
            return True
        return False

    def extract_transactions_from_pdf(self, pdf):
        # Default layout bounds in points (A4 width = ~595)
        # We will determine these boundaries dynamically on a page if headers are found,
        # otherwise we fallback to these standard bounds.
        default_bounds = {
            "date": (0, 65),
            "narration": (65, 260),
            "chq_ref": (260, 335),
            "value_date": (335, 395),
            "withdrawal": (395, 465),
            "deposit": (465, 530),
            "balance": (530, 610)
        }
        
        current_bounds = default_bounds.copy()
        
        for page_idx, page in enumerate(pdf.pages):
            words = page.extract_words()
            if not words:
                continue
                
            # Group words into lines
            lines_words = {}
            for w in words:
                # Group by rounded top coordinate
                top_rounded = round(w["top"], 1)
                found = False
                for t in lines_words:
                    if abs(t - w["top"]) <= 3:
                        lines_words[t].append(w)
                        found = True
                        break
                if not found:
                    lines_words[w["top"]] = [w]
            
            # Sort lines top-to-bottom, and words in lines left-to-right
            sorted_lines = []
            for t in sorted(lines_words.keys()):
                sorted_line_words = sorted(lines_words[t], key=lambda w: w["x0"])
                sorted_lines.append(sorted_line_words)
                
            # Look for headers to update bounds dynamically
            header_detected = False
            for line_words in sorted_lines:
                line_str = " ".join([w["text"] for w in line_words]).lower()
                if "date" in line_str and ("narration" in line_str or "particulars" in line_str or "description" in line_str) and "balance" in line_str:
                    # We found a header row! Calculate new boundaries
                    headers = {
                        "date": None,
                        "narration": None,
                        "chq_ref": None,
                        "value_date": None,
                        "withdrawal": None,
                        "deposit": None,
                        "balance": None
                    }
                    
                    for w in line_words:
                        txt = w["text"].lower()
                        if "date" in txt and not headers["date"]:
                            headers["date"] = w
                        elif ("narration" in txt or "particulars" in txt or "description" in txt) and not headers["narration"]:
                            headers["narration"] = w
                        elif ("chq" in txt or "ref" in txt) and not headers["chq_ref"]:
                            headers["chq_ref"] = w
                        elif "value" in txt and not headers["value_date"]:
                            headers["value_date"] = w
                        elif ("withdrawal" in txt or "debit" in txt) and not headers["withdrawal"]:
                            headers["withdrawal"] = w
                        elif ("deposit" in txt or "credit" in txt) and not headers["deposit"]:
                            headers["deposit"] = w
                        elif "balance" in txt and not headers["balance"]:
                            headers["balance"] = w
                            
                    # Fill missing headers with approximations based on nearby ones
                    # Calculate splitting coordinates (midpoints between centers)
                    centers = {}
                    for col, w in headers.items():
                        if w:
                            centers[col] = (w["x0"] + w["x1"]) / 2.0
                            
                    # Set bounds based on sorted centers
                    sorted_cols = sorted(centers.items(), key=lambda x: x[1])
                    for i in range(len(sorted_cols) - 1):
                        col_name = sorted_cols[i][0]
                        next_col_name = sorted_cols[i+1][0]
                        midpoint = (sorted_cols[i][1] + sorted_cols[i+1][1]) / 2.0
                        
                        # Set boundaries
                        if i == 0:
                            current_bounds[col_name] = (0, midpoint)
                        else:
                            current_bounds[col_name] = (current_bounds[col_name][0], midpoint)
                        current_bounds[next_col_name] = (midpoint, 999) # Temp end
                        
                    # Set closing boundary for last column
                    last_col = sorted_cols[-1][0]
                    current_bounds[last_col] = (current_bounds[last_col][0], 999)
                    header_detected = True
                    break
                    
            # Parse lines using current boundaries
            for line_words in sorted_lines:
                line_str = " ".join([w["text"] for w in line_words]).strip()
                if not line_str:
                    continue
                    
                # Skip noise lines (page headers/footers/sub-headers/dashed lines)
                if self.is_noise_line(line_str):
                    continue
                    
                # Assign words to columns
                row_cols = {
                    "date": [], "narration": [], "chq_ref": [], 
                    "value_date": [], "withdrawal": [], "deposit": [], "balance": []
                }
                
                for w in line_words:
                    mid_x = (w["x0"] + w["x1"]) / 2.0
                    assigned = False
                    for col_name, (x_start, x_end) in current_bounds.items():
                        if x_start <= mid_x < x_end:
                            row_cols[col_name].append(w["text"])
                            assigned = True
                            break
                    if not assigned:
                        # Append to closest column
                        if mid_x >= 600:
                            row_cols["balance"].append(w["text"])
                        else:
                            row_cols["narration"].append(w["text"])
                            
                row_data = {k: " ".join(v).strip() for k, v in row_cols.items()}
                
                # Check if this row is a new transaction (Date column starts with DD/MM/YY or DD/MM/YYYY)
                date_val = row_data["date"]
                if date_val and DATE_REGEX.match(date_val):
                    # Validate transaction entries (must have running balance to be valid)
                    bal_val = parse_amount(row_data["balance"])
                    
                    self.transactions.append({
                        "date": validate_date(date_val),
                        "value_date": validate_date(row_data["value_date"]) or validate_date(date_val),
                        "description": row_data["narration"],
                        "ref_no": row_data["chq_ref"],
                        "debit": parse_amount(row_data["withdrawal"]),
                        "credit": parse_amount(row_data["deposit"]),
                        "balance": bal_val,
                        "category": "Other" # Classified later
                    })
                else:
                    # This is likely a continuation line
                    # Append description to the active transaction if we have one
                    if self.transactions and row_data["narration"]:
                        # Avoid duplicating numbers if it's picking up stray characters
                        self.transactions[-1]["description"] += " " + row_data["narration"]
                        
                        # In case the table is slightly misaligned and values were parsed here
                        if row_data["chq_ref"] and not self.transactions[-1]["ref_no"]:
                            self.transactions[-1]["ref_no"] = row_data["chq_ref"]
                        if row_data["withdrawal"] and self.transactions[-1]["debit"] == 0.0:
                            self.transactions[-1]["debit"] = parse_amount(row_data["withdrawal"])
                        if row_data["deposit"] and self.transactions[-1]["credit"] == 0.0:
                            self.transactions[-1]["credit"] = parse_amount(row_data["deposit"])
                        if row_data["balance"] and self.transactions[-1]["balance"] == 0.0:
                            self.transactions[-1]["balance"] = parse_amount(row_data["balance"])



    def post_process_and_validate(self):
        # 1. Clean transactions: remove any lines that were parsed as transactions but are empty / noise
        # (e.g. date exists but withdrawals, deposits, and balance are all 0)
        self.transactions = [
            tx for tx in self.transactions 
            if tx["debit"] != 0.0 or tx["credit"] != 0.0 or tx["balance"] != 0.0
        ]
        

            
        if not self.transactions:
            return
            
        # 2. Sort chronologically (stable sort)
        # HDFC statements are chronological, so we keep order or sort by date. 
        # Keeping PDF order is usually safest because multiple transactions on same day keep their balance chain order.
        
        # 3. Setup of Opening Balance if missing
        if self.metadata["opening_balance"] == 0.0 and self.transactions:
            first_tx = self.transactions[0]
            self.metadata["opening_balance"] = round(first_tx["balance"] - first_tx["credit"] + first_tx["debit"], 2)
            
        # 4. Validate Balance Chain
        prev_bal = self.metadata["opening_balance"]
        valid_chain = True
        
        for idx, tx in enumerate(self.transactions):
            expected_bal = round(prev_bal - tx["debit"] + tx["credit"], 2)
            if abs(tx["balance"] - expected_bal) > 0.05: # Float tolerance
                logger.warning(f"Balance mismatch at row {idx+1}: Description: {tx['description']}. Expected {expected_bal}, Got {tx['balance']}")
                if abs(tx["balance"] - expected_bal) < 0.2:
                    tx["balance"] = expected_bal
                else:
                    valid_chain = False
            prev_bal = tx["balance"]
            
        # 5. Populate metadata summary metrics from calculated transactions
        credits = [tx["credit"] for tx in self.transactions if tx["credit"] > 0]
        debits = [tx["debit"] for tx in self.transactions if tx["debit"] > 0]
        
        self.metadata["total_credits_count"] = len(credits)
        self.metadata["total_credits_amount"] = round(sum(credits), 2)
        self.metadata["total_debits_count"] = len(debits)
        self.metadata["total_debits_amount"] = round(sum(debits), 2)
        
        if self.transactions:
            self.metadata["closing_balance"] = self.transactions[-1]["balance"]
            if not self.metadata["start_date"]:
                self.metadata["start_date"] = self.transactions[0]["date"]
            if not self.metadata["end_date"]:
                self.metadata["end_date"] = self.transactions[-1]["date"]
                
        # Format the start/end dates for output consistency
        self.metadata["start_date"] = self.format_date_standard(self.metadata["start_date"])
        self.metadata["end_date"] = self.format_date_standard(self.metadata["end_date"])

    def format_date_standard(self, date_str):
        if not date_str:
            return ""
        for fmt in ("%d-%b-%y", "%d-%b-%Y", "%d/%m/%y", "%d/%m/%Y", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                try:
                    dt = datetime.strptime(date_str.upper(), fmt)
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue
        return date_str
