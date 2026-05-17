SARIMAX + XGBoost Hybrid Pipeline

Overview
- Weekly demand forecasting by region and category group.
- SARIMAX with explicit seasonal exogenous regressors.
- XGBoost residual correction with strict time split.

How to run
1) Activate the virtual environment

Windows PowerShell:
python SARIMA/sarimax_x/pipeline.py --input data/ecommerce_algerie_2024_2025_version16mai.csv

Outputs
- SARIMAX orders, predictions, and residuals
- XGBoost model and feature importance
- Hybrid forecasts and evaluation metrics
- Plots (series, global, feature importance, R2 heatmaps)

All outputs are saved under SARIMA/sarimax_x/outputs and SARIMA/sarimax_x/plots.
