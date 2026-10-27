"""
Textora AI - PDF Document Extractor
Extracts page-by-page text from PDF documents using pypdf.
Detects scanned / empty image-based PDFs and alerts user accordingly.
"""
import io
from typing import Dict, Any, List
from pypdf import PdfReader

def extract_pdf(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        num_pages = len(reader.pages)
        
        if num_pages == 0:
            return {
                "success": False,
                "error": "The PDF file contains no pages.",
                "sections": [],
                "full_text": "",
                "page_count": 0,
                "is_scanned": False
            }
            
        sections: List[Dict[str, Any]] = []
        full_text_parts: List[str] = []
        total_extracted_chars = 0
        
        for idx, page in enumerate(reader.pages):
            page_num = idx + 1
            page_text = page.extract_text() or ""
            cleaned_text = page_text.strip()
            total_extracted_chars += len(cleaned_text)
            
            words = len(cleaned_text.split()) if cleaned_text else 0
            
            sections.append({
                "section_id": f"page_{page_num}",
                "title": f"Page {page_num}",
                "page_number": page_num,
                "text": cleaned_text,
                "word_count": words,
                "char_count": len(cleaned_text),
                "is_empty": len(cleaned_text) == 0
            })
            
            if cleaned_text:
                full_text_parts.append(f"--- Page {page_num} ---\n{cleaned_text}")
                
        # Scanned document detection check
        # If there are pages but very few characters extracted per page on average
        is_scanned = (total_extracted_chars < 30 * num_pages) and (num_pages > 0)
        
        full_text = "\n\n".join(full_text_parts).strip()
        
        message = ""
        if is_scanned:
            message = (
                "Notice: Very little or no embedded text was detected. "
                "This PDF appears to be a scanned image or rasterized document. "
                "Optical Character Recognition (OCR) is required to parse image-only PDFs."
            )
            
        return {
            "success": True,
            "filename": filename,
            "file_type": "pdf",
            "page_count": num_pages,
            "total_words": len(full_text.split()) if full_text else 0,
            "total_chars": len(full_text),
            "is_scanned": is_scanned,
            "notice": message,
            "sections": sections,
            "full_text": full_text
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to parse PDF: {str(e)}",
            "sections": [],
            "full_text": "",
            "page_count": 0,
            "is_scanned": False
        }
