"""Run optimization methods and print a metrics table."""

from pathlib import Path
import json
import sys
import argparse

try:
    from .Genitic import (
        run_optimization_comparison,
        run_exact_ilp_solver,
        _allocate_region_targets,
        _region_shares,
        fitness,
        _max_expected_holding_cost,
        _max_expected_transfer_cost,
        brute_force_verify_small_instance,
    )
except ImportError:
    sys.path.append(str(Path(__file__).resolve().parent))
    from Genitic import (
        run_optimization_comparison,
        run_exact_ilp_solver,
        _allocate_region_targets,
        _region_shares,
        fitness,
        _max_expected_holding_cost,
        _max_expected_transfer_cost,
        brute_force_verify_small_instance,
    )


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "app_config.json"

# ---------------------------------------------------------------------------
# Default demand forecast — edit these values to change the baseline forecast.
# Can be overridden at runtime with --demand  WEST:850,EAST:900,NORTH:1400,SOUTH:200
# ---------------------------------------------------------------------------
DEFAULT_FORECAST = {
    "WEST": 850.0,
    "EAST": 900.0,
    "NORTH": 1400.0,
    "SOUTH": 200.0,
}

_DISPLAY_REGIONS = ["WEST", "EAST", "NORTH", "SOUTH"]


def _normalize_region_local(r):
    """Map a raw region string to one of the four canonical keys (EAST, NORTH, SOUTH, WEST)."""
    if not r:
        return "unknown"
    s = str(r).strip().upper()
    aliases = {
        "CENTRE": "NORTH",
        "CENTER": "NORTH",
        "EST": "EAST",
        "OUEST": "WEST",
        "SUD": "SOUTH",
    }
    if s in aliases:
        return aliases[s]
    if s in _DISPLAY_REGIONS:
        return s
    lowered = str(r).lower()
    if "ouest" in lowered or "west" in lowered:
        return "WEST"
    if "centre" in lowered or "center" in lowered or "north" in lowered:
        return "NORTH"
    if "est" in lowered or "east" in lowered:
        return "EAST"
    if "sud" in lowered or "south" in lowered:
        return "SOUTH"
    return s


# ---------------------------------------------------------------------------

def _load_warehouses():
    raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    warehouses = {}
    transport_cost = {}
    holding_cost = {}

    for wh in raw.get("warehouses", []):
        wh_id = wh.get("id")
        if not wh_id:
            continue
        # Normalize region names to match demand forecast
        raw_region = wh.get("region")
        normalized_region = _normalize_region_local(raw_region) if raw_region else None
        
        warehouses[wh_id] = {
            "capacity": int(wh.get("capacity", 0)),
            "stock_level": int(wh.get("stockLevel", 0)),
            "region": normalized_region,
        }
        transport_cost[wh_id] = float(wh.get("transportCost", 0))
        holding_cost[wh_id] = float(wh.get("holdingCost", 0))

    regions = sorted({spec.get("region") for spec in warehouses.values() if spec.get("region")})
    return warehouses, transport_cost, holding_cost, regions


def _sample_demand_by_region(regions):
    """Return the default forecast, filtered to regions that actually exist in
    the warehouse config.  Falls back to 100 for any region not in DEFAULT_FORECAST."""
    return {region: DEFAULT_FORECAST.get(region, 100.0) for region in regions} if regions else {}


def _allocate_additional_units(demand_by_region, total_units):
    if not demand_by_region:
        return {}
    shares = _region_shares(demand_by_region)
    return _allocate_region_targets(total_units, shares)


