from .model import Params, validate
from .report import generate
if __name__=='__main__':
    validate(Params()); base,best=generate();
    print('Baseline LCOA $/t:', round(base['lcoa_usd_per_t'],2))
    print('Specific energy kWh/kg NH3:', round(base['specific_kwh_kg_nh3'],2))
    print('Renewable kgCO2/kg NH3:', round(base['renewable_kgco2_kg'],3))
    print('Best grid point:', best)
