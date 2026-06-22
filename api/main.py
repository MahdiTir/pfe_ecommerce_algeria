from __future__ import annotations

import json
import re
import unicodedata
from datetime import date
import time
from functools import lru_cache
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from statsmodels.tsa.statespace.sarimax import SARIMAXResults

from optimization.Genitic import run_genetic_optimization, run_optimization_comparison, run_exact_ilp_solver


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "app_config.json"
CATEGORIES_PATH = ROOT / "categories.json"
ORDERS_PATH = ROOT / "SARIMA" / "sarimax_x" / "outputs" / "sarimax_orders.csv"
WEEKLY_SERIES_PATH = ROOT / "SARIMA" / "sarimax_x" / "outputs" / "weekly_series.csv"
MODELS_DIR = ROOT / "SARIMA" / "sarimax_x" / "models"

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

CANONICAL_REGIONS = frozenset({"EAST", "NORTH", "SOUTH", "WEST"})

REGION_ALIASES = {
    "centre": "NORTH",
    "center": "NORTH",
    "north": "NORTH",
    "est": "EAST",
    "east": "EAST",
    "ouest": "WEST",
    "west": "WEST",
    "sud": "SOUTH",
    "south": "SOUTH",
}



class WarehouseSpec(BaseModel):
    capacity: int = Field(..., ge=0)
    stock_level: int = Field(0, ge=0)
    region: str = Field(..., min_length=1)


class ForecastRequest(BaseModel):
    countity: int = Field(..., ge=0)
    warehouses: Dict[str, WarehouseSpec]
    transport_cost: Dict[str, float]
    category: str
    holding_cost: Dict[str, float]
    forecast_date: date
    period: int = Field(..., ge=1)


class ForecastItem(BaseModel):
    week_start: str
    region: str
    sarimax_forecast: float


class OptimizationMethodResult(BaseModel):
    method: str
    total_cost: float
    service_level: float
    runtime_seconds: float
    mt: float


class ForecastResponse(BaseModel):
    parent_category: str
    period_weeks: int
    forecast: List[ForecastItem]
    region_percentages: Dict[str, float]
    allocation_by_region: Dict[str, int]
    allocation_by_warehouse: Dict[str, int]
    final_stock_by_warehouse: Dict[str, int]
    genetic: Dict[str, object]
    optimization_methods: List[OptimizationMethodResult]


