from backend.src.utils.humanize_time import humanize_duration


def test_formats():
    assert humanize_duration(3723) == "1h 2m 3s"
    assert humanize_duration(0) == "0s"
    assert humanize_duration(-5) == "0s"
