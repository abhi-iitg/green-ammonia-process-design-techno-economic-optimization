import pandas as pd
import streamlit as st
from dataclasses import replace

from src.model import Params, streams, energy, economics, emissions, heat_balance, validate
from src.optimize import grid_optimize
from src.display import (
    CURRENCIES,
    ENERGY_UNITS,
    MASS_FLOW_UNITS,
    currency_info,
    usd_to_currency,
    format_money,
    convert_energy,
    convert_mass_flow,
)

st.set_page_config(
    page_title="GreenAmmonia-Opt | Process Design",
    page_icon="🧪",
    layout="wide",
)

st.title("🧪 GreenAmmonia-Opt")
st.caption("Green ammonia process design, techno-economic screening and constrained optimization")

st.markdown(
    """
    **Decision-support dashboard:** explore how electrolyzer performance, synthesis conversion,
    nitrogen recovery and electricity price affect a screening-level green ammonia design.

    > This is an engineering screening model. It is **not** a substitute for a rigorous Aspen Plus
    > simulation, detailed equipment design, vendor quotations, or plant safety review.
    """
)

with st.sidebar:
    st.header("Scenario inputs")
    annual_tpy = st.number_input(
        "NH₃ production (t/y)", min_value=1_000, max_value=1_000_000,
        value=20_000, step=1_000
    )
    hours = st.number_input(
        "Operating hours (h/y)", min_value=1_000, max_value=8_760,
        value=8_000, step=100
    )
    h2_kwh = st.slider("Electrolyzer electricity (kWh/kg H₂)", 40.0, 70.0, 52.0, 0.5)
    n2_recovery = st.slider("N₂ recovery", 0.80, 0.99, 0.92, 0.01)
    conversion = st.slider("NH₃ single-pass conversion", 0.05, 0.40, 0.18, 0.01)
    pressure = st.slider("Synthesis pressure (bar)", 80, 220, 150, 5)
    carbon_factor = st.slider("Electricity carbon factor (kg CO₂e/kWh)", 0.0, 1.0, 0.05, 0.01)

    st.divider()
    st.header("Display & units")
    currency = st.selectbox("Display currency", list(CURRENCIES), index=0)
    default_fx = CURRENCIES[currency]["per_usd"]
    fx_rate = st.number_input(
        f"FX rate ({currency} per USD)", min_value=0.000001,
        value=float(default_fx), step=max(default_fx * 0.01, 0.000001),
        format="%.6f",
        help="Display/input conversion only. The engineering model remains internally denominated in USD."
    )
    energy_unit = st.selectbox("Energy display unit", list(ENERGY_UNITS), index=0)
    mass_unit = st.selectbox("Mass-flow display unit", list(MASS_FLOW_UNITS), index=0)
    st.caption(
        "Currency conversion is presentation-level. USD remains the model's internal currency. "
        "Edit the FX rate when you want a different assumption."
    )

    currency_meta = currency_info(currency, fx_rate)
    currency_symbol = currency_meta["symbol"]
    electricity_default_display = 60.0 * fx_rate
    electricity_price_display = st.number_input(
        f"Electricity price ({currency}/MWh)",
        min_value=0.0,
        value=float(electricity_default_display),
        step=max(electricity_default_display * 0.05, 0.01),
        format="%.2f",
        help=f"User-facing price in {currency}. Converted to USD/MWh internally using the FX rate above."
    )
    electricity_price_usd = electricity_price_display / fx_rate

p = replace(
    Params(),
    annual_nh3_kg=annual_tpy * 1000,
    hours=hours,
    h2_kwh_per_kg=h2_kwh,
    n2_recovery=n2_recovery,
    nh3_conversion=conversion,
    pressure_bar=pressure,
    electricity_usd_mwh=electricity_price_usd,
)

try:
    validate(p)
    s = streams(p)
    e = energy(p)
    ec = economics(p)
    em = emissions(p, carbon_factor)
    hb = heat_balance(p)
except (AssertionError, ValueError, ZeroDivisionError) as exc:
    st.error(f"Scenario validation failed: {exc}")
    st.stop()

# Display helpers. Model values remain in native units; only these values are converted.
def money(value_usd: float, decimals: int = 0) -> str:
    return format_money(value_usd, currency, fx_rate, decimals)


def energy_value(value_kwh_h: float) -> float:
    return convert_energy(value_kwh_h, energy_unit, hours)


def mass_value(value_kg_h: float) -> float:
    return convert_mass_flow(value_kg_h, mass_unit)

st.subheader("Scenario results")
c1, c2, c3, c4 = st.columns(4)
c1.metric("NH₃ production", f"{mass_value(s['nh3_product_kg_h']):,.2f} {mass_unit}")
c2.metric("Specific energy", f"{e['specific_kwh_kg_nh3']:.2f} kWh/kg NH₃")
c3.metric("LCOA", f"{money(ec['lcoa_usd_per_t'], 0)}/t NH₃")
c4.metric("CO₂ intensity", f"{em['kgco2_per_kg_nh3']:.3f} kg CO₂e/kg")