app = FastAPI(title="SARIMAX Forecast API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _normalize_text(value: str) -> str:
    text = str(value).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _canonical_region(value: str) -> str:
    raw = str(value).strip()
    upper = raw.upper()
    if upper in CANONICAL_REGIONS:
        return upper
    mapped = REGION_ALIASES.get(_normalize_text(raw))
    if mapped:
        return mapped
    raise HTTPException(
        status_code=400,
        detail=f"Unknown region: {value}. Use one of: {', '.join(sorted(CANONICAL_REGIONS))}",
    )


def _normalize_warehouse_regions(
    warehouses: Dict[str, WarehouseSpec],
) -> Dict[str, WarehouseSpec]:
    return {
        name: spec.model_copy(update={"region": _canonical_region(spec.region)})
        for name, spec in warehouses.items()
    }


@lru_cache
def _valid_parent_categories() -> frozenset:
    if not CATEGORIES_PATH.exists():
        raise FileNotFoundError(f"Missing categories.json at {CATEGORIES_PATH}")
    raw = json.loads(CATEGORIES_PATH.read_text(encoding="utf-8"))
    return frozenset(item["name"].strip() for item in raw.get("categories", []) if item.get("name"))


@lru_cache
def _child_to_parent_category() -> Dict[str, str]:
    if not CATEGORIES_PATH.exists():
        raise FileNotFoundError(f"Missing categories.json at {CATEGORIES_PATH}")
    raw = json.loads(CATEGORIES_PATH.read_text(encoding="utf-8"))
    mapping: Dict[str, str] = {}
    for item in raw.get("categories", []):
        parent = str(item.get("name", "")).strip()
        if not parent:
            continue
        for child in item.get("children", []):
            child_name = str(child).strip()
            if child_name:
                mapping[child_name] = parent
    return mapping


@lru_cache
def _orders_index() -> pd.DataFrame:
    if not ORDERS_PATH.exists():
        raise FileNotFoundError(f"Missing sarimax_orders.csv at {ORDERS_PATH}")
    return pd.read_csv(ORDERS_PATH)


@lru_cache
def _weekly_series() -> pd.DataFrame:
    if not WEEKLY_SERIES_PATH.exists():
        raise FileNotFoundError(f"Missing weekly_series.csv at {WEEKLY_SERIES_PATH}")
    df = pd.read_csv(WEEKLY_SERIES_PATH)
    df["week_start"] = pd.to_datetime(df["week_start"], errors="coerce")
    return df


@lru_cache
def _load_model(model_key: str):
    model_path = MODELS_DIR / f"sarimax_{model_key}.pkl"
    if not model_path.exists():
        raise FileNotFoundError(f"Missing SARIMAX model at {model_path}")
    return SARIMAXResults.load(model_path)


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
    pc = df["parent_category"]

    eid_fashion = pc.isin(["Apparel & Accessories", "Luggage & Bags"])
    ram_electronics = pc.isin(["Electronics", "Cameras & Optics"])
    ram_home = pc.isin(["Home & Garden", "Furniture"])
    ram_health = pc == "Health & Beauty"
    summer_sports = pc.isin(["Sporting Goods", "Arts & Entertainment"])
    rentree_boost = pc.isin(["Office Supplies", "Baby & Toddler", "Media"])

    base = np.where(eid_fashion & (df["is_eid_week"] == 1), 1.5, base)
    base = np.where(ram_electronics & (df["is_ramadan"] == 1), 1.15, base)
    base = np.where(ram_home & (df["is_ramadan"] == 1), 1.25, base)
    base = np.where(ram_health & (df["is_ramadan"] == 1), 1.2, base)
    base = np.where(summer_sports & (df["is_summer"] == 1), 1.4, base)
    base = np.where(rentree_boost & (df["is_rentree"] == 1), 1.5, base)
    return base


def _validate_parent_category(category: str) -> str:
    """Accept a parent or child category name; return the parent for forecasting."""
    name = category.strip()
    valid = _valid_parent_categories()
    if name in valid:
        return name

    parent = _child_to_parent_category().get(name)
    if parent:
        return parent

    raise HTTPException(
        status_code=400,
        detail=(
            f"Unknown category '{category}'. "
            "Use a parent category or a subcategory listed in categories.json."
        ),
    )


def _forecast_sarimax(parent_category: str, periods: int, anchor_date: pd.Timestamp) -> pd.DataFrame:
    orders = _orders_index()
    weekly = _weekly_series()

    available = orders[orders["parent_category"] == parent_category]
    if available.empty:
        raise HTTPException(status_code=400, detail=f"No SARIMAX model found for category '{parent_category}'. Run the pipeline to train models.")

    regions = sorted(available["region"].unique())
    history = weekly[weekly["parent_category"] == parent_category]
    if history.empty:
        raise HTTPException(status_code=400, detail=f"No training history for category '{parent_category}'.")

    last_week = history["week_start"].max()
    if pd.isna(last_week):
        raise HTTPException(status_code=500, detail="Invalid week_start in weekly_series.csv")
    last_week = pd.Timestamp(last_week).normalize()
    anchor_date = pd.Timestamp(anchor_date).normalize()
    anchor_week_start = anchor_date - pd.Timedelta(days=anchor_date.dayofweek)
    base_week_start = max(last_week, anchor_week_start)

    future_weeks = pd.date_range(base_week_start + pd.Timedelta(weeks=1), periods=periods, freq="W-MON")
    base = pd.DataFrame({"week_start": future_weeks, "parent_category": parent_category})

    frames = []
    for region in regions:
        chunk = base.copy()
        chunk["region"] = region
        frames.append(chunk)
    future = pd.concat(frames, ignore_index=True)

    calendar = _build_calendar_features(future["week_start"])
    future = future.merge(calendar, on="week_start", how="left")
    future["cat_season_multiplier"] = _apply_cat_season_multiplier(future)


    rows = []
    for region in regions:
        model_row = available[available["region"] == region]
        if model_row.empty:
            continue
        model_key = str(model_row["model_key"].iloc[0])
        model_fit = _load_model(model_key)

        region_future = future[future["region"] == region].copy()
        exog = region_future[EXOG_COLS].values
        preds = model_fit.get_forecast(steps=periods, exog=exog).predicted_mean
        preds = np.maximum(np.asarray(preds, dtype=float), 0.0)

        for idx, week_start in enumerate(region_future["week_start"].tolist()):
            rows.append(
                {
                    "week_start": week_start.strftime("%Y-%m-%d"),
                    "region": region,
                    "sarimax_forecast": float(preds[idx]),
                }
            )

    return pd.DataFrame(rows)


def _region_shares(region_totals: pd.Series) -> Dict[str, float]:
    total = float(region_totals.sum())
    if total <= 0:
        return {region: 0.0 for region in region_totals.index}
    return {region: float(value / total) for region, value in region_totals.items()}


def _allocate_by_shares(total: int, shares: Dict[str, float]) -> Dict[str, int]:
    if total <= 0:
        return {region: 0 for region in shares.keys()}
    raw = {region: total * share for region, share in shares.items()}
    base = {region: int(np.floor(value)) for region, value in raw.items()}
    remainder = total - sum(base.values())
    if remainder > 0 and raw:
        ranked = sorted(
            ((raw[region] - base[region], region) for region in raw.keys()),
            reverse=True,
        )
        for i in range(remainder):
            base[ranked[i % len(ranked)][1]] += 1
    return base


def _allocate_by_warehouse(
    total_quantity: int,
    warehouses: Dict[str, WarehouseSpec],
    region_shares: Dict[str, float],
) -> tuple[Dict[str, int], Dict[str, int]]:
    if total_quantity <= 0:
        empty = {name: 0 for name in warehouses.keys()}
        return empty, empty

    region_to_wh: Dict[str, List[str]] = {}
    for name, spec in warehouses.items():
        region = spec.region
        region_to_wh.setdefault(region, []).append(name)

    for region in region_to_wh.keys():
        if region not in region_shares:
            raise HTTPException(
                status_code=400,
                detail=f"warehouse region not found in forecast: {region}",
            )

    desired = {}
    for region, names in region_to_wh.items():
        share = region_shares.get(region, 0.0)
        if not names:
            continue
        per_wh = share / len(names)
        for name in names:
            desired[name] = total_quantity * per_wh

    final_stock: Dict[str, int] = {}
    for name, spec in warehouses.items():
        target = int(np.floor(desired.get(name, 0.0)))
        stock_level = spec.stock_level
        if target < stock_level:
            target = stock_level
        if target > spec.capacity:
            target = spec.capacity
        final_stock[name] = target

    remainder = total_quantity - sum(final_stock.values())
    if remainder < 0:
        raise HTTPException(
            status_code=400,
            detail="stock_level exceeds total quantity allocation",
        )

    if remainder > 0:
        candidates = []
        for name, spec in warehouses.items():
            if final_stock[name] < spec.capacity:
                gap = desired.get(name, 0.0) - final_stock[name]
                candidates.append((gap, name))
        candidates.sort(reverse=True)

        if not candidates:
            raise HTTPException(
                status_code=400,
                detail="insufficient capacity to allocate quantity",
            )

        idx = 0
        while remainder > 0:
            gap, name = candidates[idx % len(candidates)]
            if final_stock[name] < warehouses[name].capacity:
                final_stock[name] += 1
                remainder -= 1
            idx += 1
            if idx > len(candidates) * (total_quantity + 1):
                break

    if remainder > 0:
        raise HTTPException(
            status_code=400,
            detail="insufficient capacity to allocate quantity",
        )

    add_by_warehouse = {
        name: max(0, final_stock[name] - warehouses[name].stock_level)
        for name in final_stock.keys()
    }
    return add_by_warehouse, final_stock


def _validate_inputs(
    warehouses: Dict[str, WarehouseSpec],
    transport_cost: Dict[str, float],
    holding_cost: Dict[str, float],
    regions: List[str],
) -> None:
    warehouse_ids = set(warehouses.keys())
    if set(holding_cost.keys()) != warehouse_ids:
        raise HTTPException(status_code=400, detail="holding_cost keys must match warehouses")
    if set(transport_cost.keys()) != warehouse_ids:
        raise HTTPException(status_code=400, detail="transport_cost keys must match warehouses")

    for name, spec in warehouses.items():
        if spec.stock_level > spec.capacity:
            raise HTTPException(
                status_code=400,
                detail=f"stock_level exceeds capacity for warehouse {name}",
            )
        if spec.region not in regions:
            raise HTTPException(
                status_code=400,
                detail=f"warehouse region not found in forecast: {spec.region}",
            )


@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/forecast/optimization", response_model=ForecastResponse)
def forecast_and_optimize(request: ForecastRequest) -> ForecastResponse:
    parent_category = _validate_parent_category(request.category)
    warehouses = _normalize_warehouse_regions(request.warehouses)

    forecast_df = _forecast_sarimax(parent_category, request.period, pd.Timestamp(request.forecast_date))
    if forecast_df.empty:
        raise HTTPException(status_code=500, detail="Forecast generation failed")

    regions = sorted(forecast_df["region"].unique().tolist())
    _validate_inputs(warehouses, request.transport_cost, request.holding_cost, regions)


    region_totals = forecast_df.groupby("region")["sarimax_forecast"].sum()
    demand_by_region = {region: float(value) for region, value in region_totals.items()}
    region_shares = _region_shares(region_totals)
    region_percentages = {region: share * 100.0 for region, share in region_shares.items()}
    allocation_by_region = _allocate_by_shares(request.countity, region_shares)

    total_stock = sum(spec.stock_level for spec in warehouses.values())
    total_capacity = sum(spec.capacity for spec in warehouses.values())
    total_quantity = total_stock + request.countity
    if total_quantity > total_capacity:
        raise HTTPException(
            status_code=400,
            detail="countity exceeds total available capacity",
        )

    product = {
        "demand": allocation_by_region,
        "holding_cost": request.holding_cost,
        "total_quantity": total_quantity,
    }

    ilp_start = time.perf_counter()
    ilp_result = run_exact_ilp_solver(
        product=product,
        warehouses={
            k: {
                "capacity": v.capacity,
                "stock_level": v.stock_level,
                "region": v.region,
            }
            for k, v in warehouses.items()
        },
        transport_cost=request.transport_cost,
        holding_cost=request.holding_cost,
        demand_by_region=demand_by_region,
    )
    ilp_runtime = time.perf_counter() - ilp_start

    add_by_warehouse = ilp_result.get("add_by_warehouse", {})
    final_stock_by_warehouse = ilp_result.get("final_stock_by_warehouse", {})

    optimization_methods = run_optimization_comparison(
        product=product,
        warehouses={
            k: {
                "capacity": v.capacity,
                "stock_level": v.stock_level,
                "region": v.region,
            }
            for k, v in warehouses.items()
        },
        transport_cost=request.transport_cost,
        holding_cost=request.holding_cost,
        demand_by_region=demand_by_region,
        genetic_result=None,
        genetic_runtime_seconds=None,
    )

    return ForecastResponse(
        parent_category=parent_category,
        period_weeks=request.period,
        forecast=[ForecastItem(**row) for row in forecast_df.to_dict(orient="records")],
        region_percentages=region_percentages,
        allocation_by_region=allocation_by_region,
        allocation_by_warehouse=add_by_warehouse,
        final_stock_by_warehouse=final_stock_by_warehouse,
        genetic=ilp_result,
        optimization_methods=optimization_methods,
    )
