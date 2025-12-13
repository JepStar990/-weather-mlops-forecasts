from typing import Literal, Optional

Variable = Literal["temp_2m", "wind_speed_10m", "precipitation"]

def to_celsius(x: float, unit: str) -> float:
    if unit in ("C", "°C", "celsius"):
               return x
    if unit in ("K", "kelvin"):
        return x - 273.15
    if unit in ("F", "°F", "fahrenheit"):
        return (x - 32.0) * 5.0 / 9.0
    raise ValueError(f"Unsupported temp unit: {unit}")

def to_mps(x: float, unit: str) -> float:
    if unit in ("m/s", "mps"):
        return x
    if unit in ("km/h", "kmh", "kph"):
        return x / 3.6
    if unit in ("mph",):
        return x * 0.44704
    if unit in ("kt", "knot", "knots"):
        return x * 0.514444
    raise ValueError(f"Unsupported wind unit: {unit}")

def to_mm(x: float, unit: str) -> float:
    if unit in ("mm",):
        return x
    if unit in ("cm",):
        return x * 10.0
    if unit in ("m",):
        return x * 1000.0
    if unit in ("in", "inch", "inches"):
        return x * 25.4
    raise ValueError(f"Unsupported precip unit: {unit}")

def normalize_value(variable: Variable, value: float, src_unit: Optional[str]) -> tuple[float, str]:
    """Return (value_SI, unit_SI) for variable."""
    if variable == "temp_2m":
        return to_celsius(value, src_unit or "C"), "C"
    if variable == "wind_speed_10m":
        return to_mps(value, src_unit or "m/s"), "m/s"
    if variable == "precipitation":
        return to_mm(value, src_unit or "mm"), "mm"
