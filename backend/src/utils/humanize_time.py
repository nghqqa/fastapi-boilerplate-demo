"""Human-friendly durations (final toolchain validation, fresh code)."""


def humanize_duration(seconds: int) -> str:
    """Return e.g. '1h 2m 3s'; negative input clamps to 0."""
    seconds = max(0, int(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    parts = []
    if h:
        parts.append(f"{h}h")
    if m or h:
        parts.append(f"{m}m")
    parts.append(f"{s}s")
    return " ".join(parts)