def _format_table(results, warehouses, transport_cost, holding_cost, demand_by_region, show_warehouse_detail=False):
    # Display forecast demand per macro-region
    demand_display = {r: 0 for r in _DISPLAY_REGIONS}
    for r, q in (demand_by_region or {}).items():
        key = _normalize_region_local(r)
        demand_display[key] = demand_display.get(key, 0) + int(round(float(q)))
    demand_str = ", ".join(f"{r}:{demand_display.get(r, 0)}" for r in _DISPLAY_REGIONS)
    print(f"\nDemand forecast: {demand_str}")
    print("| Method            |    Total Cost | Service Level | Fitness | Runtime (s) |   Stock by Region    |")
    print("| ----------------- | ------------: | ------------: | ------: | ----------: | -------------------- |")

    max_hold = _max_expected_holding_cost(warehouses, holding_cost)
    max_trans = _max_expected_transfer_cost(warehouses, transport_cost)

    for row in results:
        cost    = f"{int(round(row['total_cost'])):,} DZD"
        service = f"{row['service_level'] * 100:.0f}%"
        runtime = f"{row['runtime_seconds']:.3f}"

        # FIX: display_regions defined once (module level) — no duplicate definition here
        allocation_by_region = {r: 0 for r in _DISPLAY_REGIONS}
        fitness_val = "-"

        indiv = row.get("final_stock_by_warehouse") or row.get("final_stock")
        if indiv is not None:
            try:
                fval = fitness(
                    indiv, warehouses, transport_cost, holding_cost,
                    demand_by_region, max_hold, max_trans,
                )
                fitness_val = f"{fval:.4f}"

                for wid, final_q in indiv.items():
                    try:
                        init_q      = int(warehouses.get(wid, {}).get("stock_level", 0))
                        final_q_int = int(round(float(final_q)))
                        added       = max(0, final_q_int - init_q)
                    except Exception:
                        added       = 0
                        final_q_int = 0
                        init_q      = 0
                    region = warehouses.get(wid, {}).get("region")
                    norm   = _normalize_region_local(region)
                    # Show final stock per region (not just added units).
                    # When existing stock already covers demand, added=0 for
                    # every warehouse, making an "added only" column misleading.
                    allocation_by_region[norm] = allocation_by_region.get(norm, 0) + final_q_int

            except Exception:
                fitness_val = "err"
        else:
            # FIX: fallback fitness uses the same alpha=0.5 weights as the real
            # fitness function, not the wrong 0.7/0.2/0.1 split that was here before.
            service_level  = row.get("service_level")
            holding_value  = row.get("holding_cost_value")
            transfer_value = row.get("transfer_cost_value")
            if service_level is not None and holding_value is not None and transfer_value is not None:
                total_cost_value = float(holding_value) + float(transfer_value)
                max_total        = float(max_hold) + float(max_trans)
                total_norm       = min(total_cost_value / max_total, 1.0) if max_total > 0 else 0.0
                fval             = 0.5 * float(service_level) - 0.5 * total_norm
                fitness_val      = f"{fval:.4f}"

        alloc_str = ", ".join(f"{r}:{allocation_by_region.get(r, 0)}" for r in _DISPLAY_REGIONS)
        print(
            f"| {row['method']:<16} | {cost:>12} | {service:>12} | "
            f"{fitness_val:>6} | {runtime:>10} | {alloc_str:>20} |"
        )
        
        # Show warehouse-level details if requested
        if show_warehouse_detail and indiv is not None:
            print(f"  >> Warehouse allocation for {row['method']}:")
            for wid in sorted(indiv.keys()):
                final_q = int(round(float(indiv.get(wid, 0))))
                if final_q > 0:  # Only show warehouses with allocation
                    wh_region = warehouses.get(wid, {}).get("region", "unknown")
                    wh_capacity = warehouses.get(wid, {}).get("capacity", 0)
                    utilization = (final_q / wh_capacity * 100) if wh_capacity > 0 else 0
                    print(f"     {wid:20} [{wh_region:>6}]: {final_q:>6} units ({utilization:>5.1f}% of capacity)")
            print()


