"""Run optimization methods and print a metrics table."""

from pathlib import Path
import json
import sys
import argparse

try:
    from .Genitic import run_optimization_comparison, run_exact_ilp_solver, _allocate_region_targets, _region_shares, fitness, _max_expected_holding_cost, _max_expected_transfer_cost, brute_force_verify_small_instance
except ImportError:
    sys.path.append(str(Path(__file__).resolve().parent))
    from Genitic import run_optimization_comparison, run_exact_ilp_solver, _allocate_region_targets, _region_shares, fitness, _max_expected_holding_cost, _max_expected_transfer_cost, brute_force_verify_small_instance


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "app_config.json"


def _load_warehouses():
    raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    warehouses = {}
    transport_cost = {}
    holding_cost = {}

    for wh in raw.get("warehouses", []):
        wh_id = wh.get("id")
        if not wh_id:
            continue
        warehouses[wh_id] = {
            "capacity": int(wh.get("capacity", 0)),
            "stock_level": int(wh.get("stockLevel", 0)),
            "region": wh.get("region"),
        }
        transport_cost[wh_id] = float(wh.get("transportCost", 0))
        holding_cost[wh_id] = float(wh.get("holdingCost", 0))

    regions = sorted({spec.get("region") for spec in warehouses.values() if spec.get("region")})
    return warehouses, transport_cost, holding_cost, regions


def _sample_demand_by_region(regions):
    return {region: 100.0 for region in regions} if regions else {}


def _allocate_additional_units(demand_by_region, total_units):
    if not demand_by_region:
        return {}
    shares = _region_shares(demand_by_region)
    return _allocate_region_targets(total_units, shares)


def _format_table(results, warehouses, transport_cost, holding_cost, demand_by_region):
    # Display forecast demand per macro-region
    def _normalize_region_local(r):
        if not r:
            return "unknown"
        s = str(r).lower()
        # check more specific tokens first to avoid substring collisions
        if "ouest" in s or "west" in s:
            return "ouest"
        if "centre" in s or "center" in s or "north" in s:
            return "north"
        if "est" in s or "east" in s:
            return "est"
        if "sud" in s or "south" in s:
            return "sud"
        return s
    display_regions = ["ouest", "est", "north", "sud"]
    demand_display = {r: 0 for r in display_regions}
    for r, q in (demand_by_region or {}).items():
        demand_display[_normalize_region_local(r)] = demand_display.get(_normalize_region_local(r), 0) + int(round(float(q)))
    demand_str = ", ".join(f"{r}:{demand_display.get(r,0)}" for r in display_regions)
    print(f"Demand forecast: {demand_str}")
    print("| Method            |    Total Cost | Service Level | Fitness | Runtime (s) | Allocation by Region |")
    print("| ----------------- | ------------: | ------------: | ------: | ----------: | -------------------- |")
    max_hold = _max_expected_holding_cost(warehouses, holding_cost)
    max_trans = _max_expected_transfer_cost(warehouses, transport_cost)
    for row in results:
        cost = f"{int(round(row['total_cost'])):,} DZD"
        service = f"{row['service_level'] * 100:.0f}%"
        runtime = f"{row['runtime_seconds']:.3f}"
        # compute per-region allocation (added units) from final stock by warehouse when available
        def _normalize_region_local(r):
            if not r:
                return "unknown"
            s = str(r).lower()
            # check more specific tokens first to avoid substring collisions
            if "ouest" in s or "west" in s:
                return "ouest"
            if "centre" in s or "center" in s or "north" in s:
                return "north"
            if "est" in s or "east" in s:
                return "est"
            if "sud" in s or "south" in s:
                return "sud"
            return s
        display_regions = ["ouest", "est", "north", "sud"]
        allocation_by_region = {r: 0 for r in display_regions}
        fitness_val = "-"

        # Prefer exact fitness computation from final individual if available
        indiv = row.get("final_stock_by_warehouse") or row.get("final_stock")
        if indiv is not None:
            try:
                fval = fitness(indiv, warehouses, transport_cost, holding_cost, demand_by_region, max_hold, max_trans)
                fitness_val = f"{fval:.4f}"
                # compute added units per region: max(0, final - initial)
                for wid, final_q in (indiv.items()):
                    try:
                        init_q = int(warehouses.get(wid, {}).get("stock_level", 0))
                        final_q_int = int(round(float(final_q)))
                        added = max(0, final_q_int - init_q)
                    except Exception:
                        added = 0
                    region = warehouses.get(wid, {}).get("region")
                    norm = _normalize_region_local(region)
                    if norm in allocation_by_region:
                        allocation_by_region[norm] += added
                    else:
                        # if unexpected region, add under its normalized key
                        allocation_by_region[norm] = allocation_by_region.get(norm, 0) + added
            except Exception:
                fitness_val = "err"
        else:
            # Fall back to using reported holding/transfer/service values if present
            service_level = row.get("service_level")
            holding_value = row.get("holding_cost_value")
            transfer_value = row.get("transfer_cost_value")
            if service_level is not None and holding_value is not None and transfer_value is not None:
                h_norm = min(holding_value / max_hold, 1.0) if max_hold > 0 else 0.0
                t_norm = min(transfer_value / max_trans, 1.0) if max_trans > 0 else 0.0
                fval = 0.7 * float(service_level) - 0.2 * float(h_norm) - 0.1 * float(t_norm)
                fitness_val = f"{fval:.4f}"

        alloc_str = ", ".join(f"{r}:{allocation_by_region.get(r,0)}" for r in display_regions)
        print(f"| {row['method']:<16} | {cost:>12} | {service:>12} | {fitness_val:>6} | {runtime:>10} | {alloc_str:>20} |")


