from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TransactionBase(BaseModel):
    date: str
    value_date: Optional[str] = None
    description: str
    ref_no: Optional[str] = None
    debit: Optional[float] = 0.0
    credit: Optional[float] = 0.0
    balance: float
    category: str

class Transaction(TransactionBase):
    id: int
    statement_id: int

    class Config:
        from_attributes = True

class StatementBase(BaseModel):
    filename: str
    account_holder: Optional[str] = None
    account_number: Optional[str] = None
    bank_name: str = "HDFC Bank"
    branch: Optional[str] = None
    ifsc: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    opening_balance: float = 0.0
    closing_balance: float = 0.0
    total_credits_count: int = 0
    total_credits_amount: float = 0.0
    total_debits_count: int = 0
    total_debits_amount: float = 0.0

class Statement(StatementBase):
    id: int
    uploaded_at: str

    class Config:
        from_attributes = True

class StatementDetail(BaseModel):
    statement: Statement
    transactions: List[Transaction]

class CategoryUpdate(BaseModel):
    category: str