def _reduced_bruteforce_check(warehouses, transport_cost, holding_cost, demand_by_region):
    """Verify the ILP solver against brute-force on a tiny synthetic instance."""
    reduced_ids       = list(warehouses.keys())
    reduced_warehouses = {}
    for wid in reduced_ids:
        spec          = warehouses[wid]
        # FIX: set stock_level=0 in the reduced instance so total_add > 0 and
        # the brute-force/ILP actually have units to allocate and compare.
        # Using real stock levels caused total_add=0 → ILP "Infeasible" because
        # the equality constraint  sum(add)==0  clashed with non-zero demands.
        tiny_capacity = max(4, min(8, int(spec.get("capacity", 8))))
        reduced_warehouses[wid] = {
            "capacity":    tiny_capacity,
            "stock_level": 0,
            "region":      spec.get("region"),
        }

    reduced_transport = {wid: transport_cost[wid] for wid in reduced_ids}
    reduced_holding   = {wid: holding_cost[wid]   for wid in reduced_ids}
    reduced_regions   = sorted({
        spec.get("region")
        for spec in reduced_warehouses.values()
        if spec.get("region")
    })
    reduced_demand = {r: float(demand_by_region.get(r, 0.0)) for r in reduced_regions}

    # FIX: derive total_quantity from reduced_demand sum instead of hardcoding +6,
    # so the brute-force check actually reflects the forecast proportions.
    total_stock        = sum(spec.get("stock_level", 0) for spec in reduced_warehouses.values())
    reduced_total      = max(total_stock + 2, int(round(sum(reduced_demand.values()))))

    product = {
        "demand":         reduced_demand,
        "holding_cost":   reduced_holding,
        "total_quantity": reduced_total,
    }

    brute = brute_force_verify_small_instance(
        product, reduced_warehouses, reduced_transport, reduced_holding,
        reduced_demand, step=1, max_combinations=1_000_000,
    )
    if brute.get("status") != "OK":
        return brute

    max_hold  = _max_expected_holding_cost(reduced_warehouses, reduced_holding)
    max_trans = _max_expected_transfer_cost(reduced_warehouses, reduced_transport)
    best_fit  = brute.get("best_fitness", 0.0)

    ilp_result    = run_exact_ilp_solver(
        product, reduced_warehouses, reduced_transport, reduced_holding, reduced_demand,
    )
    ilp_individual = ilp_result.get("final_stock_by_warehouse") or {}
    ilp_fit        = fitness(
        ilp_individual, reduced_warehouses, reduced_transport, reduced_holding,
        reduced_demand, max_hold, max_trans,
    )
    return {
        "status":                "OK",
        "brute_force_best_fitness": best_fit,
        "ilp_fitness":           ilp_fit,
        "solver_status":         ilp_result.get("solver_status"),
        "provably_optimal":      abs(ilp_fit - best_fit) < 1e-9,
        "evaluations":           brute.get("evaluations", 0),
        "warehouses":            reduced_ids,
    }


