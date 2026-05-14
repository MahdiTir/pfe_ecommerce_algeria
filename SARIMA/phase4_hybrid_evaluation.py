from __future__ import annotations

import pickle
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder


warnings.filterwarnings("ignore")

ROOT_DIR = Path(__file__).resolve().parents[1]
WEEKLY_DEMAND_PATH = ROOT_DIR / "data" / "weekly_demand_categorie_region.csv"
RESIDUALS_PATH = ROOT_DIR / "SARIMA" / "sarima_residuals_train.csv"
FORECASTS_PATH = ROOT_DIR / "SARIMA" / "sarima_forecasts_all.csv"
MODEL_PATH = ROOT_DIR / "SARIMA" / "xgb_residual_model.json"
FEATURE_COLUMNS_PATH = ROOT_DIR / "SARIMA" / "xgb_feature_columns.txt"
ENCODERS_PATH = ROOT_DIR / "SARIMA" / "label_encoders.pkl"

METRICS_ALL_PATH = ROOT_DIR / "SARIMA" / "metrics_all_series.csv"
METRICS_SUMMARY_PATH = ROOT_DIR / "SARIMA" / "metrics_summary.csv"
HYBRID_FORECASTS_PATH = ROOT_DIR / "SARIMA" / "hybrid_forecasts_all.csv"

DATE_COL = "date"
CATEGORY_COL = "Categorie"
REGION_COL = "region"
DEMAND_COL = "demand"
RESIDUAL_COL = "residual"
SPLIT_COL = "split"
SARIMA_FORECAST_COL = "sarima_forecast_val"
TARGET_COL = "target"
ACTUAL_COL = "actual"
HYBRID_COL = "hybrid_forecast"
XGB_CORRECTION_COL = "xgb_correction"

LAG_FEATURES = [1, 2, 3, 4, 8, 12, 26, 52]
ROLLING_FEATURES = [4, 12, 26]
EXPECTED_REGION_ORDER = ["EAST", "NORTH", "SOUTH", "WEST"]

RAMADAN_RANGES = [
	("2024-03-11", "2024-04-09"),
	("2025-03-01", "2025-03-29"),
]

EID_RANGES = [
	("2024-04-08", "2024-04-21"),
	("2024-06-10", "2024-06-23"),
	("2025-03-24", "2025-04-06"),
	("2025-06-02", "2025-06-15"),
]


def _normalize_text(value: str) -> str:
	import unicodedata
	text = str(value).strip().lower()
	text = unicodedata.normalize('NFKD', text)
	text = ''.join([c for c in text if not unicodedata.combining(c)])
	return " ".join(text.split())


def _find_column(columns: list[str], target_normalized: str) -> str:
	for column in columns:
		if target_normalized in _normalize_text(column):
			return column
	raise KeyError(f"Missing required column: {target_normalized}")


def _load_feature_columns() -> list[str]:
	return [line.strip() for line in FEATURE_COLUMNS_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]


def _load_encoders() -> dict[str, LabelEncoder]:
	with open(ENCODERS_PATH, "rb") as handle:
		return pickle.load(handle)


def _load_weekly_demand() -> pd.DataFrame:
	df = pd.read_csv(WEEKLY_DEMAND_PATH)
	columns = df.columns.tolist()
	date_col = _find_column(columns, "date expedition")
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


def _load_train_residuals() -> pd.DataFrame:
	df = pd.read_csv(RESIDUALS_PATH)
	df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors="coerce")
	df[RESIDUAL_COL] = pd.to_numeric(df[RESIDUAL_COL], errors="coerce")
	df[DEMAND_COL] = pd.to_numeric(df[DEMAND_COL], errors="coerce")
	df = df.dropna(subset=[DATE_COL, CATEGORY_COL, REGION_COL, RESIDUAL_COL, DEMAND_COL]).copy()
	df[SPLIT_COL] = "train"
	df[SARIMA_FORECAST_COL] = df[DEMAND_COL] - df[RESIDUAL_COL]
	df[TARGET_COL] = df[RESIDUAL_COL]
	df[ACTUAL_COL] = df[DEMAND_COL]
	return df[[DATE_COL, CATEGORY_COL, REGION_COL, SPLIT_COL, ACTUAL_COL, SARIMA_FORECAST_COL, TARGET_COL]]


