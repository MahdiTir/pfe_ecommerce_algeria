import itertools
import random
import time

import numpy as np
try:
    import pulp
except Exception:
    pulp = None


def _normalize_region_key(value):
    return str(value).strip().lower()


def _normalize_region_dict(data):
    normalized = {}
    for region, value in data.items():
        if region is None:
            continue
        key = _normalize_region_key(region)
        normalized[key] = normalized.get(key, 0.0) + float(value)
    return normalized


def _warehouse_bounds(warehouses):
    min_stock = {}
    max_stock = {}
    for name, spec in warehouses.items():
        capacity = int(spec["capacity"])
        stock_level = int(spec.get("stock_level", 0))
        if stock_level < 0:
            stock_level = 0
        if stock_level > capacity:
            stock_level = capacity
        min_stock[name] = stock_level
        max_stock[name] = capacity
    return min_stock, max_stock


def _region_shares(demand):
    total = float(sum(demand.values()))
    if total <= 0:
        return {region: 0.0 for region in demand.keys()}
    return {region: float(qty / total) for region, qty in demand.items()}


def _allocate_region_targets(total_quantity, region_shares):
    if total_quantity <= 0:
        return {region: 0 for region in region_shares.keys()}

    raw = {region: total_quantity * share for region, share in region_shares.items()}
    base = {region: int(np.floor(value)) for region, value in raw.items()}
    remainder = total_quantity - sum(base.values())
    if remainder > 0 and raw:
        ranked = sorted(
            ((raw[region] - base[region], region) for region in raw.keys()),
            reverse=True,
        )
        for i in range(remainder):
            base[ranked[i % len(ranked)][1]] += 1
    return base


def _group_warehouses_by_region(warehouses):
    region_to_wh = {}
    for name, spec in warehouses.items():
        region = spec.get("region")
        if region is None:
            continue
        region = _normalize_region_key(region)
        region_to_wh.setdefault(region, []).append(name)
    return region_to_wh


def _adjust_region_targets(region_targets, warehouses, transport_cost):
    region_to_wh = _group_warehouses_by_region(warehouses)
    missing = [region for region in region_targets.keys() if region not in region_to_wh]
    if not missing:
        return region_targets, None, []

    if not transport_cost:
        return region_targets, None, missing

    fallback_wh = min(transport_cost.items(), key=lambda item: item[1])[0]
    fallback_region = warehouses.get(fallback_wh, {}).get("region")
    if fallback_region is None:
        return region_targets, None, missing

    missing_total = sum(region_targets[region] for region in missing)
    adjusted = dict(region_targets)
    for region in missing:
        adjusted.pop(region, None)
    adjusted[fallback_region] = adjusted.get(fallback_region, 0) + missing_total

    return adjusted, fallback_region, missing


def _unit_cost(warehouse_id, holding_cost, transport_cost):
    return float(holding_cost.get(warehouse_id, 0.0) + transport_cost.get(warehouse_id, 0.0))


def _choose_one_warehouse_per_region(warehouses, holding_cost, transport_cost, strategy="lowest_cost"):
    region_to_wh = _group_warehouses_by_region(warehouses)
    choice = {}
    for region, names in region_to_wh.items():
        if not names:
            continue
        if strategy == "random":
            choice[region] = random.choice(names)
        else:
            choice[region] = min(
                names,
                key=lambda w: _unit_cost(w, holding_cost, transport_cost),
            )
    return choice


def _build_one_per_region_individual(product, warehouses, transport_cost, holding_cost, region_choice):
    min_stock, max_stock = _warehouse_bounds(warehouses)
    demand = _normalize_region_dict(product["demand"])
    total_quantity = int(round(product.get("total_quantity", sum(demand.values()))))
    min_total = sum(min_stock.values())
    if total_quantity < min_total:
        total_quantity = min_total

    region_shares = _region_shares(demand)
    region_targets = _allocate_region_targets(total_quantity, region_shares)
    region_targets, _, _ = _adjust_region_targets(region_targets, warehouses, transport_cost)

    individual = {w: min_stock[w] for w in warehouses.keys()}
    for region, target in region_targets.items():
        w = region_choice.get(region)
        if w is None:
            continue
        current = individual[w]
        add_needed = max(0, target - current)
        add = min(max_stock[w] - current, add_needed)
        individual[w] += add

    remainder = total_quantity - sum(individual.values())
    chosen_wh = list(dict.fromkeys(region_choice.values()))
    if remainder > 0 and chosen_wh:
        sorted_wh = sorted(
            chosen_wh,
            key=lambda w: _unit_cost(w, holding_cost, transport_cost),
        )
        for w in sorted_wh:
            if remainder <= 0:
                break
            capacity = max_stock[w] - individual[w]
            if capacity <= 0:
                continue
            add = min(capacity, remainder)
            individual[w] += add
            remainder -= add
    elif remainder < 0 and chosen_wh:
        remove_needed = -remainder
        sorted_wh = sorted(
            chosen_wh,
            key=lambda w: _unit_cost(w, holding_cost, transport_cost),
            reverse=True,
        )
        for w in sorted_wh:
            if remove_needed <= 0:
                break
            removable = individual[w] - min_stock[w]
            if removable <= 0:
                continue
            remove = min(removable, remove_needed)
            individual[w] -= remove
            remove_needed -= remove

    return individual


