# Textora AI — Intelligent Text Audit Platform

**Textora AI** is a professional, responsive, full-stack text auditing web application that evaluates written content to estimate whether it exhibits AI-like writing signals, human-like writing traits, or a collaborative mixture of both. 

Designed for educators, researchers, students, editors, and professional writers, Textora AI provides transparent, observable linguistic diagnostics rather than making unsubstantiated claims of certainty.

---

## 🎨 Design System & Palette

Textora AI features an editorial SaaS aesthetic with a **Midnight Teal + Warm Ivory + Electric Lime** palette:

| Token | Hex Code | Purpose |
| :--- | :--- | :--- |
| **Primary Background** | `#102A2A` | Deep Midnight Teal surface |
| **Secondary Background** | `#183A38` | Dark Forest Teal cards & elevation |
| **Main Accent** | `#C5F36A` | Electric Lime for key actions, metrics, and highlights |
| **Light Theme Surface** | `#F5F3EB` | Warm Ivory light background |
| **Main Text (Dark)** | `#F5F3EB` | High-contrast Warm Ivory text |
| **Secondary Text** | `#AABDB6` | Muted Sage for metadata and descriptions |
| **Borders & Dividers** | `#294845` | Structural borders and subtle dividers |
| **High-Risk / AI Signal**| `#E87979` | Muted Coral for formulaic pattern indicators |
| **Human Pattern Signal** | `#5CE1A6` | Emerald / Soft Green for organic human variety |
| **Mixed / Neutral** | `#E5C46A` | Amber for balanced or inconclusive text |

*Theme toggle in the header switches between Midnight Teal Dark Mode and Warm Ivory Light Mode.*

---

## 🚀 Key Features

### 1. Interactive Landing Page
- Headline: *"Know Your Text. Understand Its Signals."*
- **Live Interactive Sample Audit Preview**: 3 instant presets (*Synthetic Academic Essay*, *Authentic Human Memoir*, *Hybrid Editorial Draft*) with live score gauges and burstiness metrics.
- Feature overview cards covering multi-dimensional diagnostics, multi-format extraction, sentence-level analysis, and branded reports.
- **Probabilistic Assessment Disclaimer** highlighting false positives, false negatives, and ethical guidelines.

### 2. Auditor Workspace
- Large, responsive text editor with live metrics: Word count, Character count, Sentence count, and Estimated Reading Time.
- One-click sample text presets: *🤖 AI Sample*, *✍️ Human Sample*, *🔀 Hybrid Draft*, and *📚 Dense Academic Excerpt*.
- Paste from clipboard, clear all, and multi-step undo.
- **Multi-File Drag-and-Drop Zone**: Supports TXT, PDF, DOCX, and PPTX up to 25MB.
- Real-time extraction queue showing file size, format badge, extraction status, and direct inspector links.

