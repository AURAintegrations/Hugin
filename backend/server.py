"""Local-only application entry point. Keys are loaded server-side, never returned."""
from pathlib import Path
from dotenv import load_dotenv
from hugin.app import create_app

load_dotenv(Path(__file__).parent / '.env')
app = create_app()