def _additional_units(individual, warehouses):
    min_stock, _ = _warehouse_bounds(warehouses)
    return {w: max(0, individual.get(w, 0) - min_stock[w]) for w in warehouses.keys()}


def _compute_total_cost(individual, warehouses, holding_cost, transport_cost):
    add_by_warehouse = _additional_units(individual, warehouses)
    return float(
        sum(
            qty * _unit_cost(w, holding_cost, transport_cost)
            for w, qty in add_by_warehouse.items()
        )
    )


def _service_level(demand_by_region, satisfied_by_region):
    """
    Compute service level as the average of per-region satisfaction fractions
    across the four key macro-regions: 'ouest', 'est', 'north', 'sud'.

    For each region r in that list:
      - map 'north' to 'centre' if no 'north' key exists in the demand
      - fraction_r = min(1.0, satisfied_r / demand_r) if demand_r > 0 else 0.0

    ServiceLevel = (sum fraction_r over the four regions) / 4
    """
    demand_by_region = _normalize_region_dict(demand_by_region)
    satisfied_by_region = _normalize_region_dict(satisfied_by_region)

    regions_of_interest = ["ouest", "est", "north", "sud"]
    total_frac = 0.0
    for r in regions_of_interest:
        # support data that uses 'centre' instead of 'north'
        if r == "north":
            demand = float(demand_by_region.get("north", demand_by_region.get("centre", 0.0)))
            satisfied = float(satisfied_by_region.get("north", satisfied_by_region.get("centre", 0.0)))
        else:
            demand = float(demand_by_region.get(r, 0.0))
            satisfied = float(satisfied_by_region.get(r, 0.0))

        if demand <= 0:
            frac = 0.0
        else:
            frac = min(1.0, satisfied / demand)
        total_frac += frac

    return total_frac / 4.0


def _holding_cost(individual, holding_cost):
    return float(
        sum(
            float(individual.get(w, 0)) * float(holding_cost.get(w, 0.0))
            for w in individual.keys()
        )
    )


def _transfer_cost(add_by_warehouse, transport_cost):
    return float(
        sum(
            float(qty) * float(transport_cost.get(w, 0.0))
            for w, qty in add_by_warehouse.items()
        )
    )


def _max_expected_holding_cost(warehouses, holding_cost):
    return float(
        sum(
            int(spec.get("capacity", 0)) * float(holding_cost.get(w, 0.0))
            for w, spec in warehouses.items()
        )
    )


def _max_expected_transfer_cost(warehouses, transport_cost):
    min_stock, max_stock = _warehouse_bounds(warehouses)
    max_add_units = sum(max_stock[w] - min_stock[w] for w in max_stock.keys())
    max_unit_cost = max((float(cost) for cost in transport_cost.values()), default=0.0)
    return float(max_add_units * max_unit_cost)


def _compute_mt_and_service_level(individual, warehouses, demand_by_region, holding_cost):
    region_units = {}
    region_hold_total = {}
    for w, qty in individual.items():
        region = warehouses.get(w, {}).get("region")
        if region is None:
            continue
        region = _normalize_region_key(region)
        region_units[region] = region_units.get(region, 0.0) + float(qty)
        region_hold_total[region] = region_hold_total.get(region, 0.0) + float(qty) * float(holding_cost.get(w, 0.0))

    demand_by_region = _normalize_region_dict(demand_by_region)
    total_demand = sum(max(0.0, float(value)) for value in demand_by_region.values())
    weighted_service = 0.0
    numerator = 0.0
    denominator = 0.0

    for region, demand in demand_by_region.items():
        demand = float(demand)
        if demand <= 0:
            continue
        units = float(region_units.get(region, 0.0))
        if units > 0:
            weighted_service += min(1.0, units / demand) * demand
        region_hold = region_hold_total.get(region, 0.0)
        if units > 0 and region_hold > 0:
            avg_hold = region_hold / units
            numerator += demand * avg_hold
            denominator += units * avg_hold

    # Compute service level using per-region fractions averaged across four macro-regions
    service_level = _service_level(demand_by_region, region_units)
    mt = numerator / denominator if denominator > 0 else 0.0
    return mt, service_level


