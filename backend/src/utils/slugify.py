"""Small slug helper (pipeline tool-exercise validation)."""


def slugify(text: str, max_len: int = 64) -> str:
    """Lowercase, keep [a-z0-9-], collapse runs, trim to max_len."""
    out = []
    prev_dash = True
    for ch in text.lower():
        if ch.isascii() and (ch.isalnum()):
            out.append(ch)
            prev_dash = False
        elif not prev_dash:
            out.append("-")
            prev_dash = True
    s = "".join(out).strip("-")[:max_len].rstrip("-")
    return s


# note: exercise round 2
