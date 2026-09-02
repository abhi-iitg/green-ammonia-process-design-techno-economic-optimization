# Aspen Plus validation workflow

## Objective
Validate the transparent Python screening model with a genuine Aspen Plus steady-state flowsheet. Do **not** claim Aspen results until this workflow has been executed in IITG Aspen Plus.

## Recommended flowsheet
AIR/N2 FEED → N2 conditioning/compression ┐
                                          ├→ MIX → COMP → HB-REACTOR → COOLER → FLASH → NH3 PRODUCT
H2 FROM ELECTROLYZER → compression ──────┘                    ↑             └→ recycle/purge

For the first validation pass, use external H2 and N2 feeds. Then replace N2 with an ASU/PSA model and H2 with an electrolyzer representation if your Aspen license/database supports the desired unit operations.

## Property method
Use **Peng–Robinson / PR-BM** as the initial screening property method for the gas-rich synthesis loop; compare with another suitable method if liquid NH3 phase behavior or high-pressure VLE requires it.

## Components
H2, N2, NH3, H2O. Add inert species (e.g. Ar) only if explicitly modeled.

## Reaction
N2 + 3 H2 ⇌ 2 NH3.

For a first validation, use RGibbs to evaluate equilibrium tendency. For a design-oriented model, use an RPlug/RStoic formulation with a literature-supported conversion/kinetic basis and document the catalyst assumptions.

## Design specs
1. Set H2:N2 molar feed ratio to 3.0.
2. Set synthesis pressure according to the scenario (baseline 150 bar).
3. Adjust recycle/purge to control inert accumulation if inerts are included.
4. Condense NH3 and recycle unreacted H2/N2.
5. Verify NH3 product recovery and mass balance.

## Validation table
Export Aspen stream results and compare:

- NH3 product kg/h
- H2 feed kg/h
- N2 feed kg/h
- NH3 synthesis rate
- recycle rate
- compressor duty
- reactor duty
- condenser duty
- product purity

The Python model is a screening reference; differences are expected because Aspen uses rigorous thermodynamics and a different reactor model.

## What to screenshot for GitHub
1. Aspen flowsheet.
2. Property method setup.
3. Reactor block and reaction setup.
4. Converged stream table.
5. Energy summary.
6. Design Spec/Recycle convergence.

Place screenshots under `aspen/screenshots/` only after running the actual IITG Aspen model.