def _build_method_result(method, individual, warehouses, transport_cost, holding_cost, demand_by_region, runtime_seconds):
    total_cost = _compute_total_cost(individual, warehouses, holding_cost, transport_cost)
    mt, service_level = _compute_mt_and_service_level(individual, warehouses, demand_by_region, holding_cost)
    add_by_warehouse = _additional_units(individual, warehouses)
    holding_value = _holding_cost(individual, holding_cost)
    transfer_value = _transfer_cost(add_by_warehouse, transport_cost)
    return {
        "method": method,
        "total_cost": float(total_cost),
        "service_level": float(service_level),
        "runtime_seconds": float(runtime_seconds),
        "mt": float(mt),
        "final_stock_by_warehouse": dict(individual),
        "add_by_warehouse": dict(add_by_warehouse),
        "holding_cost_value": float(holding_value),
        "transfer_cost_value": float(transfer_value),
    }


def run_random_search_optimization(
    product,
    warehouses,
    transport_cost,
    holding_cost,
    demand_by_region,
    iterations=200,
    seed=None,
):
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    # Ensure downstream helpers see the forecast demand
    if demand_by_region is not None:
        product = dict(product)
        product["demand"] = demand_by_region

    start = time.perf_counter()
    max_expected_holding_cost = _max_expected_holding_cost(warehouses, holding_cost)
    max_expected_transfer_cost = _max_expected_transfer_cost(warehouses, transport_cost)

    best_individual = None
    best_fitness = float("-inf")

    for _ in range(iterations):
        region_choice = _choose_one_warehouse_per_region(
            warehouses,
            holding_cost,
            transport_cost,
            strategy="random",
        )
        individual = _build_one_per_region_individual(
            product,
            warehouses,
            transport_cost,
            holding_cost,
            region_choice,
        )
        current_fitness = fitness(
            individual,
            warehouses,
            transport_cost,
            holding_cost,
            demand_by_region,
            max_expected_holding_cost,
            max_expected_transfer_cost,
        )
        if current_fitness > best_fitness:
            best_fitness = current_fitness
            best_individual = individual

    if best_individual is None:
        min_stock, _ = _warehouse_bounds(warehouses)
        best_individual = {w: min_stock[w] for w in warehouses.keys()}

    runtime = time.perf_counter() - start
    return _build_method_result(
        "Random Search",
        best_individual,
        warehouses,
        transport_cost,
        holding_cost,
        demand_by_region,
        runtime,
    )


def run_greedy_heuristic(
    product,
    warehouses,
    transport_cost,
    holding_cost,
    demand_by_region,
):
    # Ensure downstream helpers see the forecast demand
    if demand_by_region is not None:
        product = dict(product)
        product["demand"] = demand_by_region

    start = time.perf_counter()
    max_expected_holding_cost = _max_expected_holding_cost(warehouses, holding_cost)
    max_expected_transfer_cost = _max_expected_transfer_cost(warehouses, transport_cost)

    region_to_wh = _group_warehouses_by_region(warehouses)
    regions = [region for region in region_to_wh.keys() if region_to_wh[region]]
    if not regions:
        min_stock, _ = _warehouse_bounds(warehouses)
        individual = {w: min_stock[w] for w in warehouses.keys()}
        runtime = time.perf_counter() - start
        return _build_method_result(
            "Greedy Heuristic",
            individual,
            warehouses,
            transport_cost,
            holding_cost,
            demand_by_region,
            runtime,
        )

    regions = sorted(
        regions,
        key=lambda r: float(demand_by_region.get(r, 0.0)),
        reverse=True,
    )

    base_choice = _choose_one_warehouse_per_region(
        warehouses,
        holding_cost,
        transport_cost,
        strategy="lowest_cost",
    )
    region_choice = {}

    for region in regions:
        best_choice = None
        best_fitness = float("-inf")
        for candidate in region_to_wh[region]:
            temp_choice = dict(base_choice)
            temp_choice.update(region_choice)
            temp_choice[region] = candidate

            individual = _build_one_per_region_individual(
                product,
                warehouses,
                transport_cost,
                holding_cost,
                temp_choice,
            )
            current_fitness = fitness(
                individual,
                warehouses,
                transport_cost,
                holding_cost,
                demand_by_region,
                max_expected_holding_cost,
                max_expected_transfer_cost,
            )
            if current_fitness > best_fitness:
                best_fitness = current_fitness
                best_choice = candidate

        if best_choice is not None:
            region_choice[region] = best_choice

    final_choice = dict(base_choice)
    final_choice.update(region_choice)
    individual = _build_one_per_region_individual(
        product,
        warehouses,
        transport_cost,
        holding_cost,
        final_choice,
    )
    runtime = time.perf_counter() - start
    return _build_method_result(
        "Greedy Heuristic",
        individual,
        warehouses,
        transport_cost,
        holding_cost,
        demand_by_region,
        runtime,
    )


