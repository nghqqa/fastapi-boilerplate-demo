"""Environment variable validator (pipeline full-toolchain validation)."""

_REQUIRED = ("APP_NAME", "APP_ENV")


def validate_env(env: dict) -> list:
    """Return a list of problems; empty list means env is valid."""
    problems = []
    for key in _REQUIRED:
        value = env.get(key, "")
        if not value or not value.strip():
            problems.append(f"missing required env: {key}")
    for key, value in env.items():
        if "secret" in key.lower() or "password" in key.lower():
            if len(str(value)) < 12:
                problems.append(f"weak credential length: {key}")
    return problems
