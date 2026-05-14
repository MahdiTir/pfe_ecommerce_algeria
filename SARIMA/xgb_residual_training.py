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
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import LabelEncoder


warnings.filterwarnings("ignore")

ROOT_DIR = Path(__file__).resolve().parents[1]
WEEKLY_DEMAND_PATH = ROOT_DIR / "data" / "weekly_demand_categorie_region.csv"
RESIDUALS_PATH = ROOT_DIR / "SARIMA" / "sarima_residuals_train.csv"
FORECASTS_PATH = ROOT_DIR / "SARIMA" / "sarima_forecasts_all.csv"

MODEL_PATH = ROOT_DIR / "SARIMA" / "xgb_residual_model.json"
FEATURE_IMPORTANCE_PATH = ROOT_DIR / "SARIMA" / "xgb_feature_importance.png"
FEATURE_COLUMNS_PATH = ROOT_DIR / "SARIMA" / "xgb_feature_columns.txt"
ENCODERS_PATH = ROOT_DIR / "SARIMA" / "label_encoders.pkl"

DATE_COL = "date"
CATEGORY_COL = "Categorie"
REGION_COL = "region"
DEMAND_COL = "demand"
RESIDUAL_COL = "residual"
SPLIT_COL = "split"
SARIMA_FORECAST_COL = "sarima_forecast_val"
TARGET_COL = "target"

LAG_FEATURES = [1, 2, 3, 4, 8, 12, 26, 52]
ROLLING_FEATURES = [4, 12, 26]

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
	# remove accents/diacritics
	text = unicodedata.normalize('NFKD', text)
	text = ''.join([c for c in text if not unicodedata.combining(c)])
	return " ".join(text.split())


def _find_column(columns: list[str], target_normalized: str) -> str:
	for column in columns:
		if target_normalized in _normalize_text(column):
			return column
	raise KeyError(f"Missing required column: {target_normalized}")


def _load_weekly_demand() -> pd.DataFrame:
	df = pd.read_csv(WEEKLY_DEMAND_PATH)
	columns = df.columns.tolist()
	date_col = _find_column(columns, "expedi")
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


def _load_residuals() -> pd.DataFrame:
	df = pd.read_csv(RESIDUALS_PATH)
	df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors="coerce")
	df[RESIDUAL_COL] = pd.to_numeric(df[RESIDUAL_COL], errors="coerce")
	df[DEMAND_COL] = pd.to_numeric(df[DEMAND_COL], errors="coerce")
	df = df.dropna(subset=[DATE_COL, CATEGORY_COL, REGION_COL, RESIDUAL_COL, DEMAND_COL]).copy()
	df[SPLIT_COL] = "train"
	df[SARIMA_FORECAST_COL] = df[DEMAND_COL] - df[RESIDUAL_COL]
	df[TARGET_COL] = df[RESIDUAL_COL]
	df["actual_demand"] = df[DEMAND_COL]
	return df[[DATE_COL, CATEGORY_COL, REGION_COL, SPLIT_COL, DEMAND_COL, SARIMA_FORECAST_COL, TARGET_COL, "actual_demand"]]


def _load_forecasts() -> pd.DataFrame:
	df = pd.read_csv(FORECASTS_PATH)
	df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors="coerce")
	df["sarima_forecast"] = pd.to_numeric(df["sarima_forecast"], errors="coerce")
	df["actual_demand"] = pd.to_numeric(df["actual_demand"], errors="coerce")
	df = df.dropna(subset=[DATE_COL, CATEGORY_COL, REGION_COL, SPLIT_COL, "sarima_forecast", "actual_demand"]).copy()
	df = df.rename(columns={"sarima_forecast": SARIMA_FORECAST_COL})
	df[TARGET_COL] = df["actual_demand"] - df[SARIMA_FORECAST_COL]
	df[DEMAND_COL] = df["actual_demand"]
	return df[[DATE_COL, CATEGORY_COL, REGION_COL, SPLIT_COL, DEMAND_COL, SARIMA_FORECAST_COL, TARGET_COL, "actual_demand"]]


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


def _build_master_frame() -> pd.DataFrame:
	weekly = _complete_weekly_history(_load_weekly_demand())
	residuals = _load_residuals()
	forecasts = _load_forecasts()
	combined = pd.concat([residuals, forecasts], ignore_index=True)
	combined = combined.drop_duplicates(subset=[DATE_COL, CATEGORY_COL, REGION_COL, SPLIT_COL], keep="first")
	master = weekly.merge(
		combined,
		on=[DATE_COL, CATEGORY_COL, REGION_COL],
		how="left",
		suffixes=("_weekly", "_target"),
	)
	weekly_col = f"{DEMAND_COL}_weekly"
	target_col = f"{DEMAND_COL}_target"
	master[DEMAND_COL] = master.get(weekly_col)
	if master[DEMAND_COL] is None:
		master[DEMAND_COL] = master.get(target_col).copy()
	else:
		master[DEMAND_COL] = master[DEMAND_COL].fillna(master.get(target_col)).fillna(0)
	master[SARIMA_FORECAST_COL] = master[SARIMA_FORECAST_COL].fillna(0)
	master[TARGET_COL] = master[TARGET_COL].fillna(0)
	master[SPLIT_COL] = master[SPLIT_COL].fillna("unknown")
	master["actual_demand"] = master["actual_demand"].fillna(master[DEMAND_COL])
	master = master[[DATE_COL, CATEGORY_COL, REGION_COL, SPLIT_COL, DEMAND_COL, SARIMA_FORECAST_COL, TARGET_COL, "actual_demand"]].copy()
	master = master.sort_values([CATEGORY_COL, REGION_COL, DATE_COL]).reset_index(drop=True)
	return master