def brute_force_verify_small_instance(product, warehouses, transport_cost, holding_cost, demand_by_region, step=1, max_combinations=50000):
    """Brute-force verifier for small instances. Returns best fitness/solution among enumerated allocations."""
    min_stock, max_stock = _warehouse_bounds(warehouses)
    demand_norm = _normalize_region_dict(product.get("demand", {}))
    total_quantity = int(round(product.get("total_quantity", sum(demand_norm.values()))))
    min_total = sum(min_stock.values())
    total_add = max(0, total_quantity - min_total)

    wh_list = list(warehouses.keys())
    add_ranges = []
    for w in wh_list:
        max_add = max_stock[w] - min_stock[w]
        add_ranges.append(list(range(0, max_add + 1, max(1, step))))

    total_combos = 1
    for arr in add_ranges:
        total_combos *= max(1, len(arr))
    if total_combos > max_combinations:
        return {
            "status": "SKIPPED",
            "reason": f"too many combinations: {total_combos}",
            "evaluations": 0,
        }

    max_hold = _max_expected_holding_cost(warehouses, holding_cost)
    max_trans = _max_expected_transfer_cost(warehouses, transport_cost)
    best_fit = float("-inf")
    best_individual = None
    eval_count = 0

    for combo in itertools.product(*add_ranges):
        if sum(combo) != total_add:
            continue
        individual = {w: min_stock[w] + combo[i] for i, w in enumerate(wh_list)}
        fit_val = fitness(individual, warehouses, transport_cost, holding_cost, demand_by_region, max_hold, max_trans)
        eval_count += 1
        if fit_val > best_fit:
            best_fit = fit_val
            best_individual = individual

    return {
        "status": "OK",
        "evaluations": eval_count,
        "best_fitness": float(best_fit),
        "best_individual": best_individual,
    }


def run_exact_solver(
    product,
    warehouses,
    transport_cost,
    holding_cost,
    demand_by_region,
    step: int = 1,
    max_combinations: int = 1000000000,
):
    # Ensure downstream helpers see the forecast demand
    if demand_by_region is not None:
        product = dict(product)
        product["demand"] = demand_by_region

    start = time.perf_counter()
    region_to_wh = _group_warehouses_by_region(warehouses)
    regions = [region for region in region_to_wh.keys() if region_to_wh[region]]
    if not regions:
        min_stock, _ = _warehouse_bounds(warehouses)
        individual = {w: min_stock[w] for w in warehouses.keys()}
        runtime = time.perf_counter() - start
        return _build_method_result(
            "Exact Solver",
            individual,
            warehouses,
            transport_cost,
            holding_cost,
            demand_by_region,
            runtime,
        )

    max_expected_holding_cost = _max_expected_holding_cost(warehouses, holding_cost)
    max_expected_transfer_cost = _max_expected_transfer_cost(warehouses, transport_cost)

    best_individual = None
    best_fitness = float("-inf")
    best_cost = float("inf")

    # Prepare bounds for added units per warehouse
    min_stock, max_stock = _warehouse_bounds(warehouses)
    add_ranges = {}
    for w in max_stock.keys():
        max_add = max_stock[w] - min_stock[w]
        if max_add <= 0:
            add_ranges[w] = [0]
        else:
            # create discrete options from 0 to max_add with given step
            add_ranges[w] = list(range(0, max_add + 1, max(1, step)))

    # total additional units we must allocate
    product_demand = product.get("demand", {})
    demand_norm = _normalize_region_dict(product_demand)
    total_quantity = int(round(product.get("total_quantity", sum(demand_norm.values()))))
    min_total = sum(min_stock.values())
    total_add = max(0, total_quantity - min_total)

    # Quick combinations count and guard
    combos_count = 1
    for w in add_ranges:
        combos_count *= max(1, len(add_ranges[w]))
    # If too many combos, fall back to region-choice enumeration
    if combos_count > max_combinations:
        combos_count = None

    eval_count = 0
    if combos_count is None:
        # fallback behavior: previous exact solver (one warehouse per region)
        for combo in itertools.product(*(region_to_wh[region] for region in regions)):
            region_choice = dict(zip(regions, combo))
            individual = _build_one_per_region_individual(
                product,
                warehouses,
                transport_cost,
                holding_cost,
                region_choice,
            )
            current_fitness = fitness(
                individual,
                warehouses,
                transport_cost,
                holding_cost,
                demand_by_region,
                max_expected_holding_cost,
                max_expected_transfer_cost,
            )
            eval_count += 1
            cost = _compute_total_cost(individual, warehouses, holding_cost, transport_cost)
            if current_fitness > best_fitness or (
                np.isclose(current_fitness, best_fitness) and cost < best_cost
            ):
                best_fitness = current_fitness
                best_cost = cost
                best_individual = individual
    else:
        # Full enumeration over added units per warehouse but prune by total_add
        wh_list = list(add_ranges.keys())
        iter_ranges = [add_ranges[w] for w in wh_list]
        checked = 0
        for combo in itertools.product(*iter_ranges):
            checked += 1
            if checked % 1000000 == 0:
                pass
            if sum(combo) != total_add:
                continue
            individual = {w: min_stock[w] + combo[i] for i, w in enumerate(wh_list)}
            current_fitness = fitness(
                individual,
                warehouses,
                transport_cost,
                holding_cost,
                demand_by_region,
                max_expected_holding_cost,
                max_expected_transfer_cost,
            )
            eval_count += 1
            cost = _compute_total_cost(individual, warehouses, holding_cost, transport_cost)
            if current_fitness > best_fitness or (
                np.isclose(current_fitness, best_fitness) and cost < best_cost
            ):
                best_fitness = current_fitness
                best_cost = cost
                best_individual = individual

    if best_individual is None:
        min_stock, _ = _warehouse_bounds(warehouses)
        best_individual = {w: min_stock[w] for w in warehouses.keys()}

    runtime = time.perf_counter() - start
    result = _build_method_result(
        "Exact Solver",
        best_individual,
        warehouses,
        transport_cost,
        holding_cost,
        demand_by_region,
        runtime,
    )
    result["evaluations"] = int(eval_count)
    return result


