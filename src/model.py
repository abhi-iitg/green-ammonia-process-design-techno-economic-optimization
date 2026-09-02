from dataclasses import dataclass
from math import ceil

H2_MW=2.016
N2_MW=28.014
NH3_MW=17.031
H2O_MW=18.015

@dataclass(frozen=True)
class Params:
    annual_nh3_kg: float=20_000_000
    hours: float=8000
    h2_kwh_per_kg: float=52.0
    n2_recovery: float=0.92
    nh3_conversion: float=0.18
    product_recovery: float=0.995
    pressure_bar: float=150.0
    electricity_usd_mwh: float=60.0
    grid_factor_kgco2_kwh: float=0.45
    renewable_factor_kgco2_kwh: float=0.05
    water_excess: float=0.05
    compression_kwh_per_kg_nh3: float=0.22
    synthesis_heat_kwh_per_kg_nh3: float=0.35
    capex_usd: float=42_000_000
    fixed_opex_frac: float=0.035
    variable_opex_usd_per_t: float=55.0
    discount_rate: float=0.10
    life_years: int=20

def streams(p=Params()):
    nh3_h=p.annual_nh3_kg/p.hours
    nh3_kmol=nh3_h/NH3_MW
    h2_stoich=1.5*nh3_kmol
    n2_stoich=0.5*nh3_kmol
    # account for product recovery loss; synthesis must make slightly more NH3
    nh3_synth=nh3_kmol/p.product_recovery
    h2_reaction=1.5*nh3_synth
    n2_reaction=0.5*nh3_synth
    # Reactor feed is larger than fresh feed because unreacted H2/N2 are recycled.
    h2_reactor=h2_reaction/p.nh3_conversion
    n2_reactor=n2_reaction/p.nh3_conversion
    unreacted_h2=h2_reactor-h2_reaction
    unreacted_n2=n2_reactor-n2_reaction
    purge=0.02
    h2_fresh=h2_reaction+purge*unreacted_h2
    n2_fresh=h2_fresh*0 + n2_reaction+purge*unreacted_n2
    n2_gross=n2_fresh/p.n2_recovery
    h2_kg=h2_fresh*H2_MW
    n2_kg=n2_gross*N2_MW
    water_kg=h2_kg*(9.0/1.0)*(1+p.water_excess)
    return dict(nh3_product_kg_h=nh3_h, nh3_product_kmol_h=nh3_kmol,
                nh3_synthesis_kmol_h=nh3_synth, h2_feed_kg_h=h2_kg,
                h2_reactor_kmol_h=h2_reactor, n2_reactor_kmol_h=n2_reactor,
                h2_recycle_kmol_h=unreacted_h2*(1-purge), n2_recycle_kmol_h=unreacted_n2*(1-purge),
                n2_synthesis_kg_h=n2_fresh*N2_MW, n2_gross_kg_h=n2_kg,
                water_feed_kg_h=water_kg, h2_kmol_h=h2_fresh, n2_kmol_h=n2_gross)

def energy(p=Params()):
    s=streams(p)
    electrolyzer=s['h2_feed_kg_h']*p.h2_kwh_per_kg
    recycle_compression=0.08*s['h2_recycle_kmol_h']*H2_MW + 0.02*s['n2_recycle_kmol_h']*N2_MW
    compression=p.compression_kwh_per_kg_nh3*s['nh3_product_kg_h'] + recycle_compression
    synthesis_heat=p.synthesis_heat_kwh_per_kg_nh3*s['nh3_product_kg_h']
    total=electrolyzer+compression+synthesis_heat
    return dict(electrolyzer_kwh_h=electrolyzer, compression_kwh_h=compression,
                synthesis_heat_kwh_h=synthesis_heat,total_kwh_h=total,
                specific_kwh_kg_nh3=total/s['nh3_product_kg_h'])

def economics(p=Params()):
    e=energy(p); annual_kwh=e['total_kwh_h']*p.hours
    annual_elec=annual_kwh*p.electricity_usd_mwh/1000
    fixed=p.capex_usd*p.fixed_opex_frac
    variable=p.variable_opex_usd_per_t*(p.annual_nh3_kg/1000)
    annual_cost=annual_elec+fixed+variable
    annuity=p.discount_rate*(1+p.discount_rate)**p.life_years/((1+p.discount_rate)**p.life_years-1)
    annualized_capex=p.capex_usd*annuity
    lcoa=(annual_cost+annualized_capex)/(p.annual_nh3_kg/1000)
    return dict(annual_electricity_kwh=annual_kwh, electricity_cost_usd_y=annual_elec,
                fixed_opex_usd_y=fixed, variable_opex_usd_y=variable,
                annual_operating_cost_usd_y=annual_cost, annualized_capex_usd_y=annualized_capex,
                lcoa_usd_per_t=lcoa)

def emissions(p=Params(), factor=None):
    f=p.renewable_factor_kgco2_kwh if factor is None else factor
    e=energy(p); kg=e['total_kwh_h']*p.hours*f
    return dict(annual_kgco2=kg, kgco2_per_kg_nh3=kg/p.annual_nh3_kg)

def heat_balance(p=Params()):
    s=streams(p)
    recoverable=0.22*s['nh3_product_kg_h']*p.hours/8000
    useful=min(recoverable,0.15*s['nh3_product_kg_h'])
    return dict(recoverable_kwh_h=recoverable, useful_heat_credit_kwh_h=useful)

def equilibrium_conversion(pressure_bar, temperature_K=700.0):
    # Transparent screening correlation: higher pressure improves conversion, higher T penalizes equilibrium.
    x=0.08 + 0.00075*pressure_bar - 0.00010*(temperature_K-650)
    return max(0.05,min(0.45,x))

def validate(p=Params()):
    s=streams(p)
    # Product stoichiometry must hold at the reaction level.
    nh3=s['nh3_synthesis_kmol_h']
    assert abs(s['h2_reactor_kmol_h']*p.nh3_conversion - 1.5*nh3) < 1e-9
    assert abs(s['n2_reactor_kmol_h']*p.nh3_conversion - 0.5*nh3) < 1e-9
    assert s['h2_feed_kg_h'] < s['h2_reactor_kmol_h']*H2_MW
    assert s['nh3_product_kg_h'] > 0
    return True
