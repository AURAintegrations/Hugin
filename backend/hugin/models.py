from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, Field, model_validator, field_validator
from urllib.parse import urlparse
import hashlib
import json


def now():
    return datetime.now(timezone.utc).isoformat()


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


class EnrichRequest(BaseModel):
    dex_contact_id: str | None = Field(default=None, min_length=1, max_length=200)
    query: str | None = Field(default=None, min_length=1, max_length=200)
    idempotency_key: str | None = Field(default=None, min_length=1, max_length=200)
    dry_run: bool = False
    write_policy: Literal['notes_only', 'fill_missing'] = 'notes_only'
    sources: list[Literal['dex_cached', 'company_web', 'api_anything', 'public_pages', 'public_discovery', 'maigret', 'linkedin', 'brave', 'dex_fresh']] = Field(default_factory=lambda: ['dex_cached', 'company_web', 'api_anything', 'linkedin', 'public_discovery', 'maigret', 'public_pages'], max_length=9)
    company_urls: list[str] = Field(default_factory=list, max_length=3)
    linkedin_html: str | None = Field(default=None, max_length=1_000_000, repr=False)
    max_pages: int = Field(default=5, ge=1, le=10)
    max_requests: int = Field(default=18, ge=1, le=25)
    timeout_seconds: int = Field(default=90, ge=10, le=180)
    paid_budget_units: int = Field(default=0, ge=0, le=2)
    # Fresh paid Dex research can replace prior research and fill its own fields.
    allow_fresh_dex: bool = False

    @field_validator('company_urls')
    @classmethod
    def company_candidates(cls, urls):
        for url in urls:
            p = urlparse(url)
            if len(url) > 1000 or p.scheme != 'https' or not p.hostname or p.username or p.password or p.port not in (None, 443) or p.query or p.fragment:
                raise ValueError('Company candidates require credential-free HTTPS URLs without query or fragment')
        return urls

    @model_validator(mode='after')
    def valid_selection(self):
        if bool(self.dex_contact_id) == bool(self.query):
            raise ValueError('Supply exactly one dex_contact_id or query')
        if self.linkedin_html is not None and 'linkedin' not in self.sources:
            raise ValueError('linkedin_html requires the linkedin source')
        if self.company_urls and 'company_web' not in self.sources:
            raise ValueError('company_urls requires company_web')
        if 'dex_fresh' in self.sources and (not self.allow_fresh_dex or self.paid_budget_units < 1 or self.dry_run or self.write_policy == 'notes_only'):
            raise ValueError('dex_fresh requires fill_missing, explicit allow_fresh_dex, paid budget >= 1, and no dry-run; Dex may fill its own empty fields')
        return self
