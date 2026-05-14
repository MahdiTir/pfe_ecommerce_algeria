from __future__ import annotations

import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from pmdarima import auto_arima
from statsmodels.tsa.statespace.sarimax import SARIMAX


warnings.filterwarnings("ignore")

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT_DIR / "data" / "weekly_demand_categorie_region.csv"
MODELS_DIR = ROOT_DIR / "SARIMA" / "models"
RESIDUALS_PATH = ROOT_DIR / "SARIMA" / "sarima_residuals_train.csv"
FORECASTS_PATH = ROOT_DIR / "SARIMA" / "sarima_forecasts_all.csv"
ORDERS_PATH = ROOT_DIR / "SARIMA" / "sarima_orders.csv"

DATE_COL = "date"
CATEGORY_COL = "Categorie"
REGION_COL = "region"
DEMAND_COL = "demand"
SPLIT_COL = "split"

AUTO_ARIMA_CONFIG = {
	"start_p": 0,
	"max_p": 3,
	"start_q": 0,
	"max_q": 3,
	"d": None,
	"seasonal": True,
	"m": 52,
	"start_P": 0,
	"max_P": 2,
	"start_Q": 0,
	"max_Q": 2,
	"D": 1,
	"information_criterion": "aic",
	"stepwise": True,
	"suppress_warnings": True,
	"error_action": "ignore",
}


def _normalize_text(value: str) -> str:
	text = str(value).strip().lower()
	text = " ".join(text.split())
	return text


def _find_column(columns: list[str], target_normalized: str) -> str:
	for column in columns:
		if _normalize_text(column) == target_normalized:
			return column
	raise KeyError(f"Missing required column: {target_normalized}")


def _load_weekly_data() -> pd.DataFrame:
	df = pd.read_csv(DATA_PATH)
	columns = df.columns.tolist()

	date_col = _find_column(columns, "date expédition")
	category_col = _find_column(columns, "categorie")
	region_col = _find_column(columns, "region")
	demand_col = _find_column(columns, "demand")

	df = df.rename(
		columns={
			date_col: DATE_COL,
			category_col: CATEGORY_COL,
			region_col: REGION_COL,
			demand_col: DEMAND_COL,
		}
	)
	df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors="coerce")
	df[DEMAND_COL] = pd.to_numeric(df[DEMAND_COL], errors="coerce")
	df = df.dropna(subset=[DATE_COL, CATEGORY_COL, REGION_COL, DEMAND_COL]).copy()
	df = df.sort_values([CATEGORY_COL, REGION_COL, DATE_COL])
	return df


def _complete_weekly_series(df: pd.DataFrame, category: str, region: str) -> pd.Series:
	series = (
		df[(df[CATEGORY_COL] == category) & (df[REGION_COL] == region)]
		.groupby(DATE_COL, as_index=True)[DEMAND_COL]
		.sum()
		.sort_index()
	)
	if series.empty:
		return series

	full_index = pd.date_range(series.index.min(), series.index.max(), freq="W-MON")
	return series.reindex(full_index, fill_value=0).rename(series.name)


def split_series(series: pd.Series):
	n = len(series)
	train_end = int(n * 0.75)
	val_end = int(n * 0.875)
	return series.iloc[:train_end], series.iloc[train_end:val_end], series.iloc[val_end:]


def _forecast_series(model_fit, steps: int, index: pd.DatetimeIndex) -> pd.Series:
	forecast = model_fit.forecast(steps=steps)
	return pd.Series(np.asarray(forecast), index=index, name="sarima_forecast")


