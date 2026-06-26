import sqlite3
import os
import json
from datetime import datetime

# On Vercel serverless, filesystem is read-only except /tmp
if os.environ.get("VERCEL"):
    DB_PATH = "/tmp/db.sqlite3"
else:
    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db.sqlite3")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create statements table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS statements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            account_holder TEXT,
            account_number TEXT,
            bank_name TEXT DEFAULT 'HDFC Bank',
            branch TEXT,
            ifsc TEXT,
            start_date TEXT,
            end_date TEXT,
            opening_balance REAL,
            closing_balance REAL,
            total_credits_count INTEGER,
            total_credits_amount REAL,
            total_debits_count INTEGER,
            total_debits_amount REAL,
            uploaded_at TEXT NOT NULL
        )
    """)
    
    # Create transactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            statement_id INTEGER,
            date TEXT NOT NULL,
            value_date TEXT,
            description TEXT NOT NULL,
            ref_no TEXT,
            debit REAL,
            credit REAL,
            balance REAL,
            category TEXT NOT NULL,
            FOREIGN KEY (statement_id) REFERENCES statements (id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()

def save_statement(statement_data, transactions_list):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Insert statement
        cursor.execute("""
            INSERT INTO statements (
                filename, account_holder, account_number, bank_name, branch, ifsc,
                start_date, end_date, opening_balance, closing_balance,
                total_credits_count, total_credits_amount, total_debits_count, total_debits_amount,
                uploaded_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            statement_data.get("filename"),
            statement_data.get("account_holder"),
            statement_data.get("account_number"),
            statement_data.get("bank_name", "HDFC Bank"),
            statement_data.get("branch"),
            statement_data.get("ifsc"),
            statement_data.get("start_date"),
            statement_data.get("end_date"),
            statement_data.get("opening_balance", 0.0),
            statement_data.get("closing_balance", 0.0),
            statement_data.get("total_credits_count", 0),
            statement_data.get("total_credits_amount", 0.0),
            statement_data.get("total_debits_count", 0),
            statement_data.get("total_debits_amount", 0.0),
            datetime.now().isoformat()
        ))
        
        statement_id = cursor.lastrowid
        
        # Insert transactions
        for tx in transactions_list:
            cursor.execute("""
                INSERT INTO transactions (
                    statement_id, date, value_date, description, ref_no, debit, credit, balance, category
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                statement_id,
                tx.get("date"),
                tx.get("value_date"),
                tx.get("description"),
                tx.get("ref_no"),
                tx.get("debit"),
                tx.get("credit"),
                tx.get("balance"),
                tx.get("category", "Other")
            ))
            
        conn.commit()
        return statement_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_statements():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM statements ORDER BY uploaded_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_statement_by_id(statement_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get statement
    cursor.execute("SELECT * FROM statements WHERE id = ?", (statement_id,))
    stmt_row = cursor.fetchone()
    if not stmt_row:
        conn.close()
        return None
        
    statement = dict(stmt_row)
    
    # Get transactions
    cursor.execute("SELECT * FROM transactions WHERE statement_id = ? ORDER BY id ASC", (statement_id,))
    tx_rows = cursor.fetchall()
    conn.close()
    
    transactions = [dict(tx) for tx in tx_rows]
    return {
        "statement": statement,
        "transactions": transactions
    }

def update_transaction_category(transaction_id, new_category):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE transactions SET category = ? WHERE id = ?
        """, (new_category, transaction_id))
        
        # We need to get statement_id to return updated analytics later
        cursor.execute("SELECT statement_id FROM transactions WHERE id = ?", (transaction_id,))
        row = cursor.fetchone()
        statement_id = row[0] if row else None
        
        conn.commit()
        return statement_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def delete_statement(statement_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM transactions WHERE statement_id = ?", (statement_id,))
        cursor.execute("DELETE FROM statements WHERE id = ?", (statement_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
