"""Display-only unit and currency helpers for the Streamlit dashboard.

The engineering model remains in its native units (USD, kg, kWh, bar, etc.).
These helpers convert values only for presentation and user-facing inputs.
"""

from __future__ import annotations

CURRENCIES = {
    "USD": {"symbol": "$", "per_usd": 1.0},
    "EUR": {"symbol": "€", "per_usd": 0.92},
    "GBP": {"symbol": "£", "per_usd": 0.79},
    "INR": {"symbol": "₹", "per_usd": 83.0},
    "JPY": {"symbol": "¥", "per_usd": 150.0},
}

ENERGY_UNITS = {
    "kWh/h": 1.0,
    "MWh/h": 1.0 / 1000.0,
    "GWh/y": "annual",
}

MASS_FLOW_UNITS = {
    "kg/h": 1.0,
    "t/h": 1.0 / 1000.0,
    "kg/d": 24.0,
    "t/d": 24.0 / 1000.0,
}


def currency_info(currency: str, custom_rate: float | None = None) -> dict:
    """Return currency metadata; rate is selected-currency units per USD."""
    if currency not in CURRENCIES:
        raise ValueError(f"Unsupported currency: {currency}")
    info = CURRENCIES[currency].copy()
    info["per_usd"] = float(custom_rate if custom_rate is not None else info["per_usd"])
    if info["per_usd"] <= 0:
        raise ValueError("FX rate must be greater than zero")
    return info


def usd_to_currency(value_usd: float, currency: str, custom_rate: float | None = None) -> float:
    return float(value_usd) * currency_info(currency, custom_rate)["per_usd"]


def currency_label(currency: str, custom_rate: float | None = None) -> str:
    info = currency_info(currency, custom_rate)
    return f"{info['symbol']} ({currency})"


def format_money(value_usd: float, currency: str, custom_rate: float | None = None, decimals: int = 0) -> str:
    info = currency_info(currency, custom_rate)
    value = usd_to_currency(value_usd, currency, custom_rate)
    return f"{info['symbol']}{value:,.{decimals}f}"


def convert_energy(value_kwh_h: float, unit: str, hours: float) -> float:
    if unit not in ENERGY_UNITS:
        raise ValueError(f"Unsupported energy unit: {unit}")
    if unit == "GWh/y":
        return float(value_kwh_h) * float(hours) / 1_000_000.0
    return float(value_kwh_h) * float(ENERGY_UNITS[unit])


def convert_mass_flow(value_kg_h: float, unit: str) -> float:
    if unit not in MASS_FLOW_UNITS:
        raise ValueError(f"Unsupported mass-flow unit: {unit}")
    return float(value_kg_h) * float(MASS_FLOW_UNITS[unit])


def format_quantity(value: float, unit: str, decimals: int = 2) -> str:
    return f"{value:,.{decimals}f} {unit}"
