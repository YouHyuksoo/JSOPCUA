"""
Centralized Path Configuration

Provides absolute paths for all backend directories to prevent
path resolution issues.
"""

from pathlib import Path
import os

# Get the backend root directory (parent of src)
_CURRENT_FILE = Path(__file__).resolve()  # .../backend/src/config/paths.py
BACKEND_ROOT = _CURRENT_FILE.parent.parent.parent  # .../backend

# Core directories
SRC_DIR = BACKEND_ROOT / "src"
CONFIG_DIR = BACKEND_ROOT / "config"
LOGS_DIR = BACKEND_ROOT / "logs"
DATA_DIR = BACKEND_ROOT / "data"
BACKUP_DIR = BACKEND_ROOT / "backup"
SCRIPTS_DIR = BACKEND_ROOT / "scripts"
TESTS_DIR = BACKEND_ROOT / "tests"

# Database path
DATABASE_PATH = DATA_DIR / "scada.db"

# Ensure critical directories exist
def ensure_directories():
    """Create necessary directories if they don't exist"""
    for directory in [CONFIG_DIR, LOGS_DIR, DATA_DIR, BACKUP_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

# Auto-create directories on import
ensure_directories()

# Convert to strings for compatibility with legacy code
def get_backend_root() -> str:
    """Get backend root directory as string"""
    return str(BACKEND_ROOT)

def get_logs_dir() -> str:
    """Get logs directory as string"""
    return str(LOGS_DIR)

def get_config_dir() -> str:
    """Get config directory as string"""
    return str(CONFIG_DIR)

def get_data_dir() -> str:
    """Get data directory as string"""
    return str(DATA_DIR)

def get_backup_dir() -> str:
    """Get backup directory as string"""
    return str(BACKUP_DIR)

def get_database_path() -> str:
    """Get database file path as string"""
    return str(DATABASE_PATH)
