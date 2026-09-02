from dataclasses import replace
from .model import Params, economics, energy, emissions

def grid_optimize(base=Params()):
    best=None
    rows=[]
    for eff in [48,50,52,54,56]:
      for pbar in [100,125,150,175,200]:
       for conv in [0.12,0.16,0.20,0.24,0.28]:
        for rec in [0.88,0.92,0.96]:
         for price in [30,45,60,75,90]:
          p=replace(base,h2_kwh_per_kg=eff,pressure_bar=pbar,nh3_conversion=conv,n2_recovery=rec,electricity_usd_mwh=price)
          e=energy(p); ec=economics(p); em=emissions(p,0.05)
          # Feasibility: realistic screening bounds and product target.
          feasible=(0.85<=rec<=0.98 and 80<=pbar<=220 and conv<=0.35)
          row={"h2_kwh_per_kg":eff,"pressure_bar":pbar,"conversion":conv,"n2_recovery":rec,"electricity_usd_mwh":price,"lcoa_usd_per_t":ec['lcoa_usd_per_t'],"specific_kwh_kg":e['specific_kwh_kg_nh3'],"renewable_kgco2_kg":em['kgco2_per_kg_nh3'],"feasible":feasible}
          rows.append(row)
          if feasible and (best is None or ec['lcoa_usd_per_t']<best[0]): best=(ec['lcoa_usd_per_t'],row)
    return best[1], rows
