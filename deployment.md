# Deployment Guide

## Recommended deployment: Streamlit Community Cloud

This repository includes a root-level `app.py`, `requirements.txt` and `.streamlit/config.toml` for Streamlit deployment.

### 1. Push the project to GitHub

Keep the repository structure intact:

```text
green-ammonia-process-design/
├── app.py
├── requirements.txt
├── .streamlit/config.toml
├── src/
├── tests/
├── results/
├── figures/
├── docs/
└── aspen/
```

### 2. Test locally before deployment

From the repository root:

```bash
python -m pytest -q
python -m src.run_all
streamlit run app.py
```

The current test suite should report **20 passed**.

Open the local Streamlit URL and verify:

- Sidebar inputs change successfully.
- Changing **Display currency** changes the LCOA currency symbol/unit.
- The economics table headers change from, for example, `USD/year` and `USD/t NH₃` to `INR/year` and `INR/t NH₃` when INR is selected.
- Changing the FX rate updates displayed economic values and the user-facing electricity price conversion.
- Changing the energy display from `kWh/h` to `MWh/h` or `GWh/y` changes both the energy chart and its table units.
- Changing mass-flow units updates material-balance values and production-rate display.
- Specific energy remains normalized as `kWh/kg NH₃` because that is the model's reporting basis.
- The electricity carbon-factor control changes the CO₂-intensity result.
- The optimization button completes and the displayed economic fields use the selected currency.
- The best-design CSV downloads successfully.
- No red Streamlit exception appears.

### 3. Deploy

1. Sign in to Streamlit Community Cloud with GitHub.
2. Choose **Create app**.
3. Select this GitHub repository.
4. Select the `main` branch.
5. Set the main file path to:

```text
app.py
```

6. Use a supported Python version aligned with the local environment.
7. Deploy.
8. Wait for the build to finish and open the generated `streamlit.app` URL.

### 4. Verify the deployed app

Run this short acceptance checklist on the live URL:

#### A. Baseline

- Dashboard opens without traceback.
- Baseline LCOA is approximately `$1,025/t NH₃` with the default USD/FX settings.
- Energy breakdown shows electrolyzer, compression and synthesis-heat components.

#### B. Currency conversion

Select `INR` and confirm that:

- LCOA is shown as `₹.../t NH₃`.
- Economics headers show `INR/year` and `INR/t NH₃`.
- Electricity price is labeled `INR/MWh`.
- The displayed values change consistently.

Return to USD and confirm the original USD display is restored.

#### C. Energy conversion

Select `MWh/h` and confirm:

- Energy chart values are approximately 1/1000 of the kWh/h values.
- The chart/table unit says `MWh/h`.

Select `GWh/y` and confirm the values are annualized using the selected operating hours.

#### D. Scenario behavior

Change production target, electrolyzer efficiency, conversion, recovery and carbon factor. Confirm the results respond without errors.

#### E. Optimization

Click **Run optimization** and verify the table and CSV download complete.

### 5. Updating an existing deployment

Push changes to the same GitHub repository and branch. Streamlit Community Cloud can rebuild the app from the updated repository.

Example:

```bash
git add .
git commit -m "Fix dashboard currency and unit conversion"
git push
```

### 6. Existing GitHub repository

If the older version is already uploaded, do not recreate the repository.

**Replace:**

```text
README.md
app.py
requirements.txt
.gitignore
docs/deployment.md
```

**Add:**

```text
src/display.py
tests/test_display.py
```

Keep the existing engineering model and results files unless you intentionally want to regenerate them.

### 7. Troubleshooting

**Build fails on dependencies**

- Check Streamlit deployment logs.
- Confirm `requirements.txt` is in the repository root.
- Keep dependencies limited to packages actually used by the application.
- Use a supported Python version.

**`ModuleNotFoundError: src`**

- Deploy from the repository root.
- Keep `src/__init__.py` in place.
- Keep `app.py` in the repository root.

**Unit/currency display appears stale**

- Confirm you are running the updated `app.py` and `src/display.py`.
- Refresh the Streamlit app.
- Verify the selected unit appears in the chart/table heading as well as the values.

**App opens but calculations fail**

Run locally:

```bash
python -m pytest -q
python -m src.run_all
streamlit run app.py
```

**Optimization feels slow**

The deterministic grid is intentionally small and auditable. Do not replace it with an opaque optimizer without documenting the new search space and constraints.

## Important limitation

The repository can be tested locally, but a real Streamlit Community Cloud deployment requires access to the user's GitHub/Streamlit account. Do not claim the app is cloud-deployed until that account-level step has been completed.

## Currency-data limitation

The dashboard does **not** call a live foreign-exchange API. Each currency has a transparent default display rate, and the user can edit the FX rate in the sidebar. This keeps the deployed application deterministic and avoids external API credentials. The engineering model remains internally denominated in USD.
