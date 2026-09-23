from backend.src.utils.slugify import slugify


def test_basic():
    assert slugify("Hello, World! 2026") == "hello-world-2026"


def test_empty_and_trim():
    assert slugify("!!!") == ""
    assert len(slugify("a" * 100)) == 64