def _load_forecasts() -> pd.DataFrame:
	df = pd.read_csv(FORECASTS_PATH)
	df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors="coerce")
	df["sarima_forecast"] = pd.to_numeric(df["sarima_forecast"], errors="coerce")
	df["actual_demand"] = pd.to_numeric(df["actual_demand"], errors="coerce")
	df = df.dropna(subset=[DATE_COL, CATEGORY_COL, REGION_COL, SPLIT_COL, "sarima_forecast", "actual_demand"]).copy()
	df = df.rename(columns={"sarima_forecast": SARIMA_FORECAST_COL, "actual_demand": ACTUAL_COL})
	df[TARGET_COL] = df[ACTUAL_COL] - df[SARIMA_FORECAST_COL]
	return df[[DATE_COL, CATEGORY_COL, REGION_COL, SPLIT_COL, ACTUAL_COL, SARIMA_FORECAST_COL, TARGET_COL]]


def _build_master_frame() -> pd.DataFrame:
	weekly = _load_weekly_demand()
	train_residuals = _load_train_residuals()
	forecasts = _load_forecasts()
	combined = pd.concat([train_residuals, forecasts], ignore_index=True)
	combined = combined.drop_duplicates(subset=[DATE_COL, CATEGORY_COL, REGION_COL, SPLIT_COL], keep="first")
	master = weekly.merge(combined, on=[DATE_COL, CATEGORY_COL, REGION_COL], how="left", suffixes=("", "_target"))
	master[ACTUAL_COL] = master[ACTUAL_COL].fillna(master[DEMAND_COL])
	master[SARIMA_FORECAST_COL] = master[SARIMA_FORECAST_COL].fillna(0)
	master[TARGET_COL] = master[TARGET_COL].fillna(master[ACTUAL_COL] - master[SARIMA_FORECAST_COL])
	master[SPLIT_COL] = master[SPLIT_COL].fillna("unknown")
	master = master[[DATE_COL, CATEGORY_COL, REGION_COL, SPLIT_COL, ACTUAL_COL, SARIMA_FORECAST_COL, TARGET_COL]]
	master = master.sort_values([CATEGORY_COL, REGION_COL, DATE_COL]).reset_index(drop=True)
	return master


def _flag_date_ranges(dates: pd.Series, ranges: list[tuple[str, str]]) -> pd.Series:
	mask = pd.Series(False, index=dates.index)
	for start_text, end_text in ranges:
		start = pd.Timestamp(start_text)
		end = pd.Timestamp(end_text)
		mask |= dates.between(start, end, inclusive="both")
	return mask.astype(int)


def _complete_weekly_history(weekly: pd.DataFrame) -> pd.DataFrame:
	frames = []
	for (category, region), group in weekly.groupby([CATEGORY_COL, REGION_COL], sort=False):
		ordered = group.sort_values(DATE_COL).set_index(DATE_COL)
		full_index = pd.date_range(ordered.index.min(), ordered.index.max(), freq="W-MON")
		reindexed = ordered.reindex(full_index)
		reindexed.index.name = DATE_COL
		reindexed = reindexed.reset_index()
		reindexed[CATEGORY_COL] = category
		reindexed[REGION_COL] = region
		reindexed[DEMAND_COL] = reindexed[DEMAND_COL].fillna(0)
		frames.append(reindexed[[DATE_COL, CATEGORY_COL, REGION_COL, DEMAND_COL]])
	return pd.concat(frames, ignore_index=True)