def run_optimization_comparison(
    product,
    warehouses,
    transport_cost,
    holding_cost,
    demand_by_region,
    genetic_result=None,
    genetic_runtime_seconds=None,
    iterations=200,
    seed=None,
):
    results = []
    results.append(
        run_random_search_optimization(
            product,
            warehouses,
            transport_cost,
            holding_cost,
            demand_by_region,
            iterations=iterations,
            seed=seed,
        )
    )
    results.append(
        run_greedy_heuristic(
            product,
            warehouses,
            transport_cost,
            holding_cost,
            demand_by_region,
        )
    )
    results.append(
        run_exact_solver(
            product,
            warehouses,
            transport_cost,
            holding_cost,
            demand_by_region,
        )
    )

    # Attempt ILP exact solver by importing pulp at runtime (more robust)
    try:
        import importlib
        pulp_mod = importlib.import_module("pulp")
        # ensure module-global pulp refers to the imported module
        global pulp
        pulp = pulp_mod
    except Exception:
        pulp_mod = None

    if pulp_mod is not None:
        try:
            ilp_result = run_exact_ilp_solver(
                product,
                warehouses,
                transport_cost,
                holding_cost,
                demand_by_region,
            )
            ilp_result["provably_optimal"] = False
            results.append(ilp_result)
        except Exception as exc:
            results.append({
                "method": "Exact ILP (error)",
                "total_cost": 0.0,
                "service_level": 0.0,
                "runtime_seconds": 0.0,
                "mt": 0.0,
                "evaluations": 0,
                "solver_status": "ERROR",
                "provably_optimal": False,
                "error": str(exc),
            })

    if genetic_result is None:
        start = time.perf_counter()
        genetic_result = run_genetic_optimization(
            product,
            warehouses,
            transport_cost,
            seed=seed,
            demand_by_region=demand_by_region,
        )
        genetic_runtime_seconds = time.perf_counter() - start

    individual = genetic_result.get("final_stock_by_warehouse", {})
    runtime = float(genetic_runtime_seconds or 0.0)
    results.append(
        _build_method_result(
            "Genetic Algorithm",
            individual,
            warehouses,
            transport_cost,
            holding_cost,
            demand_by_region,
            runtime,
        )
    )

    return results


# ----------------------------
# Generate Individual
# individual = {warehouse_id: qty}  (flat dict, single product)
# ----------------------------
def generate_individual(product, warehouses):
    warehouse_ids = list(warehouses.keys())
    min_stock, max_stock = _warehouse_bounds(warehouses)
    demand = _normalize_region_dict(product["demand"])
    region_shares = _region_shares(demand)
    total_quantity = int(round(product.get("total_quantity", sum(demand.values()))))
    region_targets = _allocate_region_targets(total_quantity, region_shares)
    region_targets, _, _ = _adjust_region_targets(region_targets, warehouses, product.get("transport_cost", {}))
    region_to_wh = _group_warehouses_by_region(warehouses)

    individual = {w: min_stock[w] for w in warehouse_ids}
    for region, target in region_targets.items():
        names = region_to_wh.get(region, [])
        if not names:
            continue
        remaining = target - sum(individual[w] for w in names)
        if remaining <= 0:
            continue

        shuffled = names[:]
        random.shuffle(shuffled)
        for w in shuffled:
            if remaining <= 0:
                break
            max_possible = max_stock[w] - individual[w]
            if max_possible <= 0:
                continue
            qty = random.randint(0, min(max_possible, remaining))
            individual[w] += qty
            remaining -= qty

        if remaining > 0:
            for w in shuffled:
                if remaining <= 0:
                    break
                max_possible = max_stock[w] - individual[w]
                if max_possible <= 0:
                    continue
                qty = min(max_possible, remaining)
                individual[w] += qty
                remaining -= qty

    return individual


