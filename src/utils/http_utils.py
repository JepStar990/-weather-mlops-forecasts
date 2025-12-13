import hashlib
import json
import os
import time
from typing import Any, Dict, Optional
import requests
from src.config import CFG
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)
CACHE_DIR = os.path.join(".cache", "http")
os.makedirs(CACHE_DIR, exist_ok=True)

def _cache_path(key: str) -> str:
    return os.path.join(CACHE_DIR, f"{key}.json")

def _key_from(url: str, params: Optional[dict], headers: Optional[dict]) -> str:
    s = url + "|" + json.dumps(params or {}, sort_keys=True) + "|" + json.dumps(headers or {}, sort_keys=True)
    return hashlib.sha256(s.encode()).hexdigest()

def get_json(url: str, params: Optional[dict] = None, headers: Optional[dict] = None, ttl: int | None = None, timeout: int | None = None) -> Dict[str, Any]:
    ttl = ttl or CFG.REQUESTS_CACHE_TTL_SECONDS
    timeout = timeout or CFG.REQUESTS_TIMEOUT
    key = _key_from(url, params, headers)
    path = _cache_path(key)

    # serve from cache
    if os.path.exists(path):
        age = time.time() - os.path.getmtime(path)
        if age <= ttl:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

    # backoff loop
    backoff = 1.5
    for attempt in range(6):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=timeout)
            if r.status_code == 429 or 500 <= r.status_code < 600:
                raise requests.HTTPError(f"HTTP {r.status_code}: {r.text[:200]}")
            r.raise_for_status()
            data = r.json()
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f)
            except Exception:
                pass
            return data
        except Exception as e:
            sleep = backoff ** attempt
            logger.warning("GET %s failed (attempt %d): %s; sleeping %.            logger.warning("GET %s failed (attempt %d): %s; sleeping %.1fs", url, attempt + 1, e, sleep)
            time.sleep(sleep)
