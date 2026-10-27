"""
Textora AI - FastAPI Application Server
Provides REST endpoints for text analysis, multi-format document extraction,
audit history management, and report generation.
"""
import io
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Response, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.config import (
    APP_NAME, APP_VERSION, APP_SUBTITLE,
    MAX_FILE_SIZE_BYTES, ALLOWED_EXTENSIONS
)
from app.database import (
    init_db, save_audit, list_audits, get_audit, delete_audit, clear_all_audits
)
from app.extractor.text_extractor import extract_document
from app.engine.analyzer import analyze_text
from app.reports.pdf_generator import generate_pdf_report
from app.reports.export_helpers import export_json, export_html

# Initialize DB schema
init_db()

app = FastAPI(
    title=APP_NAME,
    description=APP_SUBTITLE,
    version=APP_VERSION
)

# Mount static assets
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

class AnalyzeRequest(BaseModel):
    text: str
    sensitivity: Optional[str] = "balanced"
    provider: Optional[str] = "heuristic"
    document_name: Optional[str] = "Pasted Text"
    save_history: Optional[bool] = True

class ExportRequest(BaseModel):
    results: Dict[str, Any]
    document_name: Optional[str] = "Audit_Report"

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        return HTMLResponse("<h1>Textora AI is starting up...</h1>", status_code=200)
    return HTMLResponse(index_file.read_text(encoding="utf-8"))

@app.get("/api/health")
async def health_check():
    return {
        "status": "online",
        "app": APP_NAME,
        "version": APP_VERSION,
        "supported_formats": list(ALLOWED_EXTENSIONS)
    }

@app.post("/api/analyze")
async def analyze_endpoint(payload: AnalyzeRequest):
    if not payload.text or not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
        
    res = analyze_text(
        text=payload.text,
        sensitivity=payload.sensitivity or "balanced",
        custom_provider=payload.provider
    )
    
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "Analysis failed."))
        
    audit_id = None
    if payload.save_history:
        audit_id = save_audit(
            document_name=payload.document_name or "Pasted Text",
            file_type="text",
            results=res
        )
        res["audit_id"] = audit_id
        
    return res

@app.post("/api/extract")
async def extract_file_endpoint(file: UploadFile = File(...)):
    filename = file.filename or "uploaded_document"
    ext = Path(filename).suffix.lower()
    
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )
        
    content = await file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum allowed size of 25MB (Current: {round(len(content) / (1024*1024), 2)}MB)"
        )
        
    extraction_res = extract_document(content, filename)
    if not extraction_res.get("success"):
        raise HTTPException(status_code=422, detail=extraction_res.get("error", "Failed to extract text."))
        
    return extraction_res

@app.post("/api/analyze-file")
async def analyze_file_endpoint(
    file: UploadFile = File(...),
    sensitivity: str = Form("balanced"),
    provider: str = Form("heuristic"),
    save_history: bool = Form(True)
):
    filename = file.filename or "uploaded_document"
    ext = Path(filename).suffix.lower()
    
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )
        
    content = await file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds 25MB limit.")
        
    extraction = extract_document(content, filename)
    if not extraction.get("success"):
        raise HTTPException(status_code=422, detail=extraction.get("error", "Extraction failed."))
        
    full_text = extraction.get("full_text", "").strip()
    if not full_text:
        notice = extraction.get("notice")
        if extraction.get("is_scanned"):
            raise HTTPException(
                status_code=422,
                detail=notice or "Scanned or empty document detected. OCR is required to extract text from images."
            )
        raise HTTPException(status_code=422, detail="No readable text found in document.")
        
    analysis = analyze_text(
        text=full_text,
        sensitivity=sensitivity,
        custom_provider=provider
    )
    
    if not analysis.get("success"):
        raise HTTPException(status_code=400, detail=analysis.get("error", "Analysis failed."))
        
    # Attach document structure to results
    analysis["document"] = {
        "filename": filename,
        "file_type": ext.replace(".", ""),
        "sections": extraction.get("sections", []),
        "is_scanned": extraction.get("is_scanned", False),
        "page_count": extraction.get("page_count"),
        "slide_count": extraction.get("slide_count")
    }
    
    audit_id = None
    if save_history:
        audit_id = save_audit(
            document_name=filename,
            file_type=ext.replace(".", ""),
            results=analysis
        )
        analysis["audit_id"] = audit_id
        
    return analysis

@app.get("/api/history")
async def get_history(
    search: str = Query("", description="Search document name or summary"),
    file_type: str = Query("", description="Filter by file type"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    audits = list_audits(search=search, file_type=file_type, limit=limit, offset=offset)
    return {"audits": audits, "count": len(audits)}

@app.get("/api/history/{audit_id}")
async def get_history_item(audit_id: str):
    audit = get_audit(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit record not found.")
    return audit

@app.delete("/api/history/{audit_id}")
async def delete_history_item(audit_id: str):
    success = delete_audit(audit_id)
    if not success:
        raise HTTPException(status_code=404, detail="Audit record not found.")
    return {"success": True, "message": "Record deleted."}

@app.delete("/api/history")
async def clear_history():
    deleted_count = clear_all_audits()
    return {"success": True, "deleted_count": deleted_count}

@app.post("/api/export/pdf")
async def export_pdf_endpoint(payload: ExportRequest):
    pdf_bytes = generate_pdf_report(
        results=payload.results,
        document_name=payload.document_name or "Textora_Audit"
    )
    
    filename = f"{payload.document_name or 'Textora_Audit'}.pdf".replace(" ", "_")
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.post("/api/export/html")
async def export_html_endpoint(payload: ExportRequest):
    html_content = export_html(
        results=payload.results,
        document_name=payload.document_name or "Document"
    )
    return HTMLResponse(content=html_content)

@app.post("/api/export/json")
async def export_json_endpoint(payload: ExportRequest):
    json_str = export_json(payload.results)
    filename = f"{payload.document_name or 'Textora_Audit'}.json".replace(" ", "_")
    return Response(
        content=json_str,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