# ----------------------------
# Population
# ----------------------------
def generate_population(size, product, warehouses):
    return [generate_individual(product, warehouses) for _ in range(size)]


# ----------------------------
# Encode / Decode
# ----------------------------
def encode(individual, warehouse_ids):
    return np.array(
        [individual[w] for w in warehouse_ids],
        dtype=float
    )


def decode(vector, warehouse_ids):
    return {w: int(vector[i]) for i, w in enumerate(warehouse_ids)}


# ----------------------------
# Fitness Function (single product)
# ----------------------------
def fitness(
    individual,
    warehouses,
    transport_cost,
    holding_cost,
    demand_by_region,
    max_expected_holding_cost,
    max_expected_transfer_cost,
    alpha=0.5,
):
    """
    New recommended fitness:
    - TotalCost = HoldingCost + TransferCost
    - TotalCost_norm = TotalCost / MaxExpectedCost (capped at 1)
    - Fitness = alpha * ServiceLevel - (1 - alpha) * TotalCost_norm
    """
    add_by_warehouse = _additional_units(individual, warehouses)
    # Compute satisfied units per region from total final stock (includes baseline)
    satisfied_by_region = {}
    for w, qty in individual.items():
        region = warehouses.get(w, {}).get("region")
        if region is None:
            continue
        satisfied_by_region[region] = satisfied_by_region.get(region, 0.0) + float(qty)

    service_level = _service_level(demand_by_region, satisfied_by_region)
    holding_cost_value = _holding_cost(individual, holding_cost)
    transfer_cost_value = _transfer_cost(add_by_warehouse, transport_cost)

    total_cost_value = float(holding_cost_value + transfer_cost_value)
    max_total_expected = float(max_expected_holding_cost + max_expected_transfer_cost)

    total_cost_norm = 0.0
    if max_total_expected > 0:
        total_cost_norm = min(total_cost_value / max_total_expected, 1.0)

    fitness_value = alpha * float(service_level) - (1.0 - float(alpha)) * float(total_cost_norm)
    return float(fitness_value)


# ----------------------------
# Capacity Check
# ----------------------------
def is_capacity_valid(individual, warehouses):
    for w in warehouses:
        min_stock = int(warehouses[w].get("stock_level", 0))
        if individual[w] < min_stock:
            return False
        if individual[w] > warehouses[w]["capacity"]:
            return False
    return True


def _repair_individual(individual, warehouses, total_quantity, region_targets):
    warehouse_ids = list(warehouses.keys())
    min_stock, max_stock = _warehouse_bounds(warehouses)
    region_to_wh = _group_warehouses_by_region(warehouses)

    total_quantity = int(round(total_quantity))
    min_total = sum(min_stock.values())
    if total_quantity < min_total:
        total_quantity = min_total
    for w in warehouse_ids:
        qty = int(round(individual.get(w, min_stock[w])))
        if qty < min_stock[w]:
            qty = min_stock[w]
        if qty > max_stock[w]:
            qty = max_stock[w]
        individual[w] = qty

    if total_quantity <= 0:
        return individual

    for region, target in region_targets.items():
        names = region_to_wh.get(region, [])
        if not names:
            continue
        current = sum(individual[w] for w in names)
        if current > target:
            excess = current - target
            while excess > 0:
                candidates = [w for w in names if individual[w] > min_stock[w]]
                if not candidates:
                    break
                w = random.choice(candidates)
                remove = min(excess, individual[w] - min_stock[w])
                delta = random.randint(1, remove)
                individual[w] -= delta
                excess -= delta
        elif current < target:
            deficit = target - current
            while deficit > 0:
                candidates = [w for w in names if individual[w] < max_stock[w]]
                if not candidates:
                    break
                w = random.choice(candidates)
                add = min(deficit, max_stock[w] - individual[w])
                delta = random.randint(1, add)
                individual[w] += delta
                deficit -= delta

    return individual


def _mutate_individual(individual, warehouses, total_quantity, region_targets, mutation_rate):
    min_stock, max_stock = _warehouse_bounds(warehouses)
    mutated = individual.copy()
    for w in mutated:
        if random.random() < mutation_rate:
            span = max_stock[w] - min_stock[w]
            step = max(1, int(span * 0.1))
            mutated[w] += random.randint(-step, step)
    return _repair_individual(mutated, warehouses, total_quantity, region_targets)


