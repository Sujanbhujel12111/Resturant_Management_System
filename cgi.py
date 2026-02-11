"""Minimal compatibility shim for the removed stdlib `cgi` module.

This file provides a small subset of the original module's API so that
libraries (notably older Django versions) that perform a simple
`import cgi` will not fail on Python versions where the stdlib module
is removed (3.13+).

The shim implements light-weight placeholders only; it is NOT a full
replacement. It aims to satisfy imports and basic parsing calls used
during initial application startup. For full multipart/form-data
parsing rely on Django's `MultiPartParser` (already present) or
upgrade to a Python version that includes the stdlib `cgi` module.
"""
from typing import Tuple, Dict, Any
import io


def parse_header(line: str) -> Tuple[str, Dict[str, str]]:
    """Parse a header like Content-Type: return (value, params).

    This is a minimal implementation sufficient for basic usage.
    """
    parts = line.split(";")
    value = parts[0].strip()
    params = {}
    for p in parts[1:]:
        if '=' in p:
            k, v = p.split('=', 1)
            params[k.strip().lower()] = v.strip().strip('"')
    return value, params


def parse_multipart(fp: io.BytesIO, pdict: Dict[str, Any]) -> Dict[str, Any]:
    """Fallback parse_multipart that returns an empty mapping.

    Real multipart parsing is complex and handled by Django's
    `MultiPartParser` in production; returning an empty dict prevents
    import-time failures while leaving actual parsing to Django.
    """
    return {}


class FieldStorage:
    """Very small stub of cgi.FieldStorage.

    The real FieldStorage is used by some libraries to represent
    uploaded form fields. We provide a minimal object that won't
    break simple attribute access during imports.
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


# Provide small commonly-used helpers
escape = lambda s: (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;') if isinstance(s, str) else s)
