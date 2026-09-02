import os
import pandas as pd
import matplotlib.pyplot as plt
from .model import Params, streams, energy, economics, emissions, heat_balance
from .optimize import grid_optimize

def generate(out='results', fig='figures'):
    os.makedirs(out,exist_ok=True); os.makedirs(fig,exist_ok=True)
    p=Params(); s=streams(p); e=energy(p); ec=economics(p); emr=emissions(p); emg=emissions(p,0.05); hb=heat_balance(p)
    base={**s,**e,**ec,'grid_kgco2_kg':emr['kgco2_per_kg_nh3'],'renewable_kgco2_kg':emg['kgco2_per_kg_nh3'],**hb}
    pd.DataFrame([base]).to_csv(f'{out}/baseline_results.csv',index=False)
    best, rows=grid_optimize(p)
    pd.DataFrame(rows).to_csv(f'{out}/optimization_results.csv',index=False)
    pd.DataFrame([best]).to_csv(f'{out}/best_design.csv',index=False)
    sens=[]
    for price in [20,40,60,80,100,120]:
      pp=Params(electricity_usd_mwh=price); sens.append((price,economics(pp)['lcoa_usd_per_t']))
    sd=pd.DataFrame(sens,columns=['electricity_usd_mwh','lcoa_usd_per_t']); sd.to_csv(f'{out}/electricity_sensitivity.csv',index=False)
    plt.figure(); plt.plot(sd.electricity_usd_mwh,sd.lcoa_usd_per_t,marker='o'); plt.xlabel('Electricity price ($/MWh)'); plt.ylabel('LCOA ($/t NH3)'); plt.title('LCOA sensitivity to electricity price'); plt.tight_layout(); plt.savefig(f'{fig}/lcoa_electricity_sensitivity.png',dpi=180); plt.close()
    mix=pd.DataFrame({'category':['Electrolyzer','Compression','Synthesis heat'],'kWh_h':[e['electrolyzer_kwh_h'],e['compression_kwh_h'],e['synthesis_heat_kwh_h']]}); mix.to_csv(f'{out}/energy_breakdown.csv',index=False)
    plt.figure(); plt.bar(mix.category,mix.kWh_h); plt.ylabel('Energy rate (kWh/h)'); plt.title('Baseline electricity/utility breakdown'); plt.xticks(rotation=15); plt.tight_layout(); plt.savefig(f'{fig}/energy_breakdown.png',dpi=180); plt.close()
    return base,best
