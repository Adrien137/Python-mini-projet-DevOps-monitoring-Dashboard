"""Tests de api.metrics."""

from api.metrics import get_system_metrics


def test_metrics_contains_expected_fields():
    data = get_system_metrics()
    assert "cpu_percent" in data
    assert "memory_percent" in data
    assert "disk_percent" in data


def test_metrics_values_are_in_valid_range():
    data = get_system_metrics()
    for key in ("cpu_percent", "memory_percent", "disk_percent"):
        assert 0 <= data[key] <= 100
