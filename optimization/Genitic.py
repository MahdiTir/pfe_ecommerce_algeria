import random
import numpy as np


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


# ----------------------------
# Generate Individual
# individual = {warehouse_id: qty}  (flat dict, single product)
# ----------------------------
def generate_individual(product, warehouses):
    warehouse_ids = list(warehouses.keys())
    min_stock, max_stock = _warehouse_bounds(warehouses)
    region_shares = _region_shares(product["demand"])
    total_quantity = int(round(product.get("total_quantity", sum(product["demand"].values()))))
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
def fitness(individual, product, warehouses, transport_cost):
    total_quantity = sum(individual.values())

    # Holding cost
    total_holding_cost = sum(
        qty * product["holding_cost"][w]
        for w, qty in individual.items()
    )

    # Transport cost: per-warehouse unit cost
    total_transport_cost = sum(
        qty * transport_cost[w]
        for w, qty in individual.items()
    )

    if total_quantity <= 0:
        return 0.0

    fitness_value = total_quantity / (1 + total_holding_cost + total_transport_cost)

    return fitness_value  # maximize


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
):
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    total_demand = sum(product["demand"].values())
    total_quantity = int(round(product.get("total_quantity", total_demand)))
    if total_demand > 0:
        region_percentages = {
            region: (qty / total_demand) * 100.0
            for region, qty in product["demand"].items()
        }
    else:
        region_percentages = {region: 0.0 for region in product["demand"].keys()}

    region_shares = _region_shares(product["demand"])
    region_targets = _allocate_region_targets(total_quantity, region_shares)
    region_targets, fallback_region, missing_regions = _adjust_region_targets(
        region_targets,
        warehouses,
        transport_cost,
    )
    product = dict(product)
    product["transport_cost"] = transport_cost

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
            ((fitness(ind, product, warehouses, transport_cost), ind) for ind in population),
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
        best_fitness = fitness(best_individual, product, warehouses, transport_cost)

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
        print("Fitness:", fitness(ind, product, warehouses, transport_cost))


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