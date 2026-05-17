from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import unicodedata
import warnings
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import xgboost as xgb
from pmdarima import auto_arima
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.statespace.sarimax import SARIMAX

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
BASE_DIR = ROOT / "SARIMA" / "sarimax_x"
OUTPUT_DIR = BASE_DIR / "outputs"
PLOTS_DIR = BASE_DIR / "plots"
SERIES_PLOTS_DIR = PLOTS_DIR / "series"
MODELS_DIR = BASE_DIR / "models"

DEFAULT_INPUT = ROOT / "data" / "ecommerce_algerie_2024_2025_version16mai.csv"
REGIONS_PATH = ROOT / "wilayas_regions.txt"

RAMADAN_RANGES = [
    ("2024-03-11", "2024-04-09"),
    ("2025-03-01", "2025-03-30"),
]
EID_DATES = ["2024-04-10", "2025-03-30"]

EXOG_COLS = [
    "is_ramadan",
    "ramadan_progress",
    "is_eid_week",
    "is_summer",
    "is_rentree",
    "is_winter",
    "cat_season_multiplier",
]

FEATURE_COLS = [
    "lag_1",
    "lag_2",
    "lag_4",
    "lag_8",
    "rolling_mean_4",
    "rolling_mean_8",
    "rolling_std_4",
    "is_ramadan",
    "ramadan_progress",
    "is_eid_week",
    "is_summer",
    "is_rentree",
    "is_winter",
    "cat_season_multiplier",
    "sarimax_forecast",
    "week_of_year",
    "region_enc",
    "cat_group_enc",
]

AUTO_ARIMA_CONFIG = {
    "start_p": 0,
    "max_p": 2,
    "start_q": 0,
    "max_q": 2,
    "d": None,
    "seasonal": True,
    "m": 52,
    "start_P": 0,
    "max_P": 1,
    "start_Q": 0,
    "max_Q": 1,
    "D": 1,
    "information_criterion": "aic",
    "stepwise": True,
    "suppress_warnings": True,
    "error_action": "ignore",
}


@dataclass
class SplitFrames:
    train: pd.DataFrame
    val: pd.DataFrame
    test: pd.DataFrame


def _normalize_text(value: str) -> str:
    text = str(value).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _series_key(region: str, cat_group: str) -> str:
    key = f"{region}__{cat_group}".strip().lower()
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]


def _load_regions_map() -> dict[str, str]:
    raw_text = REGIONS_PATH.read_text(encoding="utf-8")
    cleaned = re.sub(r",\s*([}\]])", r"\1", raw_text)
    region_data = json.loads(cleaned)
    region_name_map = {
        "centre": "NORTH",
        "est": "EAST",
        "ouest": "WEST",
        "sud": "SOUTH",
    }
    region_map: dict[str, str] = {}
    for region, wilayas in region_data.items():
        mapped = region_name_map.get(region.strip().lower())
        if mapped is None:
            continue
        for wilaya in wilayas:
            region_map[_normalize_text(wilaya)] = mapped
    return region_map


def _map_category_group(category: str) -> str:
    norm = _normalize_text(category)
    mapping = {
        "vetements et accessoires": "fashion",
        "bagages et maroquinerie": "fashion",
        "appareils electroniques": "electronics",
        "appareils photo cameras et instruments d optique": "electronics",
        "maison et jardin": "home",
        "meubles": "home",
        "equipements sportifs": "sports_leisure",
        "arts et loisirs": "sports_leisure",
        "jeux et jouets": "sports_leisure",
    }
    return mapping.get(norm, "other")


def _iso_week_start(iso_year: pd.Series, iso_week: pd.Series) -> pd.Series:
    text = iso_year.astype(str) + "-W" + iso_week.astype(str).str.zfill(2) + "-1"
    return pd.to_datetime(text, format="%G-W%V-%u")