def run_genetic_optimization(
    product,
    warehouses,
    transport_cost,
    population_size=60,
    generations=120,
    mutation_rate=0.15,
    seed=None,
    demand_by_region=None,
):
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    # Prefer an explicitly provided demand forecast; otherwise use product['demand']
    if demand_by_region is not None:
        demand_for_targets = _normalize_region_dict(demand_by_region)
        product = dict(product)
        product["demand"] = demand_for_targets
    else:
        demand_for_targets = _normalize_region_dict(product.get("demand", {}))
    total_demand = sum(demand_for_targets.values())
    total_quantity = int(round(product.get("total_quantity", total_demand)))
    if total_demand > 0:
        region_percentages = {
            region: (qty / total_demand) * 100.0
            for region, qty in demand_for_targets.items()
        }
    else:
        region_percentages = {region: 0.0 for region in demand_for_targets.keys()}

    region_shares = _region_shares(demand_for_targets)
    region_targets = _allocate_region_targets(total_quantity, region_shares)
    region_targets, fallback_region, missing_regions = _adjust_region_targets(
        region_targets,
        warehouses,
        transport_cost,
    )
    product = dict(product)
    product["demand"] = demand_for_targets
    product["transport_cost"] = transport_cost

    holding_cost = product.get("holding_cost", {})
    if demand_by_region is None:
        demand_by_region = product.get("demand", {})
    max_expected_holding_cost = _max_expected_holding_cost(warehouses, holding_cost)
    max_expected_transfer_cost = _max_expected_transfer_cost(warehouses, transport_cost)

    population = generate_population(population_size, product, warehouses)
    population = [
        _repair_individual(ind, warehouses, total_quantity, region_targets)
        for ind in population
    ]

    best_individual = None
    best_fitness = float("-inf")
    elite_size = max(1, int(population_size * 0.2))

    for _ in range(generations):
        scored = sorted(
            (
                (
                    fitness(
                        ind,
                        warehouses,
                        transport_cost,
                        holding_cost,
                        demand_by_region,
                        max_expected_holding_cost,
                        max_expected_transfer_cost,
                    ),
                    ind,
                )
                for ind in population
            ),
            key=lambda x: x[0],
            reverse=True,
        )
        if scored and scored[0][0] > best_fitness:
            best_fitness = scored[0][0]
            best_individual = scored[0][1].copy()

        elites = [ind.copy() for _, ind in scored[:elite_size]]
        next_population = elites[:]
        while len(next_population) < population_size:
            parent = random.choice(elites)
            child = _mutate_individual(parent, warehouses, total_quantity, region_targets, mutation_rate)
            next_population.append(child)
        population = next_population

    if best_individual is None and population:
        best_individual = population[0]
        best_fitness = fitness(
            best_individual,
            warehouses,
            transport_cost,
            holding_cost,
            demand_by_region,
            max_expected_holding_cost,
            max_expected_transfer_cost,
        )

    min_stock, _ = _warehouse_bounds(warehouses)
    final_stock = best_individual or {w: min_stock[w] for w in warehouses.keys()}
    add_by_warehouse = {
        w: max(0, final_stock[w] - min_stock[w])
        for w in final_stock.keys()
    }

    return {
        "final_stock_by_warehouse": final_stock,
        "add_by_warehouse": add_by_warehouse,
        "best_fitness": float(best_fitness if best_fitness != float("-inf") else 0.0),
        "population_size": int(population_size),
        "generations": int(generations),
        "mutation_rate": float(mutation_rate),
        "region_percentages": region_percentages,
        "region_targets": region_targets,
        "fallback_region": fallback_region,
        "missing_regions": missing_regions,
    }


# ----------------------------
# Example usage
# ----------------------------
def genetic_algorithm_example(product, warehouses, transport_cost):
    population = generate_population(5, product, warehouses)

    for i, ind in enumerate(population):
        print(f"\nIndividual {i}: {ind}")
        print("Capacity OK:", is_capacity_valid(ind, warehouses))
        print(
            "Fitness:",
            fitness(
                ind,
                warehouses,
                transport_cost,
                product.get("holding_cost", {}),
                product.get("demand", {}),
                _max_expected_holding_cost(warehouses, product.get("holding_cost", {})),
                _max_expected_transfer_cost(warehouses, transport_cost),
            ),
        )