def _reduced_bruteforce_check(warehouses, transport_cost, holding_cost, demand_by_region):
    # Use all warehouses from the config, but scale capacities down to create a small synthetic instance
    reduced_ids = list(warehouses.keys())
    reduced_warehouses = {}
    for wid in reduced_ids:
        spec = warehouses[wid]
        stock = int(spec.get("stock_level", 0))
        # shrink capacities aggressively to keep brute-force feasible
        tiny_capacity = min(max(stock + 2, 2), 8)
        reduced_warehouses[wid] = {
            "capacity": tiny_capacity,
            "stock_level": min(stock, tiny_capacity),
            "region": spec.get("region"),
        }
    reduced_transport = {wid: transport_cost[wid] for wid in reduced_ids}
    reduced_holding = {wid: holding_cost[wid] for wid in reduced_ids}
    reduced_regions = sorted({spec.get("region") for spec in reduced_warehouses.values() if spec.get("region")})
    reduced_demand = {region: float(demand_by_region.get(region, 0.0)) for region in reduced_regions}
    total_stock = sum(spec.get("stock_level", 0) for spec in reduced_warehouses.values())
    product = {
        "demand": reduced_demand,
        "holding_cost": reduced_holding,
        # small extra units to allocate in the reduced instance
        "total_quantity": total_stock + 6,
    }
    brute = brute_force_verify_small_instance(product, reduced_warehouses, reduced_transport, reduced_holding, reduced_demand, step=1, max_combinations=1000000)
    if brute.get("status") != "OK":
        return brute

    max_hold = _max_expected_holding_cost(reduced_warehouses, reduced_holding)
    max_trans = _max_expected_transfer_cost(reduced_warehouses, reduced_transport)
    best_fit = brute.get("best_fitness", 0.0)
    ilp_result = run_exact_ilp_solver(product, reduced_warehouses, reduced_transport, reduced_holding, reduced_demand)
    ilp_individual = ilp_result.get("final_stock_by_warehouse") or {}
    ilp_fit = fitness(ilp_individual, reduced_warehouses, reduced_transport, reduced_holding, reduced_demand, max_hold, max_trans)
    return {
        "status": "OK",
        "brute_force_best_fitness": best_fit,
        "ilp_fitness": ilp_fit,
        "solver_status": ilp_result.get("solver_status"),
        "provably_optimal": abs(ilp_fit - best_fit) < 1e-9,
        "evaluations": brute.get("evaluations", 0),
        "warehouses": reduced_ids,
    }