### 3. Modular Linguistic Analysis Engine
Transparent multi-signal linguistic evaluation pipeline:
- **Sentence Burstiness & Pacing**: Sentence length standard deviation, mean length, and Coefficient of Variation ($CV = \sigma / \mu$). Low CV (<0.30) highlights synthetic uniformity; high CV (>0.50) reveals natural human cadence.
- **Lexical Diversity**: Type-Token Ratio (TTR), Root TTR (Guiraud's Index), Hapax Legomena ratio (words occurring once), and vocabulary entropy.
- **Formulaic LLM Tropes & Markers**: Scans 100+ known algorithmic patterns (e.g., *"delve into"*, *"serves as a testament"*, *"vibrant tapestry"*, *"pivotal role"*, *"in conclusion"*, *"not only... but also"*).
- **Phonetic & Readability Complexity**: Flesch Reading Ease, Flesch-Kincaid Grade Level, Gunning Fog Index, Coleman-Liau Index, and average syllables per word.
- **Sentence-Level Evaluation**: Every individual sentence is scored and assigned observable reasons.
- **Confidence Calibration**: Texts under 50 words are flagged with a low-confidence warning due to statistical sample constraints.

### 4. Results Dashboard
- Animated Dual Gauges: AI-Like Pattern Signal % and Human-Like Pattern Signal %.
- Verdict Badge: *Likely AI-Generated*, *Likely Human-Written*, *Mixed / Collaborative Content*, or *Inconclusive / Short Text*.
- **Interactive Sentence Stream**: Color-coded sentence passages (Coral for AI-leaning, Green for Human-leaning, Amber for Mixed).
- **Sentence Inspector Drawer**: Clicking any sentence opens its exact word count, syllables, AI likelihood score, and specific observable triggers.
- Filter pills: Filter stream by *All Sentences*, *AI-Leaning*, *Human-Leaning*, or *Mixed*.
- **4 Deep-Dive Metric Cards**:
  1. *Burstiness & Length Distribution* (Short, Medium, Long, Extended bars)
  2. *Lexical Diversity & Unique Vocabulary*
  3. *Formulaic Tropes Tag Cloud*
  4. *Readability Complexity & Grade Levels*
- Actionable Originality & Clarity Recommendations.

### 5. Dedicated Document Audit Workflow
- Document extraction for:
  - **PDF**: Page-by-page text extraction via `pypdf`, with automatic scanned document / OCR-required alerts.
  - **Word (DOCX)**: Paragraphs, Heading 1/2 sections, and embedded tables via `python-docx`.
  - **PowerPoint (PPTX)**: Slide titles, body text frames, slide tables, and presenter notes with slide numbers via `python-pptx`.
  - **Plain Text (TXT)**: Auto-detected UTF-8, UTF-16, Latin-1 encodings.
- Section / slide browser with live extracted text preview.
- Options to audit the whole document or individual sections/slides.

### 6. Audit History
- Full persistence using a local SQLite database (`data/textora.db`).
- Live search by document name, summary keywords, or classification.
- Filter by file format (Text, PDF, DOCX, PPTX).
- Re-open past audits in Results Dashboard.
- One-click PDF download directly from history.
- Individual deletion and "Clear All" with confirmation.

### 7. Official Branded PDF & HTML Exports
- Real PDF generation via `reportlab`:
  - Branded header banner and document metadata.
  - Executive scorecards (AI %, Human %, Verdict, Confidence).
  - Diagnostic metrics table (Burstiness, TTR, Readability, Markers).
  - Detected formulaic patterns summary.
  - Representative sentence breakdown table.
  - Writing improvement recommendations.
  - Prominent probabilistic disclaimer.
- Standalone HTML print view (`/api/export/html`) and raw JSON download (`/api/export/json`).

### 8. Settings & Help
- Analysis sensitivity selector (Conservative, Balanced, Sensitive).
- Configurable engine provider (Built-in Heuristics vs External API).
- Format and size limits documentation.
- Privacy & data governance statement (zero model training, ephemeral in-memory processing).
- Interactive FAQ accordion covering accuracy, burstiness, false positives, and scanned PDFs.

---

## 🛠️ Technology Stack

- **Backend Framework**: Python FastAPI + Uvicorn (ASGI)
- **Document Extractors**: `pypdf` (PDF), `python-docx` (Word), `python-pptx` (PowerPoint), `striprtf` (RTF)
- **Report Generation**: `reportlab`
- **Database**: SQLite3
- **Frontend**: HTML5, Vanilla CSS3 (Custom Variables), Modern Vanilla JavaScript (ES6 Modules)
- **Typography**: Google Fonts (*Plus Jakarta Sans* & *JetBrains Mono*)

---

## 💻 Local Installation & Running

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.13)
- pip

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the Application
Run the runner script:
```bash
python run.py
```
Or start via uvicorn directly:
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 4. Access the Platform
Open your browser and navigate to:
```
http://127.0.0.1:8000/
```

---

## 🧪 Running Validation Tests

Run the included backend test suite to verify the linguistic engine, document extractors, database CRUD, and PDF generation:

```bash
python tests/test_backend.py
```

Generate test documents (TXT, PDF, DOCX, PPTX) for upload testing:
```bash
python tests/generate_sample_files.py
```

---

## 🔒 Security & Privacy Notice

- **Ephemeral Processing**: Uploaded documents are parsed in memory / temporary storage and cleared immediately.
- **No Third-Party Transmission**: Content is processed locally on the server; nothing is sent to external services unless an external API key is explicitly configured in Settings.
- **No Model Training**: Submitted text is never retained for machine learning training.
- **Probabilistic Limitation**: AI detection is inherently probabilistic. Stylistic overlaps occur between human and synthetic writing. Findings should always be used as an informative writing aid, not as definitive proof of authorship.