def _write_14_warehouse_json(
    warehouses,
    transport_cost,
    holding_cost,
    out_path=ROOT / "reduced_14_warehouses.json",
    scale_factor=2.0,
    stock_add=50,
):
    """Write first 14 warehouses to JSON with scaled capacities and stock levels."""
    ids     = list(warehouses.keys())[:14]
    payload = {"warehouses": []}
    for wid in ids:
        spec         = warehouses[wid]
        orig_capacity = int(spec.get("capacity", 0))
        orig_stock    = int(spec.get("stock_level", 0))
        new_capacity  = max(1, int(round(orig_capacity * float(scale_factor))))
        new_stock     = min(new_capacity, int(round(orig_stock * float(scale_factor))) + int(stock_add))
        payload["warehouses"].append({
            "id":            wid,
            "capacity":      new_capacity,
            "stockLevel":    new_stock,
            "region":        spec.get("region"),
            "transportCost": float(transport_cost.get(wid, 0.0)),
            "holdingCost":   float(holding_cost.get(wid, 0.0)),
        })
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out_path


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare optimization methods")
    parser.add_argument(
        "--demand",
        "-d",
        default="WEST:850,EAST:900,NORTH:1400,SOUTH:200",
        help="Demand forecast by region (from SARIMAX), format: WEST:850,EAST:900,NORTH:1400,SOUTH:200",
    )
    parser.add_argument(
        "--quantity",
        "-q",
        type=int,
        default=None,
        help="Total inventory quantity to allocate (seller's budget). If not specified, uses current_stock + total_demand",
    )
    parser.add_argument(
        "--warehouse-detail",
        "-w",
        action="store_true",
        help="Show per-warehouse allocation details",
    )
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        default=None,
        help="Path to custom warehouse configuration JSON file",
    )
    args = parser.parse_args()

    # Load warehouse configuration
    if args.config:
        CONFIG_FILE = Path(args.config)
    else:
        REDUCED_PATH = ROOT / "reduced_14_warehouses.json"
        CONFIG_FILE = REDUCED_PATH if REDUCED_PATH.exists() else CONFIG_PATH

    if CONFIG_FILE.exists():
        raw = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        warehouses    = {}
        transport_cost = {}
        holding_cost  = {}
        for wh in raw.get("warehouses", []):
            wh_id = wh.get("id")
            if not wh_id:
                continue
            # Normalize region names to match demand forecast
            raw_region = wh.get("region")
            normalized_region = _normalize_region_local(raw_region) if raw_region else None
            
            warehouses[wh_id] = {
                "capacity":    int(wh.get("capacity", 0)),
                "stock_level": int(wh.get("stockLevel", 0)),
                "region":      normalized_region,
            }
            transport_cost[wh_id] = float(wh.get("transportCost", 0))
            holding_cost[wh_id]   = float(wh.get("holdingCost", 0))
        regions = sorted({spec.get("region") for spec in warehouses.values() if spec.get("region")})
        print(f"Loaded warehouses from: {CONFIG_FILE}")
    else:
        warehouses, transport_cost, holding_cost, regions = _load_warehouses()

    # Start with region-filtered default forecast, then apply CLI override
    demand_by_region = _sample_demand_by_region(regions)

    if args.demand:
        try:
            parts    = [p.strip() for p in args.demand.split(",") if p.strip()]
            override = {}
            for p in parts:
                k, v = p.split(":")
                override[k.strip()] = float(v.strip())
            demand_by_region = override
        except Exception:
            print("Failed to parse --demand override; using default forecast")

    total_stock    = sum(spec.get("stock_level", 0) for spec in warehouses.values())
    total_forecast = int(round(sum(float(v) for v in (demand_by_region or {}).values())))

    # total_quantity is the INVENTORY BUDGET (how much to allocate)
    # NOT the demand! The seller decides this independently.
    if args.quantity is not None:
        total_quantity = args.quantity
    else:
        # Default: use existing stock + demand forecast as the budget
        total_quantity = total_stock + total_forecast
    
    product = {
        "demand":         demand_by_region,
        "holding_cost":   holding_cost,
        "total_quantity": total_quantity,  # Seller's inventory budget
    }
    
    print(f"\nInventory Budget: {total_quantity:,} units (Current Stock: {total_stock:,}, Demand Forecast: {total_forecast:,})")

    results = run_optimization_comparison(
        product=product,
        warehouses=warehouses,
        transport_cost=transport_cost,
        holding_cost=holding_cost,
        demand_by_region=demand_by_region,
    )

    # Brute-force verification (only runs if instance is small enough)
    brute = brute_force_verify_small_instance(
        product, warehouses, transport_cost, holding_cost,
        demand_by_region, step=1, max_combinations=50_000,
    )
    if brute.get("status") == "OK":
        max_hold      = _max_expected_holding_cost(warehouses, holding_cost)
        max_trans     = _max_expected_transfer_cost(warehouses, transport_cost)
        brute_individual = brute.get("best_individual") or {}
        brute_fit     = fitness(
            brute_individual, warehouses, transport_cost, holding_cost,
            demand_by_region, max_hold, max_trans,
        )
        for row in results:
            if row.get("method") == "Exact ILP":
                row["brute_force_best_fitness"] = brute_fit
                ilp_individual = row.get("final_stock_by_warehouse") or row.get("final_stock")
                if ilp_individual is not None:
                    ilp_fit = fitness(
                        ilp_individual, warehouses, transport_cost, holding_cost,
                        demand_by_region, max_hold, max_trans,
                    )
                    row["provably_optimal"] = abs(ilp_fit - brute_fit) < 1e-9
                break

    reduced = _reduced_bruteforce_check(warehouses, transport_cost, holding_cost, demand_by_region)
    if reduced.get("status") == "OK":
        print(
            f"\nReduced brute-force check on {len(reduced['warehouses'])} warehouses: "
            f"brute={reduced['brute_force_best_fitness']:.4f}, "
            f"ilp={reduced['ilp_fitness']:.4f}, "
            f"solver={reduced['solver_status']}, "
            f"provably_optimal={'yes' if reduced['provably_optimal'] else 'no'}"
        )
    elif reduced.get("status") == "SKIPPED":
        print(f"\nReduced brute-force check skipped: {reduced.get('reason')}")

    _format_table(results, warehouses, transport_cost, holding_cost, demand_by_region, show_warehouse_detail=args.warehouse_detail)