def _build_calendar_features(week_starts: pd.Series) -> pd.DataFrame:
    df = pd.DataFrame({"week_start": week_starts}).drop_duplicates().sort_values("week_start")
    df = df.reset_index(drop=True)
    df["week_end"] = df["week_start"] + pd.Timedelta(days=6)

    df["is_ramadan"] = 0
    df["ramadan_progress"] = 0.0
    for start_text, end_text in RAMADAN_RANGES:
        start = pd.Timestamp(start_text)
        end = pd.Timestamp(end_text)
        overlap = (df["week_start"] <= end) & (df["week_end"] >= start)
        idx = df.index[overlap]
        if len(idx) == 0:
            continue
        if len(idx) == 1:
            progress = np.array([1.0])
        else:
            progress = np.linspace(0.0, 1.0, len(idx))
        df.loc[idx, "is_ramadan"] = 1
        df.loc[idx, "ramadan_progress"] = progress

    df["is_eid_week"] = 0
    for eid_text in EID_DATES:
        eid = pd.Timestamp(eid_text)
        eid_week = (df["week_start"] <= eid) & (df["week_end"] >= eid)
        df.loc[eid_week, "is_eid_week"] = 1

    summer_months = {6, 7, 8}
    rentree_months = {9}
    winter_months = {1, 2}

    start_month = df["week_start"].dt.month
    end_month = df["week_end"].dt.month

    df["is_summer"] = ((start_month.isin(summer_months)) | (end_month.isin(summer_months))).astype(int)
    df["is_rentree"] = ((start_month.isin(rentree_months)) | (end_month.isin(rentree_months))).astype(int)
    df["is_winter"] = ((start_month.isin(winter_months)) | (end_month.isin(winter_months))).astype(int)

    df = df.drop(columns=["week_end"])
    return df


def _apply_cat_season_multiplier(df: pd.DataFrame) -> pd.Series:
    base = np.ones(len(df), dtype=float)
    fashion = df["cat_group"] == "fashion"
    electronics = df["cat_group"] == "electronics"
    home = df["cat_group"] == "home"
    sports = df["cat_group"] == "sports_leisure"
    other = df["cat_group"] == "other"

    base = np.where(fashion & (df["is_eid_week"] == 1), 1.5, base)
    base = np.where(electronics & (df["is_ramadan"] == 1), 1.15, base)
    base = np.where(home & (df["is_ramadan"] == 1), 1.25, base)
    base = np.where(sports & (df["is_summer"] == 1), 1.4, base)
    base = np.where(other & (df["is_rentree"] == 1), 1.5, base)
    return base


def build_master_frame(input_path: Path) -> pd.DataFrame:
    raw = pd.read_csv(input_path)
    raw = raw.copy()

    date_col = None
    for col in raw.columns:
        if _normalize_text(col) == "date expedition":
            date_col = col
            break
    if date_col is None:
        raise KeyError("Missing required column: date expédition")

    cat_col = None
    for col in raw.columns:
        if _normalize_text(col) == "categorie":
            cat_col = col
            break
    if cat_col is None:
        raise KeyError("Missing required column: Categorie")

    wilaya_col = None
    for col in raw.columns:
        if _normalize_text(col) == "destination wilaya":
            wilaya_col = col
            break
    if wilaya_col is None:
        raise KeyError("Missing required column: destination wilaya")

    raw[date_col] = pd.to_datetime(raw[date_col], errors="coerce")
    raw = raw.dropna(subset=[date_col, cat_col, wilaya_col]).copy()

    iso = raw[date_col].dt.isocalendar()
    raw["iso_year"] = iso.year.astype(int)
    raw["iso_week"] = iso.week.astype(int)

    region_map = _load_regions_map()
    raw["region"] = raw[wilaya_col].map(_normalize_text).map(region_map).fillna("UNKNOWN")
    raw["cat_group"] = raw[cat_col].apply(_map_category_group)

    weekly = (
        raw.groupby(["iso_year", "iso_week", "region", "cat_group"], dropna=False)
        .size()
        .reset_index(name="y")
    )
    weekly["week_start"] = _iso_week_start(weekly["iso_year"], weekly["iso_week"])

    frames = []
    for (region, cat_group), group in weekly.groupby(["region", "cat_group"], sort=False):
        min_week = group["week_start"].min()
        max_week = group["week_start"].max()
        full_weeks = pd.date_range(min_week, max_week, freq="W-MON")
        full = pd.DataFrame({"week_start": full_weeks})
        full["region"] = region
        full["cat_group"] = cat_group
        merged = full.merge(group[["week_start", "y"]], on="week_start", how="left")
        merged["y"] = merged["y"].fillna(0).astype(float)
        iso_full = merged["week_start"].dt.isocalendar()
        merged["iso_year"] = iso_full.year.astype(int)
        merged["iso_week"] = iso_full.week.astype(int)
        frames.append(merged)

    master = pd.concat(frames, ignore_index=True)
    calendar = _build_calendar_features(master["week_start"])
    master = master.merge(calendar, on="week_start", how="left")
    master["cat_season_multiplier"] = _apply_cat_season_multiplier(master)
    master = master.sort_values(["region", "cat_group", "week_start"]).reset_index(drop=True)
    return master


