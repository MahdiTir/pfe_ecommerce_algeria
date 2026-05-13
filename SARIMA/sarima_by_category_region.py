from __future__ import annotations

import itertools
import json
import re
import unicodedata
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from pmdarima import auto_arima
from statsmodels.tsa.statespace.sarimax import SARIMAX


warnings.filterwarnings("ignore")

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT_DIR / "data" / "ecommerce_algerie_2024_2025_version10mai.csv"
MODELS_DIR = ROOT_DIR / "SARIMA" / "models"
REGIONS_PATH = ROOT_DIR / "wilayas_regions.txt"

DATE_COL = "date"
CATEGORY_COL = "category"
REGION_COL = "region"
DEMAND_COL = "demand"

MIN_LENGTH = 24
FORECAST_STEPS = 12

AUTO_ARIMA_CONFIG = {
    "seasonal": True,
    "m": 12,
    "stepwise": True,
    "suppress_warnings": True,
    "error_action": "ignore",
    "information_criterion": "aic",
}


def _slugify(value: str) -> str:
    text = str(value).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "unknown"


def _normalize_text(value: str) -> str:
    text = str(value).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _find_column(columns: list[str], target_normalized: str) -> str:
    for column in columns:
        if _normalize_text(column) == target_normalized:
            return column
    raise KeyError(f"Missing required column: {target_normalized}")


def _load_regions_map() -> dict[str, str]:
    raw_text = REGIONS_PATH.read_text(encoding="utf-8")
    cleaned_text = re.sub(r",\s*([}\]])", r"\1", raw_text)
    region_data = json.loads(cleaned_text)

    region_map: dict[str, str] = {}
    for region, wilayas in region_data.items():
        for wilaya in wilayas:
            region_map[_normalize_text(wilaya)] = region
    return region_map


def _prepare_aggregated(df: pd.DataFrame) -> pd.DataFrame:
    columns = df.columns.tolist()
    date_col = _find_column(columns, "date")
    category_col = _find_column(columns, "category")
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
    return df.sort_values(DATE_COL)


def _prepare_raw(df: pd.DataFrame) -> pd.DataFrame:
    columns = df.columns.tolist()
    category_col = _find_column(columns, "categorie")
    date_col = _find_column(columns, "date expedition")
    wilaya_col = _find_column(columns, "destination wilaya")

    region_map = _load_regions_map()

    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col, category_col, wilaya_col]).copy()

    df[REGION_COL] = (
        df[wilaya_col]
        .map(_normalize_text)
        .map(region_map)
        .fillna("unknown")
    )
    df[CATEGORY_COL] = df[category_col]
    df[DATE_COL] = df[date_col].dt.normalize()

    daily = (
        df.groupby([DATE_COL, CATEGORY_COL, REGION_COL], dropna=False)
        .size()
        .reset_index(name=DEMAND_COL)
        .sort_values([DATE_COL, CATEGORY_COL, REGION_COL])
    )
    return daily


def _load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    normalized_cols = {_normalize_text(col) for col in df.columns}
    has_aggregated = {"date", "category", "region", "demand"}.issubset(normalized_cols)

    if has_aggregated:
        return _prepare_aggregated(df)
    return _prepare_raw(df)


def _series_for(df: pd.DataFrame, category: str, region: str) -> pd.Series:
    ts = (
        df[(df[CATEGORY_COL] == category) & (df[REGION_COL] == region)]
        .groupby(DATE_COL, as_index=True)[DEMAND_COL]
        .sum()
        .sort_index()
    )
    return ts


def _fit_one(df: pd.DataFrame, category: str, region: str):
    file_key = f"{_slugify(category)}_{_slugify(region)}"
    display_key = f"{category} | {region}"
    path = MODELS_DIR / f"sarima_{file_key}.pkl"

    if path.exists():
        print(f"  [CACHE]  {display_key}")
        return (category, region), joblib.load(path), None, None

    ts = _series_for(df, category, region)

    if len(ts) < MIN_LENGTH:
        print(f"  [SKIP]   {display_key} - only {len(ts)} points")
        return (category, region), None, None, None

    if np.isclose(ts.sum(), 0):
        print(f"  [SKIP]   {display_key} - all zeros")
        return (category, region), None, None, None

    try:
        arima = auto_arima(ts, **AUTO_ARIMA_CONFIG)
        order = arima.order

        model = SARIMAX(
            ts,
            order=order,
            seasonal_order=(0, 0, 0, 0),
            enforce_stationarity=False,
            enforce_invertibility=False,
        )
        fit = model.fit(disp=False)
        forecast = fit.forecast(steps=FORECAST_STEPS)

        joblib.dump(fit, path)
        print(f"  [OK]     {display_key} - order={order} AIC={fit.aic:.1f}")
        return (category, region), fit, forecast, order

    except Exception as exc:
        print(f"  [ERROR]  {display_key} - {exc}")
        return (category, region), None, None, None


def main() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    df = _load_data()
    categories = sorted(df[CATEGORY_COL].unique())
    regions = sorted(df[REGION_COL].unique())
    combos = list(itertools.product(categories, regions))

    print(
        f"Fitting {len(combos)} models ({len(categories)} categories x {len(regions)} regions)...\n"
    )

    results = joblib.Parallel(n_jobs=-1)(
        joblib.delayed(_fit_one)(df, category, region)
        for category, region in combos
    )

    models = {}
    forecasts = {}
    orders = []

    for key, fit, forecast, order in results:
        if fit is None:
            continue
        models[key] = fit
        if forecast is not None:
            forecasts[key] = forecast
        if order is not None:
            orders.append(
                {
                    "category": key[0],
                    "region": key[1],
                    "order": str(order),
                    "aic": float(fit.aic),
                }
            )

    if orders:
        orders_path = MODELS_DIR / "sarima_orders.csv"
        pd.DataFrame(orders).to_csv(orders_path, index=False)
        print(f"\nSaved order summary to {orders_path}")

    print(f"\nDone - {len(models)} models fitted.")


if __name__ == "__main__":
    main()
