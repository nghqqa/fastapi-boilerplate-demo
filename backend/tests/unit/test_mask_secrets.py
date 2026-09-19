from backend.src.utils.mask_secrets import mask_secrets


def test_mask():
    r = mask_secrets({"user": "u", "api_key": "k", "note": "n"})
    assert r == {"user": "u", "api_key": "***", "note": "n"}
