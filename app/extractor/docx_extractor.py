"""
Textora AI - DOCX Document Extractor
Extracts structured paragraphs, headings, and tables from Word DOCX files.
"""
import io
from typing import Dict, Any, List
import docx

def extract_docx(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        sections: List[Dict[str, Any]] = []
        current_section_title = "Document Introduction"
        current_section_paras: List[str] = []
        full_text_parts: List[str] = []
        
        section_idx = 1
        
        # Process paragraphs
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
                
            style_name = para.style.name.lower() if para.style else ""
            is_heading = "heading" in style_name or "title" in style_name
            
            if is_heading and current_section_paras:
                # Flush previous section
                sec_text = "\n\n".join(current_section_paras).strip()
                sections.append({
                    "section_id": f"section_{section_idx}",
                    "title": current_section_title,
                    "text": sec_text,
                    "word_count": len(sec_text.split()),
                    "char_count": len(sec_text),
                })
                section_idx += 1
                current_section_title = text
                current_section_paras = []
            elif is_heading:
                current_section_title = text
            else:
                current_section_paras.append(text)
                
            full_text_parts.append(text)
            
        # Process tables if any
        table_texts: List[str] = []
        for t_idx, table in enumerate(doc.tables):
            row_texts = []
            for row in table.rows:
                cell_vals = [c.text.strip() for c in row.cells if c.text.strip()]
                if cell_vals:
                    row_texts.append(" | ".join(cell_vals))
            if row_texts:
                t_content = "\n".join(row_texts)
                table_texts.append(f"[Table {t_idx + 1}]\n{t_content}")
                full_text_parts.append(t_content)
                
        if current_section_paras:
            sec_text = "\n\n".join(current_section_paras).strip()
            sections.append({
                "section_id": f"section_{section_idx}",
                "title": current_section_title,
                "text": sec_text,
                "word_count": len(sec_text.split()),
                "char_count": len(sec_text),
            })
            
        if table_texts:
            t_combined = "\n\n".join(table_texts)
            sections.append({
                "section_id": f"section_tables",
                "title": "Document Tables",
                "text": t_combined,
                "word_count": len(t_combined.split()),
                "char_count": len(t_combined),
            })
            
        full_text = "\n\n".join(full_text_parts).strip()
        
        # If no explicit headings, create a single clean section or split by paragraph blocks
        if not sections and full_text:
            sections.append({
                "section_id": "section_1",
                "title": "Full Content",
                "text": full_text,
                "word_count": len(full_text.split()),
                "char_count": len(full_text),
            })
            
        return {
            "success": True,
            "filename": filename,
            "file_type": "docx",
            "section_count": len(sections),
            "total_words": len(full_text.split()) if full_text else 0,
            "total_chars": len(full_text),
            "sections": sections,
            "full_text": full_text
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to parse DOCX: {str(e)}",
            "sections": [],
            "full_text": "",
            "section_count": 0
        }
