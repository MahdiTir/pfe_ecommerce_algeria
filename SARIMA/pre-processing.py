from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT_DIR / "data" / "ecommerce_algerie_2024_2025_version10mai.csv"
REGIONS_PATH = ROOT_DIR / "wilayas_regions.txt"
OUTPUT_PATH = ROOT_DIR / "data" / "daily_demand_by_category_region.csv"


def _normalize_text(value: str) -> str:
	text = str(value).strip().lower()
	text = unicodedata.normalize("NFKD", text)
	text = "".join(ch for ch in text if not unicodedata.combining(ch))
	text = re.sub(r"[^a-z0-9]+", " ", text)
	return re.sub(r"\s+", " ", text).strip()


def _load_regions_map() -> dict[str, str]:
	raw_text = REGIONS_PATH.read_text(encoding="utf-8")
	# The file is JSON-like with trailing commas, so clean it before loading.
	cleaned_text = re.sub(r",\s*([}\]])", r"\1", raw_text)
	region_data = json.loads(cleaned_text)

	region_map: dict[str, str] = {}
	for region, wilayas in region_data.items():
		for wilaya in wilayas:
			region_map[_normalize_text(wilaya)] = region
	return region_map


def _find_column(columns: list[str], target_normalized: str) -> str:
	for column in columns:
		if _normalize_text(column) == target_normalized:
			return column
	raise KeyError(f"Missing required column: {target_normalized}")


def main() -> None:
	df = pd.read_csv(DATA_PATH)

	category_col = _find_column(df.columns.tolist(), "categorie")
	date_col = _find_column(df.columns.tolist(), "date expedition")
	wilaya_col = _find_column(df.columns.tolist(), "destination wilaya")

	region_map = _load_regions_map()

	df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
	df = df.dropna(subset=[date_col, category_col, wilaya_col]).copy()

	df["region"] = (
		df[wilaya_col]
		.map(_normalize_text)
		.map(region_map)
		.fillna("unknown")
	)
	df["date"] = df[date_col].dt.date.astype(str)

	daily = (
		df.groupby(["date", category_col, "region"], dropna=False)
		.size()
		.reset_index(name="demand")
		.rename(columns={category_col: "category"})
		.sort_values(["date", "category", "region"])
	)

	OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
	daily.to_csv(OUTPUT_PATH, index=False)

	unknown_count = int((df["region"] == "unknown").sum())
	print(f"Saved {len(daily)} rows to {OUTPUT_PATH}")
	if unknown_count:
		print(f"Warning: {unknown_count} rows have unknown region")


if __name__ == "__main__":
	main()
