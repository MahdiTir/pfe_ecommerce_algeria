Hybrid SARIMA + XGBoost Forecasting Pipeline — Documentation

Overview
-	Purpose: A 5-phase weekly forecasting pipeline for Algeria e-commerce demand (2024–2025) combining per-series SARIMA models + a global XGBoost residual-correction model.
-	Workspace: e:/Projects/pfe_ecommerce_algeria
-	Python: 3.12 (use the project's virtualenv `.venv`)

Prerequisites
-	Activate the virtualenv:
```
# Windows PowerShell
& .venv\Scripts\Activate.ps1
```
-	Install dependencies (recommended):
```
python -m pip install -r requirements.txt
```
(If `xgboost` fails to install quickly, allow extra time for large wheels.)

Project files (key)
- Data:
  - [data/weekly_demand_categorie_region.csv](data/weekly_demand_categorie_region.csv)
  - [data/weekly_demand_produit_region.csv](data/weekly_demand_produit_region.csv) (optional)
- SARIMA phase:
  - [SARIMA/sarima_by_category_region.py](SARIMA/sarima_by_category_region.py) — fits SARIMA per series
  - [SARIMA/models/](SARIMA/models/) — saved `sarima_*.pkl` per series
  - Outputs: [SARIMA/sarima_residuals_train.csv](SARIMA/sarima_residuals_train.csv), [SARIMA/sarima_forecasts_all.csv](SARIMA/sarima_forecasts_all.csv), [SARIMA/sarima_orders.csv](SARIMA/sarima_orders.csv)
- XGBoost training (Phase 3):
  - [SARIMA/xgb_residual_training.py](SARIMA/xgb_residual_training.py)
  - Outputs: [SARIMA/xgb_residual_model.json](SARIMA/xgb_residual_model.json), [SARIMA/label_encoders.pkl](SARIMA/label_encoders.pkl), [SARIMA/xgb_feature_columns.txt](SARIMA/xgb_feature_columns.txt), [SARIMA/xgb_feature_importance.png](SARIMA/xgb_feature_importance.png)
- Hybrid evaluation (Phase 4):
  - [SARIMA/phase4_hybrid_evaluation.py](SARIMA/phase4_hybrid_evaluation.py)
  - Outputs: [SARIMA/hybrid_forecasts_all.csv](SARIMA/hybrid_forecasts_all.csv), [SARIMA/metrics_all_series.csv](SARIMA/metrics_all_series.csv), [SARIMA/metrics_summary.csv](SARIMA/metrics_summary.csv)
- Visualizations & Forecasting (Phase 5):
  - [SARIMA/phase5_visualization_forecasting.py](SARIMA/phase5_visualization_forecasting.py)
  - Outputs: [SARIMA/forecast_plots_top6.png](SARIMA/forecast_plots_top6.png), [SARIMA/metrics_comparison_by_region.png](SARIMA/metrics_comparison_by_region.png), [SARIMA/improvement_heatmap.png](SARIMA/improvement_heatmap.png), [SARIMA/residual_correction_fit.png](SARIMA/residual_correction_fit.png), [SARIMA/future_forecast_Q1_2026.csv](SARIMA/future_forecast_Q1_2026.csv)

Phase-by-phase instructions

Phase 1 — Preprocessing
- Script: [SARIMA/pre-processing.py](SARIMA/pre-processing.py)
- Purpose: Load raw orders CSV, map wilayas → regions, aggregate weekly demand by `Categorie` × `region`.
- Run:
```
python SARIMA/pre-processing.py
```
- Produces `data/weekly_demand_categorie_region.csv` and `data/weekly_demand_produit_region.csv`.

Phase 2 — SARIMA fitting
- Script: [SARIMA/sarima_by_category_region.py](SARIMA/sarima_by_category_region.py)
- Purpose: Fit individual SARIMA models for each `Categorie` × `region` series, save residuals and per-series model PKLs.
- Run:
```
python SARIMA/sarima_by_category_region.py
```
- Outputs: `SARIMA/models/sarima_*.pkl`, `SARIMA/sarima_residuals_train.csv`, `SARIMA/sarima_forecasts_all.csv`, `SARIMA/sarima_orders.csv`.

Phase 3 — XGBoost residual training
- Script: [SARIMA/xgb_residual_training.py](SARIMA/xgb_residual_training.py)
- Purpose: Build 32-feature matrix (lags, rolling stats, calendar flags, SARIMA forecast, label encodings), train a global XGBRegressor (with early stopping) on SARIMA residuals.
- Run:
```
python SARIMA/xgb_residual_training.py
```
- Outputs (saved to `SARIMA/`): `xgb_residual_model.json`, `label_encoders.pkl`, `xgb_feature_columns.txt`, `xgb_feature_importance.png`.

Phase 4 — Hybrid evaluation
- Script: [SARIMA/phase4_hybrid_evaluation.py](SARIMA/phase4_hybrid_evaluation.py)
- Purpose: Load XGBoost model and encoders, apply to features for validation+test splits, compute per-series and aggregated metrics, export hybrid forecasts.
- Run:
```
python SARIMA/phase4_hybrid_evaluation.py
```
- Outputs: `SARIMA/hybrid_forecasts_all.csv`, `SARIMA/metrics_all_series.csv`, `SARIMA/metrics_summary.csv`.

Phase 5 — Visualization, interpretation & future forecasting
- Script: [SARIMA/phase5_visualization_forecasting.py](SARIMA/phase5_visualization_forecasting.py)
- Purpose: Produce publication-ready plots, heatmap of improvements, residual vs predicted correction plots, and forecast next 12 weeks (Q1 2026) for all series using SARIMA models + XGBoost corrections.
- Run:
```
python SARIMA/phase5_visualization_forecasting.py
```
- Outputs: `forecast_plots_top6.png`, `metrics_comparison_by_region.png`, `improvement_heatmap.png`, `residual_correction_fit.png`, `future_forecast_Q1_2026.csv`.

Result analysis summary (executed run)
- Dataset: ~220,000 orders (2024–2025)
- Series: 88 `Categorie × region` series
- Phase 4 test summary (aggregated):
  - SARIMA mean RMSE ≈ 6.414
  - Hybrid mean RMSE ≈ 7.050
  - Hybrid improved RMSE on ~38.64% of series
  - Best region (by RMSE improvement): SOUTH
  - Best category (by RMSE improvement): Vêtements et accessoires
- Notes: Hybrid model reduces error for some series but increases it for others—per-category behavior is varied; consult `SARIMA/metrics_all_series.csv` for per-series metrics.

Notes, caveats, and troubleshooting
- Environment: Ensure you run all commands inside the project virtualenv used during development.
- Package installs: `xgboost` and `scipy` wheels are large on Windows—expect longer installs.
- Column names: Weekly CSV uses `date expédition` (accented); scripts include normalization to tolerate accents and variations.
- If you need reproducibility: set deterministic seeds in XGBoost params and save model artifacts; `xgb_residual_model.json` is saved.

Quick check commands
- List artifacts:
```
ls SARIMA | e.g. PowerShell: Get-ChildItem SARIMA\
```
- View top hybrid forecasts:
```
python -c "import pandas as pd; print(pd.read_csv('SARIMA/hybrid_forecasts_all.csv').head())"
```

Next steps & options
- Fine-tune XGBoost per-category (train separate models) to capture category-specific residual structure.
- Add more calendar features (holidays, promotions) to improve XGB corrections.
- Produce interactive dashboards (Plotly, Dash) for stakeholder exploration.

If you'd like, I can:
- Commit this documentation into the repo and open a PR.
- Tweak any plot aesthetics or regenerate figures at different resolutions.
- Add a `README.md` summary or a short Jupyter notebook demonstrating the pipeline end-to-end.
