# HDFC Bank Statement Analyzer

A premium, full-stack web application designed to parse official HDFC Bank PDF statements, validate balance chain integrity, categorize transactions using keyword rules, detect recurring monthly flows (Salaries & EMIs), and generate beautifully styled 3-sheet Excel reports alongside an interactive browser dashboard.

---

## 🛠️ Technology Stack

- **Frontend**: ReactJS, Vite, Tailwind CSS (v3), Recharts, Lucide Icons, Axios.
- **Backend**: Python 3.10+ (using Python 3.12 runtime), FastAPI, pdfplumber, openpyxl, pandas.
- **Database**: SQLite3 (persistent storage for statement metadata and transaction details).

---

## 🏗️ Architecture & Core Components

```
hello/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI endpoints, CORS, routers & startup hooks
│   │   ├── database.py        # SQLite schema creation and transaction queries
│   │   ├── parser.py          # PDF parser utilizing dynamic word/column boundaries
│   │   ├── classifier.py      # Keyword matching, Salary & EMI detection algorithms
│   │   ├── excel_generator.py # openpyxl styled Excel sheet generation
│   │   └── schemas.py         # Pydantic schemas for request/response validation
│   ├── requirements.txt       # Backend dependencies
│   ├── test_parser.py         # Mock integration parser test
│   └── test_excel.py          # Mock integration Excel builder test
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── FileUpload.jsx # Drag-and-drop file upload component
    │   │   ├── LedgerTable.jsx# Searchable, filterable transaction grid
    │   │   ├── Dashboard.jsx  # Main tabs visual report module
    │   │   └── ThemeToggle.jsx# Dark/light theme state manager
    │   ├── App.jsx            # Shell container orchestrator
    │   ├── index.css          # Global CSS, scrollbars & animations
    │   └── main.jsx           # Vite React mounting entry
    ├── package.json           # Frontend package specs
    ├── tailwind.config.js     # Tailwind setup
    └── postcss.config.js      # PostCSS config
```

### 1. Dynamic PDF Parsing Strategy (`parser.py`)
Rather than relying on brittle hardcoded coordinates, the parser reads all word coordinate bounding boxes on page headers dynamically:
1. It locates the table header containing `Date`, `Narration`, and `Balance`.
2. It calculates the center $x$-coordinates of each column header.
3. It sets boundary splitting points halfway between column centers.
4. For multiline transactions, it tracks date starts: any row not beginning with a valid date format is combined into the active transaction's description.
5. It runs a balance chain verification checks: `Balance_i = Balance_{i-1} + Credit_i - Debit_i`.

### 2. Priority Categorization (`classifier.py`)
Transactions are classified against a hierarchical set of keywords. Specific transaction tags (like `Salary` or `EMI / Loan`) are prioritized over general transaction forms (like `UPI / Transfer`) to ensure Swiggy payments made via UPI register as `Food & Dining` instead of a generic transfer.

### 3. Salary & EMI Pattern Detection (`classifier.py`)
- **Salary Detection**: Identifies credit transactions matching standard inflows (or amount values $\ge 10,000$ INR) that recur once per calendar month (grouped in $\pm 10\%$ amount clusters).
- **EMI/Loan Detection**: Groups debit transactions of identical amounts ($\pm 1.5\%$ tolerance) that recur monthly.

### 4. Styled 3-Sheet Excel Export (`excel_generator.py`)
- **Sheet 1 (Account Details)**: Card-based details layout showing holder, account, branch, opening/closing balance, and debit/credit sums.
- **Sheet 2 (Ledger)**: Tabular transaction journal featuring right-aligned currency cells, formatted date strings, zebra-striped rows, and categories.
- **Sheet 3 (Summary & Analytics)**: Category tables, monthly cash flow charts, top 5 largest transaction logs, salary/EMI details, and an embedded native Excel Pie Chart.

---

## ⚡ Setup & Run Instructions

Ensure Python 3.10+ and NodeJS are installed.

### 1. Backend Service Setup

```bash
cd backend

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Seed the database with a sample statement for immediate UI preview
python seed_data.py

# Start the FastAPI server
python -m uvicorn app.main:app --port 8000 --reload
```

The API docs will be available at `http://localhost:8000/docs`.

### 2. Frontend Dashboard Setup

```bash
cd frontend

# Install Node modules
npm install

# Run the Vite React developer server
npm run dev
```

Open `http://localhost:5173/` in your browser.

---

## 📝 Assumptions Made

- HDFC statements use standard Indian Currency formats (commas separating thousands and lakhs).
- The account numbers are standard HDFC 14-digit numeric values beginning with `50`.
- Scanned PDF files require external system binaries (`tesseract-ocr` and `poppler-utils`) to be pre-installed on the host system path for the backend OCR fallback to process image text.

---

## 🤖 AI Tools Disclosure

This application was built end-to-end in collaboration with **Antigravity**, an agentic AI coding assistant designed by Google DeepMind. Antigravity assisted with:
- Scaffolding the React frontend and FastAPI backend structures.
- Implementing the dynamic column splitter and multiline text parser.
- Designing the openpyxl spreadsheet formatting and charts.
- Setting up tailwind styles, micro-animations, and theme toggling.
- Running unit test validations and automated browser UI verifications.
