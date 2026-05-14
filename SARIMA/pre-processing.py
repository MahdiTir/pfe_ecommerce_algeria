from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT_DIR / "data" / "ecommerce_algerie_2024_2025_version10mai.csv"
REGIONS_PATH = ROOT_DIR / "wilayas_regions.txt"
OUTPUT_CATEGORY_REGION_PATH = ROOT_DIR / "data" / "weekly_demand_categorie_region.csv"
OUTPUT_PRODUIT_REGION_PATH = ROOT_DIR / "data" / "weekly_demand_produit_region.csv"

DATE_COL = "date expédition"
CATEGORY_COL = "Categorie"
PRODUIT_COL = "Produit"
REGION_SOURCE_COL = "destination wilaya"
STATUS_COL = "dernier statut"
REGION_COL = "region"
DEMAND_COL = "demand"

REGION_NAME_MAP = {
	"centre": "NORTH",
	"est": "EAST",
	"ouest": "WEST",
	"sud": "SOUTH",
}


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
		mapped_region = REGION_NAME_MAP.get(region.strip().lower())
		if mapped_region is None:
			continue
		for wilaya in wilayas:
			region_map[_normalize_text(wilaya)] = mapped_region
	return region_map


def _find_column(columns: list[str], target_normalized: str) -> str:
	for column in columns:
		if _normalize_text(column) == target_normalized:
			return column
	raise KeyError(f"Missing required column: {target_normalized}")


def _inspect_data(df: pd.DataFrame) -> None:
	print(f"Shape: {df.shape}")
	print("\nDtypes:")
	print(df.dtypes)
	print("\nMissing values per column:")
	print(df.isna().sum())
	print("\nSample rows:")
	print(df.head(5).to_string(index=False))
	if STATUS_COL in df.columns:
		print("\nDelivery status distribution:")
		print(df[STATUS_COL].value_counts(dropna=False).head(20))


def main() -> None:
	df = pd.read_csv(DATA_PATH)
	_inspect_data(df)

	category_col = _find_column(df.columns.tolist(), "categorie")
	produit_col = _find_column(df.columns.tolist(), "produit")
	date_col = _find_column(df.columns.tolist(), "date expedition")
	wilaya_col = _find_column(df.columns.tolist(), "destination wilaya")

	region_map = _load_regions_map()

	df = df.dropna(subset=[date_col, category_col, wilaya_col]).copy()
	df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
	df = df.dropna(subset=[date_col]).copy()

	df[REGION_COL] = (
		df[wilaya_col]
		.map(_normalize_text)
		.map(region_map)
		.fillna("UNKNOWN")
	)
	region_counts = df[REGION_COL].value_counts(dropna=False)
	print("\nRegion value counts:")
	print(region_counts)

	unknown_count = int((df[REGION_COL] == "UNKNOWN").sum())
	if unknown_count:
		print(f"Warning: {unknown_count} rows have unknown region mappings")

	df = df.set_index(date_col)

	weekly_demand = (
		df.groupby([pd.Grouper(freq="W-MON"), category_col, REGION_COL], dropna=False)
		.size()
		.reset_index(name=DEMAND_COL)
		.rename(columns={category_col: CATEGORY_COL})
		.sort_values([DATE_COL, CATEGORY_COL, REGION_COL])
	)
	weekly_demand_produit = (
		df.groupby([pd.Grouper(freq="W-MON"), produit_col, REGION_COL], dropna=False)
		.size()
		.reset_index(name=DEMAND_COL)
		.rename(columns={produit_col: PRODUIT_COL})
		.sort_values([DATE_COL, PRODUIT_COL, REGION_COL])
	)

	OUTPUT_CATEGORY_REGION_PATH.parent.mkdir(parents=True, exist_ok=True)
	weekly_demand.to_csv(OUTPUT_CATEGORY_REGION_PATH, index=False)
	weekly_demand_produit.to_csv(OUTPUT_PRODUIT_REGION_PATH, index=False)

	print(f"\nWeekly demand (Categorie x region) shape: {weekly_demand.shape}")
	print(weekly_demand.head(5).to_string(index=False))
	print(f"\nWeekly demand (Produit x region) shape: {weekly_demand_produit.shape}")
	print(weekly_demand_produit.head(5).to_string(index=False))
	print(f"\nSaved category-region weekly demand to {OUTPUT_CATEGORY_REGION_PATH}")
	print(f"Saved product-region weekly demand to {OUTPUT_PRODUIT_REGION_PATH}")

	if len(region_counts.index.intersection(["NORTH", "WEST", "EAST", "SOUTH"])) == 4 and unknown_count == 0:
		print("\nConfirmation: Region column created with 4 values")
		print("Confirmation: Weekly aggregation done for both granularities")
		print("Confirmation: Both CSVs saved and ready for Phase 2")
	else:
		print("\nWarning: region mapping did not resolve cleanly to the expected 4 values")

	print("\nPreprocessing completed using all delivery statuses (no status-based filtering applied).")


if __name__ == "__main__":
	main()
