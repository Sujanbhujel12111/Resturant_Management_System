"""Minimal compatibility shim for the removed stdlib `cgi` module.

This file provides a small subset of the original module's API so that
libraries (notably Django) that perform a simple `import cgi` won't fail
on Python versions where the stdlib `cgi` module is unavailable.

The shim implements a few helper functions used by Django's multipart
parsing code, notably `valid_boundary` and `parse_header`. It's intentionally
small — full multipart parsing should be handled by Django's `MultiPartParser`.
"""
from typing import Tuple, Dict, Any
import io
import re


def parse_header(line: str) -> Tuple[str, Dict[str, str]]:
    """Parse a header like Content-Type and return (value, params).

    Minimal implementation similar to stdlib `cgi.parse_header`.
    """
    if not line:
        return '', {}
    parts = line.split(';')
    value = parts[0].strip()
    params: Dict[str, str] = {}
    for p in parts[1:]:
        if '=' in p:
            k, v = p.split('=', 1)
            params[k.strip().lower()] = v.strip().strip('"')
    return value, params


def valid_boundary(boundary: Any) -> bool:
    """Return True if `boundary` looks like a valid multipart boundary.

    Accepts `bytes` or `str`. This mirrors the behaviour callers expect from
    the stdlib helper: limit length and allowed characters.
    """
    if not boundary:
        return False
    if isinstance(boundary, bytes):
        try:
            boundary = boundary.decode('ascii')
        except Exception:
            return False
    # Allow 1..70 characters of the common boundary charset used in practice.
    return bool(re.fullmatch(r"[A-Za-z0-9'()+_,\-./:=?]{1,70}", boundary))


def parse_multipart(fp: io.BytesIO, pdict: Dict[str, Any]) -> Dict[str, Any]:
    """Fallback parse_multipart returning an empty mapping.

    Detailed multipart parsing is complex; Django's `MultiPartParser`
    will be used for real uploads. This stub prevents import-time failures.
    """
    return {}


class FieldStorage:
    """Small stub of cgi.FieldStorage used only to avoid attribute errors.

    This does not attempt to implement full behaviour — it's a placeholder
    for code that only inspects attributes at import time.
    """
    def __init__(self, fp=None, headers=None, outerboundary=None, environ=None):
        self.fp = fp
        self.headers = headers or {}
        self.name = None
        self.filename = None
        self.value = None

    def read(self, *args, **kwargs):
        if self.fp is None:
            return b""
        return self.fp.read(*args, **kwargs)


# Simple HTML escape helper
def escape(s: Any) -> Any:
    if isinstance(s, str):
        return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return s
