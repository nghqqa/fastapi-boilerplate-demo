from backend.src.utils.env_check import validate_env


def test_valid():
    assert validate_env({"APP_NAME": "x", "APP_ENV": "prod"}) == []


def test_missing_and_weak():
    problems = validate_env({"APP_NAME": "x", "DB_PASSWORD": "short"})
    assert any("APP_ENV" in p for p in problems)
    assert any("weak" in p for p in problems)
