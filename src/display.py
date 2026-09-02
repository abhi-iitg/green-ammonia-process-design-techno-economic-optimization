"""Display-only unit, currency and dashboard-table helpers.

The engineering model remains in native units:
- USD for economics
- kWh/h for energy rates
- kg/h for mass flow

All conversions in this module are presentation-level unless explicitly noted.
"""
from __future__ import annotations

import pandas as pd

CURRENCIES = {
    "USD": {"symbol": "$", "per_usd": 1.0},
    "EUR": {"symbol": "€", "per_usd": 0.92},
    "GBP": {"symbol": "£", "per_usd": 0.79},
    "INR": {"symbol": "₹", "per_usd": 83.0},
    "JPY": {"symbol": "¥", "per_usd": 150.0},
}

ENERGY_UNITS = {"kWh/h": 1.0, "MWh/h": 1.0 / 1000.0, "GWh/y": "annual"}
MASS_FLOW_UNITS = {"kg/h": 1.0, "t/h": 1.0 / 1000.0, "kg/d": 24.0, "t/d": 24.0 / 1000.0}


def currency_info(currency: str, custom_rate: float | None = None) -> dict:
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
    if hours <= 0:
        raise ValueError("Operating hours must be greater than zero")
    if unit == "GWh/y":
        return float(value_kwh_h) * float(hours) / 1_000_000.0
    return float(value_kwh_h) * float(ENERGY_UNITS[unit])


def convert_mass_flow(value_kg_h: float, unit: str) -> float:
    if unit not in MASS_FLOW_UNITS:
        raise ValueError(f"Unsupported mass-flow unit: {unit}")
    return float(value_kg_h) * float(MASS_FLOW_UNITS[unit])


def format_quantity(value: float, unit: str, decimals: int = 2) -> str:
    return f"{value:,.{decimals}f} {unit}"


def build_economics_table(ec: dict, annual_nh3_t: float, currency: str, fx_rate: float) -> pd.DataFrame:
    """Build a complete, unit-consistent economics table.

    Annual-cost rows show both annual cost and cost per tonne. LCOA is a
    per-tonne metric, so its annual column shows the equivalent annualized
    cost (LCOA multiplied by annual NH3 production) rather than a blank/None.
    """
    if annual_nh3_t <= 0:
        raise ValueError("Annual NH3 production must be greater than zero")

    annual_rows = [
        ("Annual electricity cost", ec["electricity_cost_usd_y"]),
        ("Fixed OPEX", ec["fixed_opex_usd_y"]),
        ("Variable OPEX", ec["variable_opex_usd_y"]),
        ("Annual operating cost", ec["annual_operating_cost_usd_y"]),
        ("Annualized CAPEX", ec["annualized_capex_usd_y"]),
    ]
    total_annualized = ec["annual_operating_cost_usd_y"] + ec["annualized_capex_usd_y"]

    rows = []
    for metric, usd_y in annual_rows:
        rows.append({
            "Metric": metric,
            f"{currency}/year": usd_to_currency(usd_y, currency, fx_rate),
            f"{currency}/t NH₃": usd_to_currency(usd_y / annual_nh3_t, currency, fx_rate),
        })

    rows.append({
        "Metric": "Total annualized cost",
        f"{currency}/year": usd_to_currency(total_annualized, currency, fx_rate),
        f"{currency}/t NH₃": usd_to_currency(total_annualized / annual_nh3_t, currency, fx_rate),
    })
    # LCOA is defined per tonne, but its annual equivalent is still meaningful:
    # LCOA × annual NH3 production = annualized cost represented by the LCOA.
    # Showing this value avoids an apparently empty cell while keeping the
    # relationship between the two units explicit.
    lcoa_annual_usd = ec["lcoa_usd_per_t"] * annual_nh3_t
    rows.append({
        "Metric": "LCOA",
        f"{currency}/year": usd_to_currency(lcoa_annual_usd, currency, fx_rate),
        f"{currency}/t NH₃": usd_to_currency(ec["lcoa_usd_per_t"], currency, fx_rate),
    })
    return pd.DataFrame(rows)


def build_energy_breakdown(e: dict, unit: str, hours: float) -> pd.DataFrame:
    categories = ["Electrolyzer", "Compression", "Synthesis heat"]
    values = [
        convert_energy(e["electrolyzer_kwh_h"], unit, hours),
        convert_energy(e["compression_kwh_h"], unit, hours),
        convert_energy(e["synthesis_heat_kwh_h"], unit, hours),
    ]
    total = sum(values)
    shares = [100.0 * value / total for value in values] if total > 0 else [0.0] * len(values)
    return pd.DataFrame({"Energy category": categories, f"Energy ({unit})": values, "Share (%)": shares})


def convert_electricity_price_to_usd(display_price: float, currency: str, fx_rate: float) -> float:
    if display_price < 0:
        raise ValueError("Electricity price cannot be negative")
    if fx_rate <= 0:
        raise ValueError("FX rate must be greater than zero")
    currency_info(currency, fx_rate)
    return float(display_price) / float(fx_rate)
