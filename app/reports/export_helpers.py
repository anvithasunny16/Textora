"""
Textora AI - Export Helpers
Utilities for exporting audit reports in JSON and standalone HTML formats.
"""
import json
from typing import Dict, Any

def export_json(results: Dict[str, Any]) -> str:
    return json.dumps(results, indent=2)

def export_html(results: Dict[str, Any], document_name: str = "Document") -> str:
    scores = results.get("scores", {})
    stats = results.get("statistics", {})
    metrics = results.get("metrics", {})
    burst = metrics.get("burstiness", {})
    read = metrics.get("readability", {})
    recs = results.get("recommendations", [])
    
    recs_html = "".join([
        f"<div class='rec-card'><strong>{r.get('title')}</strong> ({r.get('category')}): {r.get('description')}</div>"
        for r in recs
    ])
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Textora AI - Audit Report: {document_name}</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      line-height: 1.6;
      color: #102A2A;
      max-width: 800px;
      margin: 40px auto;
      padding: 0 20px;
      background: #FAFAFA;
    }}
    .header {{
      border-bottom: 2px solid #102A2A;
      padding-bottom: 15px;
      margin-bottom: 25px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .logo {{ font-size: 24px; font-weight: 800; color: #102A2A; }}
    .badge {{
      display: inline-block;
      padding: 6px 14px;
      border-radius: 6px;
      font-weight: 700;
      font-size: 14px;
      color: white;
      background: #183A38;
    }}
    .score-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 15px;
      margin: 25px 0;
    }}
    .score-card {{
      background: white;
      padding: 15px;
      border-radius: 8px;
      border: 1px solid #E2E8F0;
      text-align: center;
    }}
    .score-val {{ font-size: 28px; font-weight: 800; }}
    .metric-table {{
      width: 100%;
      border-collapse: collapse;
      margin: 20px 0;
      background: white;
    }}
    .metric-table th, .metric-table td {{
      border: 1px solid #E2E8F0;
      padding: 10px 14px;
      text-align: left;
    }}
    .metric-table th {{ background: #F5F3EB; }}
    .rec-card {{
      background: white;
      border-left: 4px solid #102A2A;
      padding: 12px 16px;
      margin-bottom: 10px;
      border-radius: 0 6px 6px 0;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    .disclaimer {{
      background: #F5F3EB;
      border: 1px solid #D4DCD9;
      border-radius: 6px;
      padding: 14px;
      font-size: 13px;
      color: #5A6E68;
      margin-top: 30px;
    }}
    @media print {{
      body {{ margin: 0; background: white; }}
      .no-print {{ display: none; }}
    }}
  </style>
</head>
<body>
  <div class="header">
    <div class="logo">TEXTORA AI AUDIT REPORT</div>
    <div class="badge">{results.get("classification", "Report")}</div>
  </div>
  
  <p><strong>Document:</strong> {document_name} | <strong>Words:</strong> {stats.get('word_count')} | <strong>Sentences:</strong> {stats.get('sentence_count')} | <strong>Date:</strong> {results.get('created_at', 'Recent')}</p>
  
  <div class="score-grid">
    <div class="score-card" style="border-top: 4px solid #E87979;">
      <div class="score-val" style="color: #D9534F;">{scores.get('ai_score')}%</div>
      <div>AI-Like Signal</div>
    </div>
    <div class="score-card" style="border-top: 4px solid #6EA300;">
      <div class="score-val" style="color: #6EA300;">{scores.get('human_score')}%</div>
      <div>Human-Like Signal</div>
    </div>
    <div class="score-card" style="border-top: 4px solid #102A2A;">
      <div class="score-val">{results.get('confidence')}</div>
      <div>Confidence Level</div>
    </div>
  </div>
  
  <h3>Analysis Summary</h3>
  <p>{results.get('summary')}</p>
  
  <h3>Linguistic Diagnostics</h3>
  <table class="metric-table">
    <tr><th>Indicator</th><th>Value</th><th>Interpretation</th></tr>
    <tr><td>Burstiness (CV)</td><td>{burst.get('coefficient_of_variation')}</td><td>{burst.get('burstiness_label')}</td></tr>
    <tr><td>Reading Grade</td><td>Grade {read.get('flesch_kincaid_grade')}</td><td>{read.get('flesch_reading_ease_label')}</td></tr>
    <tr><td>Formulaic Markers</td><td>{metrics.get('formulaic_patterns', {}).get('total_markers', 0)}</td><td>Density: {metrics.get('formulaic_patterns', {}).get('density_per_100_words', 0)} per 100 words</td></tr>
  </table>
  
  <h3>Recommendations</h3>
  {recs_html}
  
  <div class="disclaimer">
    <strong>Probabilistic Disclaimer:</strong> {results.get('disclaimer')}
  </div>
  
  <div style="margin-top: 25px; text-align: center;" class="no-print">
    <button onclick="window.print()" style="padding: 10px 20px; background: #102A2A; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold;">Print or Save as PDF</button>
  </div>
</body>
</html>"""
    return html