def assign_split(df: pd.DataFrame) -> pd.DataFrame:
    def _split_row(row):
        if row["iso_year"] == 2024 and row["iso_week"] <= 44:
            return "train"
        if row["iso_year"] == 2024 and row["iso_week"] >= 45:
            return "validation"
        if row["iso_year"] == 2025:
            return "test"
        return "other"

    df = df.copy()
    df["split"] = df.apply(_split_row, axis=1)
    df = df[df["split"].isin(["train", "validation", "test"])].copy()
    return df


def _split_frames(df: pd.DataFrame) -> SplitFrames:
    train = df[df["split"] == "train"].copy()
    val = df[df["split"] == "validation"].copy()
    test = df[df["split"] == "test"].copy()
    return SplitFrames(train=train, val=val, test=test)


def _series_sparsity(y: pd.Series) -> float:
    if len(y) == 0:
        return 0.0
    return float((y == 0).mean())


def run_sarimax(master: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    orders = []
    rows = []

    for (region, cat_group), group in master.groupby(["region", "cat_group"], sort=False):
        group = group.sort_values("week_start").reset_index(drop=True)
        splits = _split_frames(group)

        print(f"[SARIMAX] {region} | {cat_group} | rows={len(group)}")

        if splits.train.empty or splits.val.empty or splits.test.empty:
            print("  [SKIP] insufficient split sizes")
            continue

        y_train = splits.train["y"].values
        exog_train = splits.train[EXOG_COLS].values
        y_val = splits.val["y"].values
        exog_val = splits.val[EXOG_COLS].values
        y_test = splits.test["y"].values
        exog_test = splits.test[EXOG_COLS].values

        sparsity = _series_sparsity(group["y"])
        if sparsity > 0.30:
            print(f"  [WARN] high sparsity ({sparsity:.2%} zeros)")

        used_m = 52
        try:
            arima = auto_arima(y_train, X=exog_train, **AUTO_ARIMA_CONFIG)
        except Exception as exc:
            print(f"  [WARN] auto_arima failed for m=52: {exc}")
            used_m = 1
            fallback = AUTO_ARIMA_CONFIG.copy()
            fallback["seasonal"] = False
            fallback["m"] = 1
            arima = auto_arima(y_train, X=exog_train, **fallback)

        order = arima.order
        seasonal_order = arima.seasonal_order if used_m == 52 else (0, 0, 0, 0)
        print(f"  order={order} seasonal={seasonal_order} m={used_m}")

        model = SARIMAX(
            y_train,
            order=order,
            seasonal_order=seasonal_order,
            exog=exog_train,
            enforce_stationarity=False,
            enforce_invertibility=False,
        )
        model_fit = model.fit(disp=False)

        fitted = model_fit.get_prediction(start=0, end=len(y_train) - 1, exog=exog_train).predicted_mean
        fitted = np.asarray(fitted)
        residuals_train = y_train - fitted

        ljung = acorr_ljungbox(residuals_train, lags=[10], return_df=True)
        pval = float(ljung["lb_pvalue"].iloc[0])
        if pval < 0.05:
            print(f"  [WARN] Ljung-Box p<0.05 (p={pval:.4f})")

        exog_future = np.vstack([exog_val, exog_test])
        forecast_all = model_fit.get_forecast(steps=len(exog_future), exog=exog_future).predicted_mean
        forecast_all = np.asarray(forecast_all)
        forecast_val = forecast_all[: len(y_val)]
        forecast_test = forecast_all[len(y_val) :]

        key = _series_key(region, cat_group)
        model_path = MODELS_DIR / f"sarimax_{key}.pkl"
        model_fit.save(model_path)

        orders.append({
            "region": region,
            "cat_group": cat_group,
            "order": str(order),
            "seasonal_order": str(seasonal_order),
            "m": used_m,
            "model_key": key,
        })

        for idx, row in splits.train.iterrows():
            rows.append({
                "week_start": row["week_start"],
                "region": region,
                "cat_group": cat_group,
                "split": "train",
                "y": row["y"],
                "sarimax_pred": fitted[splits.train.index.get_loc(idx)],
                "residual": row["y"] - fitted[splits.train.index.get_loc(idx)],
            })
        for i, row in splits.val.reset_index(drop=True).iterrows():
            rows.append({
                "week_start": row["week_start"],
                "region": region,
                "cat_group": cat_group,
                "split": "validation",
                "y": row["y"],
                "sarimax_pred": forecast_val[i],
                "residual": row["y"] - forecast_val[i],
            })
        for i, row in splits.test.reset_index(drop=True).iterrows():
            rows.append({
                "week_start": row["week_start"],
                "region": region,
                "cat_group": cat_group,
                "split": "test",
                "y": row["y"],
                "sarimax_pred": forecast_test[i],
                "residual": row["y"] - forecast_test[i],
            })

    orders_df = pd.DataFrame(orders)
    preds_df = pd.DataFrame(rows)
    return orders_df, preds_df


def build_feature_matrix(master: pd.DataFrame, preds_df: pd.DataFrame) -> pd.DataFrame:
    df = master.merge(
        preds_df[["week_start", "region", "cat_group", "sarimax_pred", "residual"]],
        on=["week_start", "region", "cat_group"],
        how="left",
    )
    df = df.sort_values(["region", "cat_group", "week_start"]).reset_index(drop=True)
    if "residual" not in df.columns:
        df["residual"] = df["y"] - df["sarimax_pred"]
    else:
        df["residual"] = df["residual"].fillna(df["y"] - df["sarimax_pred"])

    # lags and rolling features
    features = []
    for (region, cat_group), group in df.groupby(["region", "cat_group"], sort=False):
        group = group.copy()
        y = group["y"]
        group["lag_1"] = y.shift(1)
        group["lag_2"] = y.shift(2)
        group["lag_4"] = y.shift(4)
        group["lag_8"] = y.shift(8)
        group["rolling_mean_4"] = y.shift(1).rolling(4).mean()
        group["rolling_mean_8"] = y.shift(1).rolling(8).mean()
        group["rolling_std_4"] = y.shift(1).rolling(4).std()
        features.append(group)
    df = pd.concat(features, ignore_index=True)

    df["sarimax_forecast"] = df["sarimax_pred"]
    df["week_of_year"] = df["iso_week"].astype(int)

    region_order = sorted(df["region"].unique())
    cat_order = sorted(df["cat_group"].unique())
    df["region_enc"] = pd.Categorical(df["region"], categories=region_order).codes
    df["cat_group_enc"] = pd.Categorical(df["cat_group"], categories=cat_order).codes

    # leakage check: lag_1 should equal previous week y within series
    for (region, cat_group), group in df.groupby(["region", "cat_group"], sort=False):
        group = group.sort_values("week_start").reset_index(drop=True)
        if len(group) < 2:
            continue
        lag_check = group["y"].shift(1)
        mismatch = (group["lag_1"].notna()) & (~np.isclose(group["lag_1"], lag_check, equal_nan=True))
        if mismatch.any():
            raise AssertionError("Leakage detected in lag_1 for series")

    df = df.dropna(subset=FEATURE_COLS + ["sarimax_pred"]).copy()
    return df


def train_xgb(train_df: pd.DataFrame, val_df: pd.DataFrame) -> xgb.Booster:
    dtrain = xgb.DMatrix(train_df[FEATURE_COLS], label=train_df["residual"], feature_names=FEATURE_COLS)
    dval = xgb.DMatrix(val_df[FEATURE_COLS], label=val_df["residual"], feature_names=FEATURE_COLS)

    params = {
        "objective": "reg:squarederror",
        "eta": 0.03,
        "max_depth": 4,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "min_child_weight": 5,
        "eval_metric": "rmse",
    }

    booster = xgb.train(
        params,
        dtrain,
        num_boost_round=1000,
        evals=[(dval, "validation")],
        early_stopping_rounds=50,
        verbose_eval=50,
    )
    return booster


def _series_metrics(actual: pd.Series, forecast: pd.Series, train_series: pd.Series) -> dict[str, float]:
    mae = float(mean_absolute_error(actual, forecast)) if len(actual) else math.nan
    rmse = float(np.sqrt(mean_squared_error(actual, forecast))) if len(actual) else math.nan

    mask = actual != 0
    mape = float((np.abs((actual[mask] - forecast[mask]) / actual[mask])).mean() * 100) if mask.any() else math.nan

    denom = (np.abs(actual) + np.abs(forecast))
    smape = float((2.0 * np.abs(actual - forecast) / denom.replace(0, np.nan)).mean() * 100)

    train_naive = np.abs(train_series.diff().dropna())
    mase_den = float(train_naive.mean()) if len(train_naive) else math.nan
    mase = float(mae / mase_den) if mase_den and not math.isnan(mase_den) else math.nan

    r2 = float(r2_score(actual, forecast)) if len(actual) > 1 else math.nan

    return {
        "MAE": mae,
        "RMSE": rmse,
        "MAPE": mape,
        "SMAPE": smape,
        "MASE": mase,
        "R2": r2,
    }


def evaluate(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, set[tuple[str, str]]]:
    metrics_rows = []
    fallback = set()

    for (region, cat_group), group in df.groupby(["region", "cat_group"], sort=False):
        train_series = group[group["split"] == "train"]["y"]
        val = group[group["split"] == "validation"]
        test = group[group["split"] == "test"]

        if val.empty or test.empty:
            continue

        sarima_val = _series_metrics(val["y"], val["sarimax_pred"], train_series)
        hybrid_val = _series_metrics(val["y"], val["hybrid_pred"], train_series)

        if hybrid_val["MAE"] > sarima_val["MAE"]:
            print(f"[WARN] fallback to SARIMAX for {region} | {cat_group} (validation MAE worse)")
            fallback.add((region, cat_group))

        sarima_test = _series_metrics(test["y"], test["sarimax_pred"], train_series)
        hybrid_test = _series_metrics(test["y"], test["hybrid_pred"], train_series)

        metrics_rows.append({"region": region, "cat_group": cat_group, "split": "validation", "model": "SARIMAX", **sarima_val})
        metrics_rows.append({"region": region, "cat_group": cat_group, "split": "validation", "model": "Hybrid", **hybrid_val})
        metrics_rows.append({"region": region, "cat_group": cat_group, "split": "test", "model": "SARIMAX", **sarima_test})
        metrics_rows.append({"region": region, "cat_group": cat_group, "split": "test", "model": "Hybrid", **hybrid_test})

    metrics_df = pd.DataFrame(metrics_rows)
    summary = (
        metrics_df.groupby(["model", "split"])[["MAE", "RMSE", "MAPE", "SMAPE", "MASE", "R2"]]
        .agg(["mean", "std"])
        .reset_index()
    )
    return metrics_df, summary, fallback


def plot_series(df: pd.DataFrame) -> None:
    for (region, cat_group), group in df.groupby(["region", "cat_group"], sort=False):
        group = group.sort_values("week_start")
        key = _series_key(region, cat_group)
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(group["week_start"], group["y"], label="Actual", color="black")
        ax.plot(group["week_start"], group["sarimax_pred"], label="SARIMAX", linestyle="--")
        ax.plot(group["week_start"], group["hybrid_pred"], label="Hybrid", linestyle=":")
        ax.set_title(f"{region} | {cat_group}")
        ax.legend()
        fig.tight_layout()
        fig.savefig(SERIES_PLOTS_DIR / f"series_{key}.png", dpi=150)
        plt.close(fig)


def plot_global(df: pd.DataFrame) -> None:
    grouped = (
        df.groupby(["week_start", "split"], sort=False)
        .agg(actual=("y", "sum"), sarimax=("sarimax_pred", "sum"), hybrid=("hybrid_pred", "sum"))
        .reset_index()
        .sort_values("week_start")
    )
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(grouped["week_start"], grouped["actual"], label="Actual", color="black")
    ax.plot(grouped["week_start"], grouped["sarimax"], label="SARIMAX", linestyle="--")
    ax.plot(grouped["week_start"], grouped["hybrid"], label="Hybrid", linestyle=":")
    ax.set_title("Global aggregated forecast")
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "global_actual_vs_pred.png", dpi=150)
    plt.close(fig)


