"""
Textora AI - SQLite Database Interface
Stores audit history locally with full querying, filtering, retrieval, and deletion.
"""
import sqlite3
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.config import DB_PATH

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audits (
            id TEXT PRIMARY KEY,
            document_name TEXT NOT NULL,
            file_type TEXT NOT NULL,
            created_at TEXT NOT NULL,
            word_count INTEGER NOT NULL,
            char_count INTEGER NOT NULL,
            sentence_count INTEGER NOT NULL,
            ai_score REAL NOT NULL,
            human_score REAL NOT NULL,
            mixed_score REAL NOT NULL,
            classification TEXT NOT NULL,
            confidence TEXT NOT NULL,
            summary_notes TEXT,
            results_json TEXT NOT NULL
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audits_created_at ON audits(created_at DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audits_file_type ON audits(file_type)")
    conn.commit()
    conn.close()

def save_audit(
    document_name: str,
    file_type: str,
    results: Dict[str, Any],
    audit_id: Optional[str] = None
) -> str:
    if not audit_id:
        audit_id = str(uuid.uuid4())
    
    created_at = datetime.utcnow().isoformat() + "Z"
    counts = results.get("statistics", {})
    scores = results.get("scores", {})
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO audits (
            id, document_name, file_type, created_at,
            word_count, char_count, sentence_count,
            ai_score, human_score, mixed_score,
            classification, confidence, summary_notes, results_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        audit_id,
        document_name,
        file_type.lower(),
        created_at,
        counts.get("word_count", 0),
        counts.get("char_count", 0),
        counts.get("sentence_count", 0),
        round(scores.get("ai_score", 0.0), 1),
        round(scores.get("human_score", 0.0), 1),
        round(scores.get("mixed_score", 0.0), 1),
        results.get("classification", "Inconclusive"),
        results.get("confidence", "Moderate"),
        results.get("summary", ""),
        json.dumps(results)
    ))
    conn.commit()
    conn.close()
    return audit_id

def list_audits(
    search: str = "",
    file_type: str = "",
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT id, document_name, file_type, created_at, word_count, char_count, sentence_count, ai_score, human_score, mixed_score, classification, confidence, summary_notes FROM audits WHERE 1=1"
    params: List[Any] = []
    
    if search:
        query += " AND (document_name LIKE ? OR summary_notes LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term])
        
    if file_type and file_type.lower() != "all":
        query += " AND file_type = ?"
        params.append(file_type.lower())
        
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def get_audit(audit_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audits WHERE id = ?", (audit_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    data = dict(row)
    data["results"] = json.loads(data["results_json"])
    del data["results_json"]
    return data

def delete_audit(audit_id: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM audits WHERE id = ?", (audit_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def clear_all_audits() -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM audits")
    count = cursor.rowcount
    conn.commit()
    conn.close()
    return count
