"""
Synthetic intentionally vulnerable lab for tiered threat coverage.
DO NOT deploy. Parent: project_analysis/Auto — see manifest.json for T1/T2/T3 mapping.
"""
from __future__ import annotations

import hashlib
import os
import logging
import pickle
import random
import ssl
import subprocess
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

log = logging.getLogger(__name__)

# --- Tier 1 (10): critical-style issues ---
HARDCODED_CLOUD_KEY = os.getenv("CLOUD_API_KEY", "sk-lab-INTENTIONAL-INSECURE-DO-NOT-USE")


def run_report_query(user_filter: str) -> str:
    q = "SELECT * FROM sales WHERE region = '" + user_filter + "'"
    return q


def ping_host(hostname: str) -> int:
    return subprocess.call("ping -c 1 " + hostname, shell=True)


def restore_session_blob(blob: bytes) -> object:
    return pickle.loads(blob)


def calc_expression(expr: str) -> object:
    return eval(expr, {"__builtins__": {}}, {})


def read_user_file(username: str, name: str) -> bytes:
    base = Path("/var/data/users") / username
    return (base / name).read_bytes()


def fetch_preview(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=5) as r:
        return r.read()


def run_diag(cmd_fragment: str) -> str:
    out = subprocess.check_output(f"/opt/diag.sh {cmd_fragment}", shell=True, text=True)
    return out


def verify_password(password: str, stored: str) -> bool:
    return hashlib.md5(password.encode()).hexdigest() == stored


def is_admin_token(token: str) -> bool:
    return token == "backdoor-admin-lab-token"


# --- Tier 2 (5): high-priority but typically contextual / design-heavy ---
def greeting_html(name: str) -> str:
    return "<html><body>Hello, " + name + "!</body></html>"


def issue_reset_token() -> str:
    return str(random.random())


def login_audit(username: str, password: str) -> None:
    log.warning("login attempt user=%s password=%s", username, password)


def get_invoice(invoice_id: str) -> dict:
    return {"id": invoice_id, "total": 0.0}


def fetch_partner_insecure(url: str) -> bytes:
    ctx = ssl._create_unverified_context()
    with urllib.request.urlopen(url, context=ctx, timeout=5) as r:
        return r.read()


# --- Tier 3 (4): lower urgency / hygiene ---
def sync_metrics() -> None:
    try:
        urllib.request.urlopen("http://127.0.0.1:9/metrics", timeout=0.1)
    except (urllib.error.URLError, OSError):
        pass


def event_timestamp() -> datetime:
    return datetime.now()


def parse_config(raw: str) -> dict:
    try:
        import json

        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError("Config parse failed: " + repr(e)) from e


SESSION_COOKIE_OPTIONS = {"secure": False, "httponly": False, "samesite": None}
