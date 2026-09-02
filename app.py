import pandas as pd
import streamlit as st
from dataclasses import replace

from src.model import Params, streams, energy, economics, emissions, heat_balance, validate
from src.optimize import grid_optimize

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
    annual_tpy = st.number_input("NH₃ production (t/y)", min_value=1_000, max_value=1_000_000, value=20_000, step=1_000)
    hours = st.number_input("Operating hours (h/y)", min_value=1_000, max_value=8_760, value=8_000, step=100)
    h2_kwh = st.slider("Electrolyzer electricity (kWh/kg H₂)", 40.0, 70.0, 52.0, 0.5)
    n2_recovery = st.slider("N₂ recovery", 0.80, 0.99, 0.92, 0.01)
    conversion = st.slider("NH₃ single-pass conversion", 0.05, 0.40, 0.18, 0.01)
    pressure = st.slider("Synthesis pressure (bar)", 80, 220, 150, 5)
    electricity_price = st.slider("Electricity price ($/MWh)", 10, 200, 60, 5)
    carbon_factor = st.slider("Electricity carbon factor (kg CO₂e/kWh)", 0.0, 1.0, 0.05, 0.01)

p = replace(
    Params(),
    annual_nh3_kg=annual_tpy * 1000,
    hours=hours,
    h2_kwh_per_kg=h2_kwh,
    n2_recovery=n2_recovery,
    nh3_conversion=conversion,
    pressure_bar=pressure,
    electricity_usd_mwh=electricity_price,
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

st.subheader("Scenario results")
c1, c2, c3, c4 = st.columns(4)
c1.metric("NH₃ production", f"{s['nh3_product_kg_h']/1000:.2f} t/h")
c2.metric("Specific energy", f"{e['specific_kwh_kg_nh3']:.2f} kWh/kg")
c3.metric("LCOA", f"${ec['lcoa_usd_per_t']:,.0f}/t")
c4.metric("CO₂ intensity", f"{em['kgco2_per_kg_nh3']:.3f} kg/kg")

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
            s["h2_feed_kg_h"],
            s["n2_gross_kg_h"],
            s["water_feed_kg_h"],
            s["h2_recycle_kmol_h"],
            s["n2_recycle_kmol_h"],
            e["total_kwh_h"],
            hb["useful_heat_credit_kwh_h"],
        ],
        "Unit": ["kg/h", "kg/h", "kg/h", "kmol/h", "kmol/h", "kWh/h", "kWh/h"],
    }
)
st.dataframe(balance, use_container_width=True, hide_index=True)

left, right = st.columns(2)
with left:
    st.subheader("Energy breakdown")
    energy_df = pd.DataFrame(
        {
            "Energy category": ["Electrolyzer", "Compression", "Synthesis heat"],
            "kWh/h": [e["electrolyzer_kwh_h"], e["compression_kwh_h"], e["synthesis_heat_kwh_h"]],
        }
    ).set_index("Energy category")
    st.bar_chart(energy_df)

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
            ],
            "USD/year": [
                ec["electricity_cost_usd_y"],
                ec["fixed_opex_usd_y"],
                ec["variable_opex_usd_y"],
                ec["annual_operating_cost_usd_y"],
                ec["annualized_capex_usd_y"],
            ],
        }
    )
    st.dataframe(economics_df, use_container_width=True, hide_index=True)

st.subheader("Optimization")
st.write(
    "The optimization uses the repository's deterministic grid search. "
    "It minimizes screening LCOA over the predefined design space."
)
if st.button("Run optimization", type="primary"):
    with st.spinner("Evaluating design grid..."):
        best, rows = grid_optimize(p)
    st.success("Optimization complete.")
    best_df = pd.DataFrame([best])
    st.dataframe(best_df, use_container_width=True, hide_index=True)
    csv = best_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download best design CSV", csv, "best_design.csv", "text/csv")

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
