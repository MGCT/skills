"""Public conversion entry point."""
from units import LENGTH, MASS, category


def convert(value, from_unit, to_unit):
    cat_from, cat_to = category(from_unit), category(to_unit)
    if cat_from != cat_to:
        raise ValueError(f"cannot convert {from_unit} to {to_unit}")
    if cat_from == "temperature":
        return _convert_temp(value, from_unit, to_unit)
    table = LENGTH if cat_from == "length" else MASS
    return value * table[from_unit] / table[to_unit]


def _convert_temp(value, from_unit, to_unit):
    # normalise to Celsius first
    if from_unit == "F":
        c = (value - 32) * 5 / 9
    elif from_unit == "K":
        c = value - 273.15
    else:
        c = value
    if to_unit == "F":
        return c * 9 / 5 + 32
    if to_unit == "K":
        return c + 273.15
    return c
