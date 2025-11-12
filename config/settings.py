import os
from pathlib import Path

# Path configurations
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MASTER_DB_PATH = DATA_DIR / "Entities.xlsx"

# Matching thresholds
EXACT_MATCH_THRESHOLD = 100
FUZZY_MATCH_THRESHOLD = 85
# HIGH_CONFIDENCE_THRESHOLD = 90

# Supported file types
SUPPORTED_FILE_TYPES = ["csv", "xlsx", "xls"]

# Column mappings
COLUMN_MAPPINGS = {
    "company_name": ["Entity Name", "Company Name", "Name", "entity_name"],
    "ticker": ["Ticker", "ticker", "Symbol"],
    "isin": ["ISIN", "isin"],
    "lei": ["LEI", "lei"],
    "entity_id": ["Entity ID", "Company ID", "entity_id"]
}