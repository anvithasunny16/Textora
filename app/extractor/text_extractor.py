"""
Textora AI - Document Extraction Dispatcher
Dispatches files to specific extractors based on extension and validates inputs.
"""
from pathlib import Path
from typing import Dict, Any
from app.extractor.pdf_extractor import extract_pdf
from app.extractor.docx_extractor import extract_docx
from app.extractor.pptx_extractor import extract_pptx

def extract_plain_text(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "utf-16"]
    text = None
    used_encoding = "utf-8"
    
    for enc in encodings:
        try:
            text = file_bytes.decode(enc)
            used_encoding = enc
            break
        except UnicodeDecodeError:
            continue
            
    if text is None:
        return {
            "success": False,
            "error": "Unable to decode text file with standard encodings.",
            "sections": [],
            "full_text": "",
            "file_type": "txt"
        }
        
    cleaned_text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    paragraphs = [p.strip() for p in cleaned_text.split("\n\n") if p.strip()]
    
    sections = []
    if len(paragraphs) > 1:
        for idx, p in enumerate(paragraphs):
            sections.append({
                "section_id": f"para_{idx + 1}",
                "title": f"Paragraph {idx + 1}",
                "text": p,
                "word_count": len(p.split()),
                "char_count": len(p)
            })
    else:
        sections.append({
            "section_id": "section_1",
            "title": "Full Document",
            "text": cleaned_text,
            "word_count": len(cleaned_text.split()),
            "char_count": len(cleaned_text)
        })
        
    return {
        "success": True,
        "filename": filename,
        "file_type": "txt",
        "encoding": used_encoding,
        "section_count": len(sections),
        "total_words": len(cleaned_text.split()) if cleaned_text else 0,
        "total_chars": len(cleaned_text),
        "sections": sections,
        "full_text": cleaned_text
    }

def extract_document(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    ext = Path(filename).suffix.lower()
    
    if ext == ".pdf":
        return extract_pdf(file_bytes, filename)
    elif ext == ".docx":
        return extract_docx(file_bytes, filename)
    elif ext == ".pptx":
        return extract_pptx(file_bytes, filename)
    elif ext in [".txt", ".text", ".md", ".rtf"]:
        return extract_plain_text(file_bytes, filename)
    else:
        return {
            "success": False,
            "error": f"Unsupported format '{ext}'. Supported formats: .txt, .pdf, .docx, .pptx",
            "sections": [],
            "full_text": "",
            "file_type": ext.replace(".", "")
        }
