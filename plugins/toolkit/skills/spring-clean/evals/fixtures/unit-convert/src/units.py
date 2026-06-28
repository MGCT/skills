"""Unit tables. Factors are relative to a base unit per category."""

# base: metre
LENGTH = {"mm": 0.001, "cm": 0.01, "m": 1.0, "km": 1000.0, "in": 0.0254, "ft": 0.3048}

# base: kilogram
MASS = {"mg": 1e-6, "g": 0.001, "kg": 1.0, "lb": 0.453592, "oz": 0.0283495}

TEMPERATURE = {"C", "F", "K"}


def category(unit):
    if unit in LENGTH:
        return "length"
    if unit in MASS:
        return "mass"
    if unit in TEMPERATURE:
        return "temperature"
    raise ValueError(f"unknown unit: {unit}")
