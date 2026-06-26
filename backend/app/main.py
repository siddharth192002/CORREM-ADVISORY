import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from app.database import (
    init_db, save_statement, get_statements, get_statement_by_id,
    update_transaction_category, delete_statement
)
from app.parser import HDFCPDFParser
from app.classifier import run_categorization, compute_analytics
from app.excel_generator import create_excel_report
from app import schemas

app = FastAPI(title="Bank Statement Analyzer API")

# Configure CORS for local development and live URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, lock this down or configure as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()

@app.post("/api/upload", response_model=schemas.Statement)
async def upload_statement(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only HDFC Bank statement PDF files are accepted.")
        
    # Save uploaded file to a temporary file
    temp_dir = tempfile.mkdtemp()
    temp_file_path = os.path.join(temp_dir, file.filename)
    
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Parse PDF
        parser = HDFCPDFParser(temp_file_path)
        metadata, transactions = parser.parse()
        metadata["filename"] = file.filename
        
        if not transactions:
            raise HTTPException(
                status_code=422, 
                detail="Unable to extract any transaction records. Ensure the file is a valid HDFC Bank statement PDF."
            )
            
        # Run categorization
        transactions = run_categorization(transactions)
        
        # Save to DB
        statement_id = save_statement(metadata, transactions)
        
        # Retrieve full statement details to return
        db_details = get_statement_by_id(statement_id)
        if not db_details:
            raise HTTPException(status_code=500, detail="Error retrieving statement after saving.")
            
        return db_details["statement"]
        
    except Exception as e:
        # Log error in backend
        import logging
        logging.getLogger(__name__).error(f"Upload error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process statement: {str(e)}")
    finally:
        # Clean up temp files
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass

@app.get("/api/statements", response_model=List[schemas.Statement])
def list_statements():
    return get_statements()

@app.get("/api/statements/{statement_id}")
def get_statement_detail(statement_id: int):
    details = get_statement_by_id(statement_id)
    if not details:
        raise HTTPException(status_code=404, detail="Statement not found.")
        
    # Re-run analytics dynamically based on current categories
    analytics = compute_analytics(details["transactions"])
    
    return {
        "statement": details["statement"],
        "transactions": details["transactions"],
        "analytics": analytics
    }

@app.put("/api/transactions/{transaction_id}/category")
def update_category(transaction_id: int, payload: schemas.CategoryUpdate):
    statement_id = update_transaction_category(transaction_id, payload.category)
    if not statement_id:
        raise HTTPException(status_code=404, detail="Transaction not found.")
        
    # Fetch updated details and return fresh analytics
    details = get_statement_by_id(statement_id)
    analytics = compute_analytics(details["transactions"])
    
    return {
        "transactions": details["transactions"],
        "analytics": analytics
    }

@app.get("/api/statements/{statement_id}/export")
def export_statement(statement_id: int):
    details = get_statement_by_id(statement_id)
    if not details:
        raise HTTPException(status_code=404, detail="Statement not found.")
        
    # Compute final analytics
    analytics = compute_analytics(details["transactions"])
    
    # Generate Excel
    excel_data = create_excel_report(details["statement"], details["transactions"], analytics)
    
    # Format filename safely
    safe_filename = details["statement"]["filename"].replace(".pdf", "").replace(" ", "_")
    filename = f"{safe_filename}_analysis.xlsx"
    
    # Stream the file back
    return StreamingResponse(
        io_bytes_stream(excel_data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )

@app.delete("/api/statements/{statement_id}")
def delete_statement_endpoint(statement_id: int):
    success = delete_statement(statement_id)
    if not success:
        raise HTTPException(status_code=404, detail="Statement not found.")
    return {"message": "Statement deleted successfully."}

def io_bytes_stream(data: bytes):
    import io
    return io.BytesIO(data)