def run_exact_ilp_solver(
    product,
    warehouses,
    transport_cost,
    holding_cost,
    demand_by_region,
    alpha=0.5,
):
    """Solve exact integer allocation using MILP (pulp). Returns same result structure as other solvers."""
    if pulp is None:
        raise RuntimeError("pulp not available")

    # Ensure the ILP uses the provided demand forecast when given
    if demand_by_region is not None:
        product = dict(product)
        product["demand"] = demand_by_region

    start = time.perf_counter()
    min_stock, max_stock = _warehouse_bounds(warehouses)
    product_demand = product.get("demand", {})
    demand_norm = _normalize_region_dict(product_demand)
    total_demand = sum(demand_norm.values())
    total_quantity = int(round(product.get("total_quantity", sum(demand_norm.values()))))
    min_total = sum(min_stock.values())
    if total_quantity < min_total:
        total_quantity = min_total
    total_add = max(0, total_quantity - min_total)

    region_to_wh = _group_warehouses_by_region(warehouses)
    regions = list(region_to_wh.keys())

    max_expected_hold = _max_expected_holding_cost(warehouses, holding_cost)
    max_expected_trans = _max_expected_transfer_cost(warehouses, transport_cost)

    # Build MILP (model exact capped fitness)
    prob = pulp.LpProblem("exact_allocation", pulp.LpMaximize)

    # Variables: add_w integer, satisfied_r continuous
    add_vars = {
        w: pulp.LpVariable(f"add_{w}", lowBound=0, upBound=(max_stock[w] - min_stock[w]), cat="Integer")
        for w in warehouses.keys()
    }
    sat_vars = {
        r: pulp.LpVariable(f"sat_{r}", lowBound=0, upBound=float(demand_norm.get(r, 0.0)), cat="Continuous")
        for r in regions
    }

    # Constraints: satisfied_r <= sum adds in region; sum adds == total_add
    for r in regions:
        prob += sat_vars[r] <= pulp.lpSum([add_vars[w] for w in region_to_wh.get(r, [])])

    prob += pulp.lpSum([add_vars[w] for w in add_vars.keys()]) == total_add

    # Raw objective terms
    service_term = pulp.lpSum([sat_vars[r] for r in regions])
    holding_term = pulp.lpSum([(min_stock[w] + add_vars[w]) * float(holding_cost.get(w, 0.0)) for w in add_vars.keys()])
    transfer_term = pulp.lpSum([add_vars[w] * float(transport_cost.get(w, 0.0)) for w in add_vars.keys()])

    # Normalize denominators
    norm_service = float(total_demand) if total_demand > 0 else 1.0
    norm_holding = float(max_expected_hold) if max_expected_hold > 0 else 1.0
    norm_transfer = float(max_expected_trans) if max_expected_trans > 0 else 1.0

    # Combine holding and transfer into TotalCost and normalize by max total expected
    total_term = holding_term + transfer_term
    norm_total = float(max_expected_hold + max_expected_trans) if (max_expected_hold + max_expected_trans) > 0 else 1.0

    # Introduce normalized capped variable for total cost: total_norm = min(total_term / norm_total, 1)
    M = 1e9
    total_norm = pulp.LpVariable("total_norm", lowBound=0, upBound=1, cat="Continuous")
    z_tot = pulp.LpVariable("z_tot", cat="Binary")

    Total_raw = total_term / float(norm_total)

    # Enforce z flag: if Total_raw > 1 then z_tot = 1
    prob += Total_raw - 1 <= M * z_tot

    # Linearize total_norm = min(Total_raw, 1)
    prob += total_norm <= Total_raw
    prob += total_norm <= 1
    prob += total_norm >= Total_raw - M * z_tot
    prob += total_norm >= 1 - M * (1 - z_tot)

    # Objective matches new capped fitness: alpha * service - (1 - alpha) * total_norm
    prob += (
        alpha * (service_term / norm_service) - (1.0 - float(alpha)) * total_norm
    )

    # Solve (no time limit)
    solver = pulp.PULP_CBC_CMD(msg=False)
    prob.solve(solver)

    # Build individual final stock dict
    final_stock = {w: int(min_stock[w] + pulp.value(add_vars[w])) for w in add_vars.keys()}

    runtime = time.perf_counter() - start
    result = _build_method_result(
        "Exact ILP",
        final_stock,
        warehouses,
        transport_cost,
        holding_cost,
        demand_by_region,
        runtime,
    )
    # add solver status
    result["solver_status"] = pulp.LpStatus.get(prob.status, str(prob.status)) if hasattr(pulp, 'LpStatus') else pulp.LpStatus[prob.status]
    result["evaluations"] = 1
    return result


if __name__ == "__main__":
    product = {
        "demand": {"R1": 50, "R2": 30},
        "holding_cost": {"W1": 2, "W2": 3},
        "total_quantity": 120,
    }

    warehouses = {
        "W1": {"capacity": 200, "stock_level": 50, "region": "R1"},
        "W2": {"capacity": 150, "stock_level": 0, "region": "R2"},
    }

    transport_cost = {
        "W1": 4,
        "W2": 2,
    }

    genetic_algorithm_example(product, warehouses, transport_cost)