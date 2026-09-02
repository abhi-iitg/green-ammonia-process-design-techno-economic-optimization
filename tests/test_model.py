from dataclasses import replace
from src.model import Params,streams,energy,economics,emissions,equilibrium_conversion,validate
from src.optimize import grid_optimize

def test_annual_rate():
 s=streams(); assert abs(s['nh3_product_kg_h']-2500)<1e-9

def test_stoichiometry():
 s=streams(); assert s['h2_reactor_kmol_h']*0.18 == s['h2_reactor_kmol_h']*0.18 and abs((s['h2_reactor_kmol_h']*0.18)-1.5*s['nh3_synthesis_kmol_h'])<1e-9

def test_n2_recovery_relation():
 s=streams(); assert abs(s['n2_reactor_kmol_h']*0.18-0.5*s['nh3_synthesis_kmol_h'])<1e-9

def test_water_positive(): assert streams()['water_feed_kg_h']>0

def test_energy_positive(): assert energy()['total_kwh_h']>energy()['electrolyzer_kwh_h']

def test_electrolyzer_dominates():
 e=energy(); assert e['electrolyzer_kwh_h']>e['compression_kwh_h']

def test_lcoa_positive(): assert economics()['lcoa_usd_per_t']>0

def test_renewable_lower_than_grid(): assert emissions(Params(),0.05)['kgco2_per_kg_nh3']<emissions(Params(),0.45)['kgco2_per_kg_nh3']

def test_conversion_bounds():
 assert 0.05<=equilibrium_conversion(100)<=0.45
 assert equilibrium_conversion(200)>=equilibrium_conversion(100)

def test_validation(): assert validate()

def test_pressure_does_not_break_model(): assert economics(replace(Params(),pressure_bar=200))['lcoa_usd_per_t']>0

def test_grid_has_best():
 best,rows=grid_optimize(); assert best['feasible'] and len(rows)==5*5*5*3*5

def test_best_is_minimum():
 best,rows=grid_optimize(); vals=[r['lcoa_usd_per_t'] for r in rows if r['feasible']]; assert best['lcoa_usd_per_t']==min(vals)

def test_deterministic_grid():
 assert grid_optimize()[0]==grid_optimize()[0]

def test_product_scaling():
 a=streams(Params(annual_nh3_kg=40_000_000)); b=streams(); assert abs(a['nh3_product_kg_h']/b['nh3_product_kg_h']-2)<1e-12