def _write_14_warehouse_json(
    warehouses, transport_cost, holding_cost, out_path=ROOT / "reduced_14_warehouses.json", scale_factor=2.0, stock_add=50
):
    """Write first 14 warehouses to JSON, scaling capacities and stock levels.

    - `scale_factor` multiplies the original capacities and stock levels.
    - `stock_add` adds extra stock after scaling to make quantities noticeably bigger.
    """
    ids = list(warehouses.keys())[:14]
    payload = {"warehouses": []}
    for wid in ids:
        spec = warehouses[wid]
        orig_capacity = int(spec.get("capacity", 0))
        orig_stock = int(spec.get("stock_level", 0))
        new_capacity = max(1, int(round(orig_capacity * float(scale_factor))))
        # ensure stock is not larger than capacity
        new_stock = min(new_capacity, int(round(orig_stock * float(scale_factor))) + int(stock_add))
        payload["warehouses"].append(
            {
                "id": wid,
                "capacity": new_capacity,
                "stockLevel": new_stock,
                "region": spec.get("region"),
                "transportCost": float(transport_cost.get(wid, 0.0)),
                "holdingCost": float(holding_cost.get(wid, 0.0)),
            }
        )
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare optimization methods")
    parser.add_argument(
        "--demand",
        "-d",
        help="Override demand forecast, format: ouest:850,est:900,north:1400,sud:200",
        default=None,
    )
    args = parser.parse_args()

    REDUCED_PATH = ROOT / "reduced_14_warehouses.json"

    # If a reduced file exists, load it directly and do not modify it.
    if REDUCED_PATH.exists():
        raw = json.loads(REDUCED_PATH.read_text(encoding="utf-8"))
        warehouses = {}
        transport_cost = {}
        holding_cost = {}
        for wh in raw.get("warehouses", []):
            wh_id = wh.get("id")
            if not wh_id:
                continue
            warehouses[wh_id] = {
                "capacity": int(wh.get("capacity", 0)),
                "stock_level": int(wh.get("stockLevel", 0)),
                "region": wh.get("region"),
            }
            transport_cost[wh_id] = float(wh.get("transportCost", 0))
            holding_cost[wh_id] = float(wh.get("holdingCost", 0))

        regions = sorted({spec.get("region") for spec in warehouses.values() if spec.get("region")})
        print(f"Loaded reduced warehouses from: {REDUCED_PATH}")
    else:
        warehouses, transport_cost, holding_cost, regions = _load_warehouses()
    demand_by_region = _sample_demand_by_region(regions)
    # If user provided a demand override, parse and use it
    if args.demand:
        try:
            parts = [p.strip() for p in args.demand.split(",") if p.strip()]
            override = {}
            for p in parts:
                k, v = p.split(":")
                override[k.strip()] = float(v.strip())
            demand_by_region = override
        except Exception:
            print("Failed to parse --demand override; using default forecast")

    # Use the forecast demand per region as the product demand so all methods
    # receive the same input demand_by_region. Set total_quantity to the sum
    # of forecasted demand so solvers attempt to allocate to meet the forecast
    # (subject to capacity limits).
    total_stock = sum(spec.get("stock_level", 0) for spec in warehouses.values())
    total_forecast = int(round(sum(float(v) for v in (demand_by_region or {}).values())))
    planned_new_units = max(0, total_forecast - total_stock)
    allocation_by_region = _allocate_additional_units(demand_by_region, planned_new_units)

    # Treat the forecast as additional units to allocate on top of current stock
    # so that `total_quantity = total_stock + total_forecast` and methods will
    # attempt to allocate `planned_new_units = total_forecast` across regions.
    product = {
        "demand": demand_by_region,
        "holding_cost": holding_cost,
        "total_quantity": total_stock + total_forecast,
    }

    # Using reduced_14_warehouses.json directly when present; do not modify it.

    results = run_optimization_comparison(
        product=product,
        warehouses=warehouses,
        transport_cost=transport_cost,
        holding_cost=holding_cost,
        demand_by_region=demand_by_region,
    )

    # Run a brute-force verifier only if the instance is small enough for comparison.
    brute = brute_force_verify_small_instance(product, warehouses, transport_cost, holding_cost, demand_by_region, step=1, max_combinations=50000)
    if brute.get("status") == "OK":
        max_hold = _max_expected_holding_cost(warehouses, holding_cost)
        max_trans = _max_expected_transfer_cost(warehouses, transport_cost)
        brute_individual = brute.get("best_individual") or {}
        brute_fit = fitness(brute_individual, warehouses, transport_cost, holding_cost, demand_by_region, max_hold, max_trans)
        for row in results:
            if row.get("method") == "Exact ILP":
                row["brute_force_best_fitness"] = brute_fit
                ilp_individual = row.get("final_stock_by_warehouse") or row.get("final_stock")
                if ilp_individual is not None:
                    ilp_fit = fitness(ilp_individual, warehouses, transport_cost, holding_cost, demand_by_region, max_hold, max_trans)
                    row["provably_optimal"] = abs(ilp_fit - brute_fit) < 1e-9
                break

    reduced = _reduced_bruteforce_check(warehouses, transport_cost, holding_cost, demand_by_region)
    if reduced.get("status") == "OK":
        print(
            f"\nReduced brute-force check on warehouses {reduced['warehouses']}: "
            f"brute={reduced['brute_force_best_fitness']:.4f}, "
            f"ilp={reduced['ilp_fitness']:.4f}, "
            f"solver={reduced['solver_status']}, "
            f"provably_optimal={'yes' if reduced['provably_optimal'] else 'no'}"
        )

    _format_table(results, warehouses, transport_cost, holding_cost, demand_by_region)