def _engineer_features(master: pd.DataFrame, feature_cols: list[str], encoders: dict[str, LabelEncoder]) -> pd.DataFrame:
	weekly = _complete_weekly_history(_load_weekly_demand())
	master = master.merge(weekly, on=[DATE_COL, CATEGORY_COL, REGION_COL], how="left", suffixes=("", "_weekly"))
	master[DEMAND_COL] = master[DEMAND_COL].fillna(0)

	category_encoder = encoders["Categorie"]
	region_encoder = encoders["region"]
	master["categorie_encoded"] = category_encoder.transform(master[CATEGORY_COL].astype(str))
	master["region_encoded"] = region_encoder.transform(master[REGION_COL].astype(str))
	master["categorie_region_id"] = pd.factorize(
		master[CATEGORY_COL].astype(str) + "__" + master[REGION_COL].astype(str), sort=True
	)[0]

	train_mask = master[SPLIT_COL] == "train"
	train_stats = master.loc[train_mask, [CATEGORY_COL, REGION_COL, DEMAND_COL]].copy()
	region_mean_map = train_stats.groupby(REGION_COL)[DEMAND_COL].mean().to_dict()
	category_mean_map = train_stats.groupby(CATEGORY_COL)[DEMAND_COL].mean().to_dict()
	master["demand_per_region"] = master[REGION_COL].map(region_mean_map)
	master["demand_per_categorie"] = master[CATEGORY_COL].map(category_mean_map)

	grouped = master.groupby([CATEGORY_COL, REGION_COL], sort=False)[DEMAND_COL]
	for lag in LAG_FEATURES:
		master[f"lag_{lag}"] = grouped.transform(lambda series, lag=lag: series.shift(lag))

	for window in ROLLING_FEATURES:
		master[f"rolling_mean_{window}"] = (
			master.groupby([CATEGORY_COL, REGION_COL], sort=False)[DEMAND_COL]
			.transform(lambda series, window=window: series.shift(1).rolling(window=window).mean())
		)
		if window in (4, 12):
			master[f"rolling_std_{window}"] = (
				master.groupby([CATEGORY_COL, REGION_COL], sort=False)[DEMAND_COL]
				.transform(lambda series, window=window: series.shift(1).rolling(window=window).std())
			)

	master["week_of_year"] = master[DATE_COL].dt.isocalendar().week.astype(int).clip(upper=52)
	master["month"] = master[DATE_COL].dt.month.astype(int)
	master["quarter"] = master[DATE_COL].dt.quarter.astype(int)
	master["is_ramadan"] = _flag_date_ranges(master[DATE_COL], RAMADAN_RANGES)
	master["is_summer"] = master[DATE_COL].dt.month.isin([7, 8]).astype(int)
	master["is_eid"] = _flag_date_ranges(master[DATE_COL], EID_RANGES)

	region_dummies = pd.get_dummies(master[REGION_COL], prefix="region", drop_first=True)
	for expected_column in ["region_NORTH", "region_SOUTH", "region_WEST"]:
		if expected_column not in region_dummies.columns:
			region_dummies[expected_column] = 0
	region_dummies = region_dummies[["region_NORTH", "region_SOUTH", "region_WEST"]]
	master = pd.concat([master, region_dummies], axis=1)

	feature_frame = master.dropna(subset=feature_cols + [TARGET_COL]).copy()
	return feature_frame


def _series_metrics(actual: pd.Series, forecast: pd.Series, train_series: pd.Series) -> dict[str, float]:
	actual = pd.Series(actual).astype(float)
	forecast = pd.Series(forecast).astype(float)
	residual = actual - forecast
	mae = float(mean_absolute_error(actual, forecast))
	rmse = float(np.sqrt(mean_squared_error(actual, forecast)))
	mask_nonzero = actual != 0
	mape = float(np.mean(np.abs((actual[mask_nonzero] - forecast[mask_nonzero]) / actual[mask_nonzero])) * 100) if mask_nonzero.any() else np.nan
	smape_den = np.abs(actual) + np.abs(forecast)
	smape = float(np.mean(np.where(smape_den != 0, 200 * np.abs(actual - forecast) / smape_den, np.nan)))
	train_naive = np.abs(train_series.diff().dropna())
	mase_den = float(train_naive.mean()) if not train_naive.empty else np.nan
	mase = float(mae / mase_den) if mase_den and not np.isnan(mase_den) and mase_den != 0 else np.nan
	r2 = float(r2_score(actual, forecast)) if len(actual) > 1 else np.nan
	return {
		"MAE": mae,
		"RMSE": rmse,
		"MAPE": mape,
		"SMAPE": smape,
		"MASE": mase,
		"R2": r2,
	}


def _format_mean_std(series: pd.Series) -> str:
	series = pd.to_numeric(series, errors="coerce")
	return f"{series.mean():.4f} ± {series.std(ddof=0):.4f}"


