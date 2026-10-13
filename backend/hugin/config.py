from dataclasses import dataclass, field
from pathlib import Path
import os


@dataclass
class Settings:
    mode: str = field(default_factory=lambda: os.getenv('HUGIN_MODE', 'live'))
    mongo_url: str = field(default_factory=lambda: os.getenv('MONGO_URL', 'mongodb://127.0.0.1:27017'))
    db_name: str = field(default_factory=lambda: os.getenv('DB_NAME', 'hugin'))
    fixture_store: str = field(default_factory=lambda: os.getenv('HUGIN_FIXTURE_STORE', str(Path(__file__).parents[2] / '.data/fixture-store.json')))
    dex_key: str = field(default_factory=lambda: os.getenv('DEX_API_KEY', ''))
    dex_url: str = 'https://mcp.getdex.com/mcp'
    brave_key: str = field(default_factory=lambda: os.getenv('BRAVE_SEARCH_API_KEY', ''))
    source_hosts: tuple = field(default_factory=lambda: tuple(h.strip().lower() for h in os.getenv('HUGIN_SOURCE_HOSTS', '').split(',') if h.strip()))
    origins: tuple = field(default_factory=lambda: tuple(os.getenv('HUGIN_CORS_ORIGINS', 'http://127.0.0.1:3000,http://localhost:3000').split(',')))
    workers: int = 1
    maigret_python: str = field(default_factory=lambda: os.getenv('HUGIN_MAIGRET_PYTHON', '/workspace/.hugin-setup/maigret/bin/python'))
    linkedin_python: str = field(default_factory=lambda: os.getenv('HUGIN_LINKEDIN_PYTHON', '/workspace/.hugin-setup/linkedin/bin/python'))
    linkedin_chromium: str = field(default_factory=lambda: os.getenv('HUGIN_LINKEDIN_CHROMIUM', '/usr/bin/chromium'))
    linkedin_session_file: str = field(default_factory=lambda: os.getenv('HUGIN_LINKEDIN_SESSION_FILE', ''))
    api_anything_dir: str = field(default_factory=lambda: os.getenv('HUGIN_API_ANYTHING_DIR', '/workspace/.hugin-setup/api-anything/lib/node_modules/api-anything'))
    api_anything_node: str = field(default_factory=lambda: os.getenv('HUGIN_API_ANYTHING_NODE', 'node'))

    def __post_init__(self):
        if self.mode not in ('live', 'fixture'):
            raise ValueError('HUGIN_MODE must be live or fixture')
        for host in self.source_hosts:
            if any(c in host for c in '/:@*'):
                raise ValueError('HUGIN_SOURCE_HOSTS requires exact public hostnames')


class ConnectorError(Exception):
    """Safe status and message. Never include provider response bodies or credentials."""
    def __init__(self, outcome, message):
        self.outcome, self.message = outcome, message
        super().__init__(message)