def _flag_date_ranges(dates: pd.Series, ranges: list[tuple[str, str]]) -> pd.Series:
	mask = pd.Series(False, index=dates.index)
	for start_text, end_text in ranges:
		start = pd.Timestamp(start_text)
		end = pd.Timestamp(end_text)
		mask |= dates.between(start, end, inclusive="both")
	return mask.astype(int)


def _engineer_features(master: pd.DataFrame) -> tuple[pd.DataFrame, list[str], dict[str, LabelEncoder]]:
	master = master.copy()
	master = master.sort_values([CATEGORY_COL, REGION_COL, DATE_COL]).reset_index(drop=True)

	category_encoder = LabelEncoder()
	region_encoder = LabelEncoder()
	category_encoder.fit(master[CATEGORY_COL].astype(str))
	region_encoder.fit(master[REGION_COL].astype(str))
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

	required_feature_cols = [
		*(f"lag_{lag}" for lag in LAG_FEATURES),
		"rolling_mean_4",
		"rolling_std_4",
		"rolling_mean_12",
		"rolling_std_12",
		"rolling_mean_26",
		"week_of_year",
		"month",
		"quarter",
		"is_ramadan",
		"is_summer",
		"is_eid",
		SARIMA_FORECAST_COL,
		"categorie_encoded",
		"region_encoded",
		"region_NORTH",
		"region_SOUTH",
		"region_WEST",
		"categorie_region_id",
		"demand_per_region",
		"demand_per_categorie",
	]

	master = master.dropna(subset=required_feature_cols + [TARGET_COL]).copy()
	feature_cols = required_feature_cols
	encoders = {"Categorie": category_encoder, "region": region_encoder}
	return master, feature_cols, encoders


def _plot_feature_importance(model: object, feature_cols: list[str]) -> None:
	# accept either sklearn wrapper (XGBRegressor) or raw Booster
	if hasattr(model, "get_booster"):
		booster = model.get_booster()
	else:
		booster = model
	importance = booster.get_score(importance_type="gain")
	importance_df = pd.DataFrame(
		{
			"feature": feature_cols,
			"gain": [importance.get(feature, 0.0) for feature in feature_cols],
		}
	).sort_values("gain", ascending=False)
	top_features = importance_df.head(20)

	plt.figure(figsize=(12, 8))
	plt.barh(top_features["feature"].iloc[::-1], top_features["gain"].iloc[::-1], color="#0f766e")
	plt.title("Top 20 XGBoost Feature Importance by Gain")
	plt.xlabel("Gain")
	plt.tight_layout()
	plt.savefig(FEATURE_IMPORTANCE_PATH, dpi=200)
	plt.close()


def main() -> None:
	print("Loading SARIMA residuals, forecasts, and weekly demand...")
	master = _build_master_frame()
	print(f"Base feature frame before lag/rolling drop: {master.shape}")

	engineered, feature_cols, encoders = _engineer_features(master)
	print(f"Feature matrix after dropna: {engineered.shape}")
	print(f"Feature columns: {len(feature_cols)}")

	train_df = engineered[engineered[SPLIT_COL] == "train"].copy()
	val_df = engineered[engineered[SPLIT_COL] == "validation"].copy()
	test_df = engineered[engineered[SPLIT_COL] == "test"].copy()

	if train_df.empty or val_df.empty:
		raise RuntimeError("Train or validation split is empty after feature engineering.")

	X_train = train_df[feature_cols]
	y_train = train_df[TARGET_COL]
	X_val = val_df[feature_cols]
	y_val = val_df[TARGET_COL]

	print(f"Train rows: {len(train_df)} | Validation rows: {len(val_df)} | Test rows: {len(test_df)}")

	dtrain = xgb.DMatrix(X_train, label=y_train, feature_names=feature_cols)
	dval = xgb.DMatrix(X_val, label=y_val, feature_names=feature_cols)
	params = {
		"objective": "reg:squarederror",
		"eta": 0.05,
		"max_depth": 6,
		"subsample": 0.8,
		"colsample_bytree": 0.8,
		"min_child_weight": 5,
		"alpha": 0.1,
		"lambda": 1.0,
		"eval_metric": "rmse",
		"seed": 42,
		"nthread": -1,
	}

	booster = xgb.train(
		params,
		dtrain,
		num_boost_round=500,
		evals=[(dval, "validation")],
		early_stopping_rounds=30,
		verbose_eval=50,
	)

	val_predictions = pd.Series(booster.predict(dval), index=val_df.index)
	val_rmse = float(np.sqrt(mean_squared_error(y_val, val_predictions)))
	val_mae = float(mean_absolute_error(y_val, val_predictions))
	print(f"Validation RMSE: {val_rmse:.4f}")
	print(f"Validation MAE:  {val_mae:.4f}")

	booster.save_model(MODEL_PATH)
	FEATURE_COLUMNS_PATH.write_text("\n".join(feature_cols) + "\n", encoding="utf-8")
	with open(ENCODERS_PATH, "wb") as handle:
		pickle.dump(encoders, handle)

	_plot_feature_importance(booster, feature_cols)

	print(f"Saved XGBoost model to {MODEL_PATH}")
	print(f"Saved feature importance plot to {FEATURE_IMPORTANCE_PATH}")
	print(f"Saved feature columns to {FEATURE_COLUMNS_PATH}")
	print(f"Saved label encoders to {ENCODERS_PATH}")

	print("\nPhase 3 summary:")
	print("✓ Feature matrix built for all series")
	print("✓ Global XGBoost model trained on SARIMA residuals")
	print("✓ Model, encoders, feature list saved")
	print("✓ Ready for hybrid prediction in Phase 4")


if __name__ == "__main__":
	main()
