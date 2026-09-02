# Deployment Guide

## Recommended deployment: Streamlit Community Cloud

This repository includes a root-level `app.py` and `requirements.txt`, which are the key pieces needed for a Streamlit Community Cloud deployment.

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

### 2. Deploy

1. Sign in to Streamlit Community Cloud with GitHub.
2. Choose **Create app**.
3. Select your GitHub repository and the `main` branch.
4. Set the main file path to `app.py`.
5. Deploy.
6. Wait for the build to complete and open the generated `streamlit.app` URL.

### 3. Verify the deployed app

Check all of the following:

- The dashboard opens without a Python traceback.
- Sidebar inputs can be changed.
- Scenario metrics update.
- The energy breakdown renders.
- The economics table renders.
- **Run optimization** completes.
- The best-design CSV download works.
- The app disclaimer remains visible.

### 4. Updating an existing deployment

Push changes to the same GitHub repository and branch. Streamlit Community Cloud watches the repository and updates the deployed app. Dependency changes in `requirements.txt` trigger dependency installation/redeployment.

### 5. Troubleshooting

**Build fails on dependencies**
- Check the deployment logs.
- Confirm `requirements.txt` is in the repository root.
- Avoid adding packages that are not imported by the app.
- Keep the Python version used locally aligned with the deployment environment.

**`ModuleNotFoundError: src`**
- Deploy from the repository root.
- Keep `src/__init__.py` in place.
- Keep `app.py` in the repository root.

**App opens but results fail**
- Run locally from the repository root:
  ```bash
  python -m pytest -q
  python -m src.run_all
  ```
- Then run:
  ```bash
  streamlit run app.py
  ```

**Optimization feels slow**
- The current deterministic grid is intentionally small and auditable.
- Do not replace it with an opaque optimizer without documenting the new search space and constraints.

## Local deployment smoke test

From the repository root:

```bash
python -m pytest -q
python -m src.run_all
streamlit run app.py
```

Open the local URL printed by Streamlit and exercise the sidebar and optimization button.

## Important limitation

The repository can be fully tested in a local Python environment, but a real Streamlit Community Cloud deployment requires access to your GitHub/Streamlit account. Do not claim the app is cloud-deployed until you have completed that final account-level step.