def _fit_one_series(df: pd.DataFrame, category: str, region: str):
	key = (category, region)
	file_key = f"{category}__{region}".replace(" ", "_")
	model_path = MODELS_DIR / f"sarima_{file_key}.pkl"

	series = _complete_weekly_series(df, category, region)
	if series.empty:
		print(f"  [SKIP]   {category} | {region} - no data")
		return key, None, pd.DataFrame(), pd.DataFrame(), None

	train, val, test = split_series(series)

	if len(train) < 8 or len(val) == 0 or len(test) == 0:
		print(f"  [SKIP]   {category} | {region} - insufficient split sizes ({len(train)}, {len(val)}, {len(test)})")
		return key, None, pd.DataFrame(), pd.DataFrame(), None

	if np.isclose(train.sum(), 0) and np.isclose(val.sum(), 0) and np.isclose(test.sum(), 0):
		print(f"  [SKIP]   {category} | {region} - all zero demand")
		return key, None, pd.DataFrame(), pd.DataFrame(), None

	try:
		order_model = auto_arima(train, **AUTO_ARIMA_CONFIG)
		order = order_model.order
		seasonal_order = order_model.seasonal_order

		train_fit = SARIMAX(
			train,
			order=order,
			seasonal_order=seasonal_order,
			enforce_stationarity=False,
			enforce_invertibility=False,
		)
		train_fit_result = train_fit.fit(disp=False)

		fitted_train = train_fit_result.get_prediction(start=0, end=len(train) - 1).predicted_mean
		fitted_train = pd.Series(fitted_train, index=train.index, name="fitted_train")
		residuals_train = (train - fitted_train).rename("residual")

		train_val = pd.concat([train, val])
		refit_model = SARIMAX(
			train_val,
			order=order,
			seasonal_order=seasonal_order,
			enforce_stationarity=False,
			enforce_invertibility=False,
		)
		refit_result = refit_model.fit(disp=False)
		joblib.dump(refit_result, model_path)

		forecast_val = _forecast_series(train_fit_result, len(val), val.index)
		forecast_test = _forecast_series(refit_result, len(test), test.index)

		residuals_df = pd.DataFrame(
			{
				"date": residuals_train.index,
				"Categorie": category,
				"region": region,
				"residual": residuals_train.values,
				"demand": train.values,
			}
		)

		forecast_df = pd.concat(
			[
				pd.DataFrame(
					{
						"date": val.index,
						"Categorie": category,
						"region": region,
						SPLIT_COL: "validation",
						"sarima_forecast": forecast_val.values,
						"actual_demand": val.values,
					}
				),
				pd.DataFrame(
					{
						"date": test.index,
						"Categorie": category,
						"region": region,
						SPLIT_COL: "test",
						"sarima_forecast": forecast_test.values,
						"actual_demand": test.values,
					}
				),
			],
			ignore_index=True,
		)

		result = {
			"model": refit_result,
			"order": (order, seasonal_order),
			"fitted_train": fitted_train,
			"residuals_train": residuals_train,
			"forecast_val": forecast_val,
			"forecast_test": forecast_test,
			"actual_train": train,
			"actual_val": val,
			"actual_test": test,
		}

		print(
			f"  [OK]     {category} | {region} - order={order}, seasonal={seasonal_order}, train={len(train)}, val={len(val)}, test={len(test)}"
		)
		return key, result, residuals_df, forecast_df, {
			"Categorie": category,
			"region": region,
			"order": str(order),
			"seasonal_order": str(seasonal_order),
			"aic": float(refit_result.aic),
		}

	except Exception as exc:
		print(f"  [ERROR]  {category} | {region} - {exc}")
		return key, None, pd.DataFrame(), pd.DataFrame(), None


def main() -> None:
	MODELS_DIR.mkdir(parents=True, exist_ok=True)

	df = _load_weekly_data()
	print(f"Loaded weekly demand data: {df.shape}")

	combos = (
		df[[CATEGORY_COL, REGION_COL]]
		.drop_duplicates()
		.sort_values([CATEGORY_COL, REGION_COL])
		.itertuples(index=False, name=None)
	)
	combos = list(combos)
	print(f"Fitting {len(combos)} SARIMA series ({df[CATEGORY_COL].nunique()} categories x {df[REGION_COL].nunique()} regions)...\n")

	results = joblib.Parallel(n_jobs=-1)(
		joblib.delayed(_fit_one_series)(df, category, region)
		for category, region in combos
	)

	sarima_results: dict[tuple[str, str], dict] = {}
	residual_frames: list[pd.DataFrame] = []
	forecast_frames: list[pd.DataFrame] = []
	orders: list[dict] = []

	for key, result, residuals_df, forecast_df, order_info in results:
		if result is not None:
			sarima_results[key] = result
		if not residuals_df.empty:
			residual_frames.append(residuals_df)
		if not forecast_df.empty:
			forecast_frames.append(forecast_df)
		if order_info is not None:
			orders.append(order_info)

	if residual_frames:
		residuals_all = pd.concat(residual_frames, ignore_index=True)
		residuals_all["date"] = pd.to_datetime(residuals_all["date"]).dt.strftime("%Y-%m-%d")
		residuals_all.to_csv(RESIDUALS_PATH, index=False)
		print(f"\nSaved training residuals to {RESIDUALS_PATH} ({residuals_all.shape})")
	else:
		print("\nWarning: no residuals were collected")

	if forecast_frames:
		forecasts_all = pd.concat(forecast_frames, ignore_index=True)
		forecasts_all["date"] = pd.to_datetime(forecasts_all["date"]).dt.strftime("%Y-%m-%d")
		forecasts_all.to_csv(FORECASTS_PATH, index=False)
		print(f"Saved SARIMA forecasts to {FORECASTS_PATH} ({forecasts_all.shape})")
	else:
		print("Warning: no forecasts were collected")

	if orders:
		pd.DataFrame(orders).to_csv(ORDERS_PATH, index=False)
		print(f"Saved SARIMA orders to {ORDERS_PATH}")

	print("\nPhase 2 summary:")
	print(f"✓ All series split into train/val/test: {len(sarima_results)} fitted series")
	print("✓ SARIMA fitted on all (Categorie × region) tuples")
	print("✓ Residuals extracted and saved")
	print("✓ Ready for XGBoost in Phase 3")


if __name__ == "__main__":
	main()