def main() -> None:
	print("Loading Phase 4 artifacts...")
	feature_cols = _load_feature_columns()
	encoders = _load_encoders()
	booster = xgb.Booster()
	booster.load_model(MODEL_PATH)
	print(f"Loaded {len(feature_cols)} feature columns and XGBoost model")

	master = _build_master_frame()
	engineered = _engineer_features(master, feature_cols, encoders)
	engineered = engineered[engineered[SPLIT_COL].isin(["train", "validation", "test"])].copy()
	engineered = engineered.sort_values([CATEGORY_COL, REGION_COL, DATE_COL]).reset_index(drop=True)
	print(f"Engineered feature frame: {engineered.shape}")

	X_all = engineered[feature_cols]
	dmatrix = xgb.DMatrix(X_all, feature_names=feature_cols)
	xgb_residual_preds = booster.predict(dmatrix)
	engineered[XGB_CORRECTION_COL] = xgb_residual_preds
	engineered[HYBRID_COL] = engineered[SARIMA_FORECAST_COL] + engineered[XGB_CORRECTION_COL]
	engineered["sarima_only_forecast"] = engineered[SARIMA_FORECAST_COL]

	forecast_rows = engineered[engineered[SPLIT_COL].isin(["validation", "test"])][
		[DATE_COL, CATEGORY_COL, REGION_COL, SPLIT_COL, ACTUAL_COL, SARIMA_FORECAST_COL, XGB_CORRECTION_COL, HYBRID_COL]
	].copy()
	forecast_rows.to_csv(HYBRID_FORECASTS_PATH, index=False)

	metrics_rows: list[dict] = []
	for (category, region), group in engineered.groupby([CATEGORY_COL, REGION_COL], sort=False):
		train_series = group.loc[group[SPLIT_COL] == "train", ACTUAL_COL]
		for split in ["validation", "test"]:
			split_frame = group[group[SPLIT_COL] == split].copy()
			if split_frame.empty:
				continue
			actual = split_frame[ACTUAL_COL]
			sarima_forecast = split_frame[SARIMA_FORECAST_COL]
			hybrid_forecast = split_frame[HYBRID_COL]
			sarima_metrics = _series_metrics(actual, sarima_forecast, train_series)
			hybrid_metrics = _series_metrics(actual, hybrid_forecast, train_series)
			metrics_rows.append({"Categorie": category, "region": region, "split": split, "model": "SARIMA", **sarima_metrics})
			metrics_rows.append({"Categorie": category, "region": region, "split": split, "model": "Hybrid", **hybrid_metrics})

	metrics_df = pd.DataFrame(metrics_rows)
	metrics_df.to_csv(METRICS_ALL_PATH, index=False)

	overall_summary = (
		metrics_df.groupby(["model", "split"])[["MAE", "RMSE", "MAPE", "SMAPE", "MASE", "R2"]]
		.agg(["mean", "std"])
	)
	flat_summary = overall_summary.copy()
	flat_summary.columns = [f"{metric}_{stat}" for metric, stat in flat_summary.columns]
	flat_summary = flat_summary.reset_index()
	flat_summary.to_csv(METRICS_SUMMARY_PATH, index=False)

	print("\nOverall summary (mean ± std):")
	for _, row in flat_summary.iterrows():
		print(f"{row['model']} {row['split']}")
		for metric in ["MAE", "RMSE", "MAPE", "SMAPE", "MASE", "R2"]:
			print(f"  {metric}: {row[f'{metric}_mean']:.4f} ± {row[f'{metric}_std']:.4f}")

	print("\nPer-region summary (mean metrics):")
	region_summary = (
		metrics_df.groupby(["region", "model", "split"])[["MAE", "RMSE", "MAPE", "SMAPE", "MASE", "R2"]].mean().reset_index()
	)
	print(region_summary.to_string(index=False))

	print("\nPer-category summary (test split mean metrics):")
	category_summary = (
		metrics_df[metrics_df["split"] == "test"]
		.groupby(["Categorie", "model"])[["MAE", "RMSE", "MAPE", "SMAPE", "MASE", "R2"]]
		.mean()
		.reset_index()
	)
	print(category_summary.to_string(index=False))

	test_metrics = metrics_df[metrics_df["split"] == "test"].copy()
	test_wide = test_metrics.pivot_table(index=["Categorie", "region"], columns="model", values="RMSE").reset_index()
	test_wide["rmse_improvement"] = (test_wide["SARIMA"] - test_wide["Hybrid"]) / test_wide["SARIMA"] * 100
	positive_rate = float((test_wide["rmse_improvement"] > 0).mean() * 100)
	print(f"\nHybrid outperforms SARIMA on {positive_rate:.2f}% of series (test RMSE improvement > 0)")
	print("\nTop 5 most improved series:")
	print(test_wide.sort_values("rmse_improvement", ascending=False).head(5).to_string(index=False))
	print("\nTop 5 where SARIMA was better:")
	print(test_wide.sort_values("rmse_improvement", ascending=True).head(5).to_string(index=False))

	print("\nPhase 4 summary:")
	print("✓ Hybrid forecasts generated for all series")
	print("✓ All 6 metrics computed for SARIMA and Hybrid")
	print("✓ Improvement analysis printed")
	print("✓ All outputs saved, ready for Phase 5")


if __name__ == "__main__":
	main()