def plot_feature_importance(booster: xgb.Booster) -> None:
    importance = booster.get_score(importance_type="gain")
    if not importance:
        return
    items = sorted(importance.items(), key=lambda x: x[1], reverse=True)
    labels = [k for k, _ in items]
    scores = [v for _, v in items]
    plt.figure(figsize=(10, 6))
    plt.barh(labels[::-1], scores[::-1], color="#0f766e")
    plt.title("XGBoost feature importance (gain)")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "xgb_feature_importance.png", dpi=150)
    plt.close()


def plot_r2_heatmaps(metrics_df: pd.DataFrame) -> None:
    for model in ["SARIMAX", "Hybrid"]:
        test_df = metrics_df[(metrics_df["split"] == "test") & (metrics_df["model"] == model)]
        pivot = test_df.pivot(index="cat_group", columns="region", values="R2")
        plt.figure(figsize=(6, 4))
        sns.heatmap(pivot, annot=True, fmt=".2f", cmap="coolwarm", center=0)
        plt.title(f"R2 heatmap ({model})")
        plt.tight_layout()
        plt.savefig(PLOTS_DIR / f"r2_heatmap_{model.lower()}.png", dpi=150)
        plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="SARIMAX + XGBoost hybrid pipeline")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    SERIES_PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    print("[STEP 1] Building weekly master frame...")
    master = build_master_frame(args.input)
    master = assign_split(master)
    master.to_csv(OUTPUT_DIR / "weekly_series.csv", index=False)

    print("[STEP 2] SARIMAX fitting...")
    orders_df, preds_df = run_sarimax(master)
    orders_df.to_csv(OUTPUT_DIR / "sarimax_orders.csv", index=False)
    preds_df.to_csv(OUTPUT_DIR / "sarimax_predictions.csv", index=False)

    print("[STEP 3] Feature engineering for XGBoost...")
    features = build_feature_matrix(master, preds_df)

    train_df = features[features["split"] == "train"].copy()
    val_df = features[features["split"] == "validation"].copy()
    test_df = features[features["split"] == "test"].copy()

    print(f"Train rows: {len(train_df)} | Val rows: {len(val_df)} | Test rows: {len(test_df)}")

    print("[STEP 4] Training XGBoost...")
    booster = train_xgb(train_df, val_df)
    booster.save_model(str(OUTPUT_DIR / "xgb_model.json"))

    with open(OUTPUT_DIR / "xgb_feature_columns.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(FEATURE_COLS) + "\n")

    dval = xgb.DMatrix(val_df[FEATURE_COLS], feature_names=FEATURE_COLS)
    dtest = xgb.DMatrix(test_df[FEATURE_COLS], feature_names=FEATURE_COLS)

    val_df["xgb_correction"] = booster.predict(dval)
    test_df["xgb_correction"] = booster.predict(dtest)

    val_df["hybrid_pred"] = val_df["sarimax_pred"] + val_df["xgb_correction"]
    test_df["hybrid_pred"] = test_df["sarimax_pred"] + test_df["xgb_correction"]

    print("[STEP 6] Sanity checks (correction magnitude)...")
    mean_corr = float(test_df["xgb_correction"].mean())
    mean_abs_err = float(np.abs(test_df["y"] - test_df["sarimax_pred"]).mean())
    if abs(mean_corr) > 0.5 * mean_abs_err:
        print("[WARN] XGBoost may be overcorrecting on test data")

    print("[STEP 5] Evaluation...")
    full_df = pd.concat([train_df, val_df, test_df], ignore_index=True)
    metrics_df, summary_df, fallback = evaluate(full_df)

    if fallback:
        mask = full_df[["region", "cat_group"]].apply(tuple, axis=1).isin(fallback)
        full_df.loc[mask & (full_df["split"] == "test"), "hybrid_pred"] = full_df.loc[
            mask & (full_df["split"] == "test"), "sarimax_pred"
        ]
        full_df.loc[mask & (full_df["split"] == "validation"), "hybrid_pred"] = full_df.loc[
            mask & (full_df["split"] == "validation"), "sarimax_pred"
        ]

    metrics_df.to_csv(OUTPUT_DIR / "metrics_all_series.csv", index=False)
    summary_df.to_csv(OUTPUT_DIR / "metrics_summary.csv", index=False)

    print("[STEP 5] Plotting...")
    plot_series(full_df)
    plot_global(full_df)
    plot_feature_importance(booster)
    plot_r2_heatmaps(metrics_df)

    hybrid_out = full_df[full_df["split"].isin(["validation", "test"])][
        ["week_start", "region", "cat_group", "split", "y", "sarimax_pred", "xgb_correction", "hybrid_pred"]
    ].copy()
    hybrid_out.to_csv(OUTPUT_DIR / "hybrid_forecasts.csv", index=False)

    print("Pipeline completed successfully.")


if __name__ == "__main__":
    main()