st.caption(
    f"All economic values below are displayed in {currency}. Internal model currency: USD. "
    f"FX assumption: 1 USD = {fx_rate:g} {currency}."
)

st.subheader("Material and utility balance")
balance = pd.DataFrame(
    {
        "Metric": [
            "H₂ fresh feed",
            "N₂ gross feed",
            "Water feed",
            "H₂ recycle",
            "N₂ recycle",
            "Total utility demand",
            "Useful heat credit",
        ],
        "Value": [
            mass_value(s["h2_feed_kg_h"]),
            mass_value(s["n2_gross_kg_h"]),
            mass_value(s["water_feed_kg_h"]),
            s["h2_recycle_kmol_h"],
            s["n2_recycle_kmol_h"],
            energy_value(e["total_kwh_h"]),
            energy_value(hb["useful_heat_credit_kwh_h"]),
        ],
        "Unit": [
            mass_unit, mass_unit, mass_unit, "kmol/h", "kmol/h",
            energy_unit, energy_unit,
        ],
    }
)
st.dataframe(balance, use_container_width=True, hide_index=True)

left, right = st.columns(2)
with left:
    st.subheader("Energy breakdown")
    energy_categories = ["Electrolyzer", "Compression", "Synthesis heat"]
    energy_values = [
        energy_value(e["electrolyzer_kwh_h"]),
        energy_value(e["compression_kwh_h"]),
        energy_value(e["synthesis_heat_kwh_h"]),
    ]
    energy_df = pd.DataFrame(
        {f"Energy ({energy_unit})": energy_values}, index=energy_categories
    )
    st.bar_chart(energy_df)
    total_energy = sum(energy_values)
    shares = [100 * v / total_energy for v in energy_values]
    energy_summary = pd.DataFrame(
        {
            "Energy category": energy_categories,
            f"Energy ({energy_unit})": energy_values,
            "Share (%)": shares,
        }
    )
    st.dataframe(energy_summary, use_container_width=True, hide_index=True)
    st.caption(
        "The breakdown uses the same selected display unit as the chart. "
        "GWh/y annualizes each hourly energy-rate component using the selected operating hours."
    )

with right:
    st.subheader("Economics")
    economics_df = pd.DataFrame(
        {
            "Metric": [
                "Annual electricity cost",
                "Fixed OPEX",
                "Variable OPEX",
                "Annual operating cost",
                "Annualized CAPEX",
                "LCOA",
            ],
            f"{currency}/year": [
                usd_to_currency(ec["electricity_cost_usd_y"], currency, fx_rate),
                usd_to_currency(ec["fixed_opex_usd_y"], currency, fx_rate),
                usd_to_currency(ec["variable_opex_usd_y"], currency, fx_rate),
                usd_to_currency(ec["annual_operating_cost_usd_y"], currency, fx_rate),
                usd_to_currency(ec["annualized_capex_usd_y"], currency, fx_rate),
                None,
            ],
            f"{currency}/t NH₃": [
                None, None, None, None, None,
                usd_to_currency(ec["lcoa_usd_per_t"], currency, fx_rate),
            ],
        }
    )
    st.dataframe(economics_df, use_container_width=True, hide_index=True)
    st.caption(
        f"Electricity price used by the model: {money(electricity_price_usd, 2)}/MWh. "
        "All rows are converted from the model's USD values using the selected FX rate."
    )

st.subheader("Optimization")
st.write(
    "The optimization uses the repository's deterministic grid search. "
    "It minimizes screening LCOA over the predefined design space. "
    "Optimization is performed in USD internally; the result is converted to the selected display currency."
)
if st.button("Run optimization", type="primary"):
    with st.spinner("Evaluating design grid..."):
        best, rows = grid_optimize(p)
    st.success("Optimization complete.")
    best_display = best.copy()
    best_display[f"lcoa_{currency}_per_t"] = usd_to_currency(best["lcoa_usd_per_t"], currency, fx_rate)
    best_display[f"electricity_{currency}_per_mwh"] = usd_to_currency(best["electricity_usd_mwh"], currency, fx_rate)
    best_display.pop("lcoa_usd_per_t", None)
    best_display.pop("electricity_usd_mwh", None)
    best_df = pd.DataFrame([best_display])
    st.dataframe(best_df, use_container_width=True, hide_index=True)
    csv = best_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download best design CSV", csv, "best_design_display.csv", "text/csv")

st.subheader("Engineering context")
st.markdown(
    """
    - **Reaction:** N₂ + 3H₂ ⇌ 2NH₃
    - **Main energy driver:** hydrogen production by electrolysis
    - **Loop strategy:** recycle unreacted H₂/N₂ and purge a small fraction
    - **Validation path:** compare this screening model against a genuine Aspen Plus flowsheet
    - **Decision use:** early-stage screening, sensitivity analysis and interview-ready engineering discussion
    """
)

st.info(
    "For a reproducible repository run, use `python -m pytest -q` followed by "
    "`python -m src.run_all`. The generated CSVs and figures are stored in `results/` and `figures/`."
)
