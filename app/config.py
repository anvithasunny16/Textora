"""
Textora AI - Configuration
"""
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

TEMP_UPLOAD_DIR = DATA_DIR / "temp_uploads"
TEMP_UPLOAD_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "textora.db"

# Application metadata
APP_NAME = "Textora AI"
APP_SUBTITLE = "Intelligent Text Audit Platform"
APP_VERSION = "1.0.0"

# Limits & Supported Files
MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB
ALLOWED_EXTENSIONS = {".txt", ".pdf", ".docx", ".pptx"}

# Detection Engine Defaults
DEFAULT_SENSITIVITY = "balanced"  # 'conservative', 'balanced', 'sensitive'
EXTERNAL_API_KEY = os.getenv("TEXTORA_API_KEY", "")
EXTERNAL_API_URL = os.getenv("TEXTORA_API_URL", "")
EXTERNAL_PROVIDER = os.getenv("TEXTORA_PROVIDER", "heuristic")  # 'heuristic' or 'external'
