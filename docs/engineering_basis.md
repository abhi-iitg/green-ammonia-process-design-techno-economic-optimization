# Engineering basis

## Reaction basis
Haber–Bosch synthesis: N2 + 3H2 ⇌ 2NH3.

## Material balance
The model first determines the required NH3 product flow, then accounts for product recovery and single-pass conversion to determine synthesis-feed H2 and N2. Nitrogen feed is increased by the specified N2 recovery.

## Electrolysis
The H2 electricity demand is modeled as a user-controlled specific consumption in kWh/kg H2. This is deliberately transparent and easy to sensitivity-test rather than pretending to represent a particular PEM stack's detailed polarization curve.

## Energy
Total utility requirement includes electrolyzer electricity, compression electricity and a synthesis heat allowance. The electrolyzer contribution should dominate the baseline, consistent with published e-ammonia system studies.

## Economics
LCOA includes annual electricity, fixed OPEX, variable OPEX and annualized CAPEX using a standard capital-recovery factor. Values are screening assumptions, not vendor quotations.

## Environmental metric
CO2 intensity is calculated from electricity consumption multiplied by a user-specified electricity carbon factor. Scope is cradle-to-gate electricity-related emissions only; embodied equipment and upstream materials are excluded.

## Optimization
The grid search minimizes screening LCOA over electrolyzer consumption, synthesis pressure, conversion, N2 recovery and electricity price. It is intentionally auditable and deterministic.
