import math

from src.display import (
    build_economics_table,
    build_energy_breakdown,
    convert_electricity_price_to_usd,
    currency_info,
    convert_energy,
    convert_mass_flow,
    usd_to_currency,
)
from src.model import Params, economics, energy


def test_currency_conversion_identity():
    assert usd_to_currency(100.0, "USD") == 100.0


def test_currency_conversion_changes_display_value():
    assert usd_to_currency(100.0, "INR", 83.0) == 8300.0


def test_energy_display_conversion():
    assert convert_energy(1000.0, "MWh/h", 8000) == 1.0
    assert convert_energy(1000.0, "GWh/y", 8000) == 8.0


def test_mass_flow_display_conversion():
    assert convert_mass_flow(1000.0, "t/h") == 1.0
    assert convert_mass_flow(1000.0, "t/d") == 24.0


def test_invalid_fx_rate_rejected():
    try:
        currency_info("USD", 0)
    except ValueError:
        return
    assert False, "Expected invalid FX rate to raise ValueError"


def test_electricity_price_display_round_trip():
    assert convert_electricity_price_to_usd(4980.0, "INR", 83.0) == 60.0
    assert convert_electricity_price_to_usd(55.2, "EUR", 0.92) == 60.0


def test_economics_table_has_no_none_values():
    p = Params()
    ec = economics(p)
    table = build_economics_table(ec, p.annual_nh3_kg / 1000.0, "USD", 1.0)
    assert not table.isna().any().any()
    assert table["USD/year"].notna().all()
    assert table["USD/t NH₃"].notna().all()
    assert "—" not in table["USD/year"].astype(str).tolist()
    assert "None" not in table["USD/year"].astype(str).tolist()


def test_economics_table_unit_costs_are_correct():
    p = Params()
    ec = economics(p)
    annual_t = p.annual_nh3_kg / 1000.0
    table = build_economics_table(ec, annual_t, "USD", 1.0)
    elec = table.loc[table["Metric"] == "Annual electricity cost"].iloc[0]
    assert math.isclose(elec["USD/t NH₃"], ec["electricity_cost_usd_y"] / annual_t)
    lcoa = table.loc[table["Metric"] == "LCOA"].iloc[0]
    assert math.isclose(lcoa["USD/t NH₃"], ec["lcoa_usd_per_t"])
    assert math.isclose(lcoa["USD/year"], ec["lcoa_usd_per_t"] * annual_t)


def test_economics_currency_columns_change_together():
    p = Params()
    ec = economics(p)
    annual_t = p.annual_nh3_kg / 1000.0
    usd = build_economics_table(ec, annual_t, "USD", 1.0)
    inr = build_economics_table(ec, annual_t, "INR", 83.0)
    assert "USD/year" in usd.columns and "USD/t NH₃" in usd.columns
    assert "INR/year" in inr.columns and "INR/t NH₃" in inr.columns
    assert "USD/year" not in inr.columns and "USD/t NH₃" not in inr.columns
    assert math.isclose(
        inr.loc[inr["Metric"] == "LCOA", "INR/t NH₃"].iloc[0],
        usd.loc[usd["Metric"] == "LCOA", "USD/t NH₃"].iloc[0] * 83.0,
    )


def test_energy_breakdown_converts_all_rows_consistently():
    p = Params()
    e = energy(p)
    kwh = build_energy_breakdown(e, "kWh/h", p.hours)
    mwh = build_energy_breakdown(e, "MWh/h", p.hours)
    gwh = build_energy_breakdown(e, "GWh/y", p.hours)
    for _, row in kwh.iterrows():
        category = row["Energy category"]
        m = mwh.loc[mwh["Energy category"] == category].iloc[0]
        g = gwh.loc[gwh["Energy category"] == category].iloc[0]
        assert math.isclose(m["Energy (MWh/h)"], row["Energy (kWh/h)"] / 1000.0)
        assert math.isclose(g["Energy (GWh/y)"], row["Energy (kWh/h)"] * p.hours / 1_000_000.0)
