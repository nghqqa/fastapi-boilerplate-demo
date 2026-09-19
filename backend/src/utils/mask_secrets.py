"""Log secret masker (full-toolchain validation, fresh code)."""

_PATTERNS = ("password", "secret", "token", "api_key")


def mask_secrets(data: dict) -> dict:
    """Return a copy with credential-looking values masked."""
    out = {}
    for key, value in data.items():
        if any(p in key.lower() for p in _PATTERNS):
            out[key] = "***"
        else:
            out[key] = value
    return out
