import pytest

from convert import convert


def test_length():
    assert convert(100, "cm", "m") == 1.0


def test_temp_f_to_c():
    assert convert(32, "F", "C") == 0.0


def test_cross_category_raises():
    with pytest.raises(ValueError):
        convert(1, "kg", "m")
