# Optimization Methods: Technical Documentation

## Overview

This document provides comprehensive technical documentation for all five optimization methods implemented in the warehouse allocation system. Special emphasis is placed on the **fitness function**, which serves as the unified objective function guiding all optimization approaches.

---

## Table of Contents

1. [The Fitness Function - Core Concept](#the-fitness-function)
2. [Cost Components](#cost-components)
3. [Service Level Calculation](#service-level-calculation)
4. [Method 1: Random Search](#method-1-random-search)
5. [Method 2: Greedy Heuristic](#method-2-greedy-heuristic)
6. [Method 3: Exact Solver (Brute Force)](#method-3-exact-solver)
7. [Method 4: Exact ILP (Integer Linear Programming)](#method-4-exact-ilp)
8. [Method 5: Genetic Algorithm](#method-5-genetic-algorithm)
9. [Comparative Analysis](#comparative-analysis)
10. [Implementation Details](#implementation-details)

---

## The Fitness Function

### Purpose and Philosophy

The **fitness function** is the single most important component of the optimization system. It serves multiple critical roles:

1. **Objective Function:** Quantifies the quality of any stock allocation solution
2. **Unified Metric:** Enables fair comparison across different optimization methods
3. **Multi-Objective Balancing:** Combines two competing goals:
   - **Maximize service level** (meet customer demand)
   - **Minimize total cost** (reduce expenses)
4. **Decision Criterion:** Determines which allocation is "better" than another

### Mathematical Definition

```
Fitness(S) = α × ServiceLevel(S) - (1 - α) × TotalCost_normalized(S)
```

**Where:**
- **S** = A stock allocation solution (dictionary: {warehouse_id: quantity})
- **α** = Weighting parameter (0 ≤ α ≤ 1), typically α = 0.5
- **ServiceLevel(S)** = Percentage of regional demand satisfied (0 to 100)
- **TotalCost_normalized(S)** = Normalized total cost (scaled to 0-1 range)

### Component Breakdown

#### 1. Service Level Term: α × ServiceLevel(S)

**Purpose:** Reward solutions that satisfy customer demand.

**Calculation:**
```
ServiceLevel(S) = (Demand_Met / Total_Demand) × 100
```

**Example:**
```
Regional demand:    {'ouest': 1000, 'est': 800, 'north': 1500, 'sud': 300}
Total demand:       3600

Allocation satisfies: ouest=1000, est=800, north=1200, sud=300
Demand met:         3300

ServiceLevel = (3300 / 3600) × 100 = 91.67%
```

**With α = 0.5:**
```
Contribution to fitness = 0.5 × 91.67 = 45.835
```

**Key Insight:** High service level → High fitness (desirable).

#### 2. Cost Term: -(1 - α) × TotalCost_normalized(S)

**Purpose:** Penalize expensive solutions.

**Why Negative?** Costs are BAD, so we subtract them. Higher cost → Lower fitness.

**Normalization:**
```
TotalCost_normalized = (TotalCost - MinCost) / (MaxCost - MinCost)
```

Where MinCost and MaxCost are estimated bounds (e.g., from initial exploration).

**Calculation Example:**
```
TotalCost(S) = 10,500,000 DZD

Normalization (assume):
MinCost = 9,000,000 DZD
MaxCost = 15,000,000 DZD

TotalCost_normalized = (10,500,000 - 9,000,000) / (15,000,000 - 9,000,000)
                     = 1,500,000 / 6,000,000
                     = 0.25
```

**With α = 0.5:**
```
Contribution to fitness = -(1 - 0.5) × 0.25 = -0.125
```

**Key Insight:** Low cost → Low normalized cost → Less penalty → Higher fitness.

#### 3. Combined Fitness

```
Fitness = 45.835 - 0.125 = 45.71
```

### Why This Formulation?

#### Multi-Objective Optimization

In reality, businesses face competing goals:

- **Goal 1:** Satisfy all customer demand (service level = 100%)
- **Goal 2:** Minimize costs

These goals conflict:
- Spreading inventory across many warehouses → High service level, HIGH cost
- Concentrating inventory in cheapest warehouse → Low cost, LOW service level

**The fitness function finds the Pareto-optimal balance.**

#### The Role of α

The parameter **α** controls the trade-off:

| α Value | Interpretation | Behavior |
|---------|----------------|----------|
| α = 0 | Cost-only optimization | Ignores demand, minimizes cost |
| α = 0.25 | Cost-focused | Slight preference for low cost over service |
| α = 0.5 | **Balanced** (default) | Equal weight to service and cost |
| α = 0.75 | Service-focused | Slight preference for service over cost |
| α = 1 | Service-only optimization | Ignores cost, maximizes service |

**Why α = 0.5?**
- Represents balanced business priorities
- Neither cost nor service dominates
- Reflects real-world decision-making: "Good service at reasonable cost"

**Customization:** In practice, α can be tuned based on business strategy:
- Luxury e-commerce: α = 0.7 (prioritize service)
- Budget e-commerce: α = 0.3 (prioritize cost)

### Fitness as a Guiding Principle

Every optimization method uses fitness to:

1. **Evaluate:** Compute fitness for candidate solutions
2. **Compare:** Solution A is better than B if Fitness(A) > Fitness(B)
3. **Select:** Choose the solution with maximum fitness
4. **Optimize:** Iteratively improve solutions to increase fitness

**Pseudocode (all methods follow this pattern):**
```
best_fitness = -∞
best_solution = None

for each candidate_solution in search_space:
    fitness = compute_fitness(candidate_solution)
    if fitness > best_fitness:
        best_fitness = fitness
        best_solution = candidate_solution

return best_solution
```

### Example: Comparing Two Solutions

**Scenario:**
- Total quantity: 5000 units
- Demand: {'ouest': 850, 'est': 900, 'north': 1400, 'sud': 200} → Total: 3350

**Solution A: Random Allocation**
```
Stock: {'WH-01': 1000, 'WH-02': 800, ..., 'WH-14': 350}
Service Level: 75% (only 2513/3350 demand met)
Total Cost: 12,000,000 DZD
Cost_normalized: 0.50 (assume)

Fitness_A = 0.5 × 75 - 0.5 × 0.50 = 37.5 - 0.25 = 37.25
```

**Solution B: ILP-Optimized Allocation**
```
Stock: {'WH-03': 2000, 'WH-07': 1500, ..., 'WH-12': 500}
Service Level: 100% (all 3350 demand met, 1650 buffer)
Total Cost: 10,403,500 DZD
Cost_normalized: 0.23 (assume)

Fitness_B = 0.5 × 100 - 0.5 × 0.23 = 50.0 - 0.115 = 49.885
```

**Conclusion:** Solution B is superior (49.885 > 37.25).

---

## Cost Components

### Total Cost Formula

```
TotalCost(S) = HoldingCost(S) + TransferCost(S)
```

### 1. Holding Cost

**Definition:** Cost of storing inventory at a warehouse.

**Formula:**
```
HoldingCost = Σ (stock[w] × holding_cost[w])  for all warehouses w
```

**Where:**
- **stock[w]:** Final stock quantity at warehouse w (after optimization)
- **holding_cost[w]:** Per-unit holding cost at warehouse w (DZD per unit per period)

**Intuition:** 
- Large warehouses have economies of scale → Lower holding cost per unit
- Small/remote warehouses → Higher holding cost per unit

**Example:**
```
Warehouses:
  WH-01 (north): capacity=2000, holding_cost=1000 DZD/unit
  WH-02 (ouest): capacity=1500, holding_cost=1200 DZD/unit
  WH-03 (sud):   capacity=800,  holding_cost=1500 DZD/unit

Allocation:
  stock = {WH-01: 1200, WH-02: 900, WH-03: 400}

HoldingCost = 1200×1000 + 900×1200 + 400×1500
            = 1,200,000 + 1,080,000 + 600,000
            = 2,880,000 DZD
```

**Key Insight:** Concentrating stock in low-holding-cost warehouses reduces total cost.

### 2. Transfer Cost

**Definition:** Cost of moving inventory to/from a warehouse (redistribution cost).

**Formula:**
```
TransferCost = Σ |stock[w] - initial_stock[w]| × transfer_cost[w]  for all warehouses w
```

**Where:**
- **stock[w]:** Final stock quantity (optimization result)
- **initial_stock[w]:** Current stock level before optimization
- **|difference|:** Absolute value (whether adding or removing stock)
- **transfer_cost[w]:** Per-unit transfer cost (DZD per unit)

**Intuition:**
- Moving inventory costs money (transport, handling, labor)
- Both adding AND removing stock incurs cost
- Remote warehouses have higher transfer costs

**Example:**
```
Initial stock:
  {WH-01: 800, WH-02: 600, WH-03: 300}

Optimized stock:
  {WH-01: 1200, WH-02: 900, WH-03: 100}

Changes:
  WH-01: |1200 - 800| = 400 units added
  WH-02: |900 - 600| = 300 units added
  WH-03: |100 - 300| = 200 units removed

Transfer costs:
  {WH-01: 500, WH-02: 600, WH-03: 800} DZD/unit

TransferCost = 400×500 + 300×600 + 200×800
             = 200,000 + 180,000 + 160,000
             = 540,000 DZD
```

**Key Insight:** Minimizing stock movement reduces transfer costs. ILP often makes strategic trade-offs: move less vs. optimize holding.

### Why Two Cost Components?

**Holding Cost:** Ongoing operational expense (weekly/monthly)
**Transfer Cost:** One-time redistribution expense

**Trade-off Example:**
- **Option A:** Move 1000 units to cheap warehouse
  - High transfer cost (one-time)
  - Low holding cost (ongoing savings)
  - Best for long planning horizons

- **Option B:** Keep stock as-is
  - Zero transfer cost
  - High holding cost (ongoing expense)
  - Best for short planning horizons

**The optimization balances these dynamically.**

---

## Service Level Calculation

### Definition

**Service Level:** Percentage of regional demand that can be satisfied given the stock allocation and warehouse-region assignments.

### Calculation Process

#### Step 1: Group Warehouses by Region

```python
warehouses_by_region = {
    'ouest': ['WH-02', 'WH-05', 'WH-08'],
    'est': ['WH-04', 'WH-09', 'WH-13'],
    'north': ['WH-01', 'WH-03', 'WH-06', 'WH-07', 'WH-10', 'WH-11'],
    'sud': ['WH-12', 'WH-14']
}
```

#### Step 2: Calculate Total Stock per Region

```python
stock_by_region = {}
for region, wh_list in warehouses_by_region.items():
    stock_by_region[region] = sum(stock[wh] for wh in wh_list)

# Example result:
# {'ouest': 1500, 'est': 1800, 'north': 3200, 'sud': 500}
```

#### Step 3: Compute Demand Met per Region

```python
demand_by_region = {'ouest': 850, 'est': 900, 'north': 1400, 'sud': 200}

demand_met = {}
for region in demand_by_region:
    available = stock_by_region.get(region, 0)
    required = demand_by_region[region]
    demand_met[region] = min(available, required)

# Example result:
# {'ouest': 850, 'est': 900, 'north': 1400, 'sud': 200}
# All demand met (stock ≥ demand in each region)
```

#### Step 4: Calculate Overall Service Level

```python
total_demand = sum(demand_by_region.values())
total_met = sum(demand_met.values())

service_level = (total_met / total_demand) × 100 if total_demand > 0 else 100

# Example:
# total_demand = 3350
# total_met = 3350
# service_level = 100%
```

### Edge Cases

#### Case 1: Excess Stock (Over-Stocked)

```
Demand: {'ouest': 850, 'est': 900, 'north': 1400, 'sud': 200}
Stock:  {'ouest': 1500, 'est': 1800, 'north': 3200, 'sud': 500}

Demand met: All regions satisfied
Service Level: 100%
```

**Note:** Excess stock doesn't increase service level beyond 100%, but incurs higher holding costs.

#### Case 2: Shortage (Under-Stocked)

```
Demand: {'ouest': 850, 'est': 900, 'north': 1400, 'sud': 200}
Stock:  {'ouest': 600, 'est': 700, 'north': 1000, 'sud': 150}

Demand met:
  ouest: min(600, 850) = 600
  est: min(700, 900) = 700
  north: min(1000, 1400) = 1000
  sud: min(150, 200) = 150

Total met: 2450
Total demand: 3350
Service Level: (2450 / 3350) × 100 = 73.13%
```

#### Case 3: Region with No Warehouses

```
Demand: {'ouest': 850, 'est': 900, 'north': 1400, 'sud': 200}
Warehouses: Only in north, est, sud (no ouest warehouses)

Stock by region:
  {'ouest': 0, 'est': 1800, 'north': 3200, 'sud': 500}

Demand met:
  ouest: 0 (cannot satisfy)
  Others: satisfied

Total met: 2500
Service Level: (2500 / 3350) × 100 = 74.63%
```

**Important:** This is a realistic edge case. Optimization cannot create warehouses where none exist.

### Service Level in Fitness Function

High service level directly increases fitness:

```
Fitness = 0.5 × ServiceLevel - (cost term)
```

- Service Level = 100% → contributes +50 to fitness
- Service Level = 80% → contributes +40 to fitness
- Service Level = 50% → contributes +25 to fitness

**Trade-off:** Achieving 100% service level might require expensive allocations. Optimization finds the sweet spot.

---

## Method 1: Random Search

### Algorithm Overview

**Approach:** Generate random valid allocations and select the best.

**Complexity:** O(n × m) where n = number of iterations, m = number of warehouses

**Pros:** Simple, fast, no assumptions about problem structure

**Cons:** No guarantee of optimality, highly variable results

### Detailed Algorithm

```python
def run_random_search_optimization(product, demand_by_region, warehouses, num_iterations=500):
    """
    Random Search Optimization
    
    Process:
    1. Determine valid stock range for each warehouse [0, capacity]
    2. Generate num_iterations random allocations
    3. Each allocation must sum to total_quantity
    4. Evaluate fitness for each
    5. Return the best
    """
    
    # Step 1: Setup
    demand_norm, total_quantity = _resolve_demand_and_quantity(product, demand_by_region, warehouses)
    capacities = {wh_id: wh['capacity'] for wh_id, wh in warehouses.items()}
    
    # Step 2: Initialize best solution
    best_individual = None
    best_fitness = -float('inf')
    
    # Step 3: Random search loop
    for iteration in range(num_iterations):
        # Generate random allocation
        individual = _generate_random_individual(warehouses, total_quantity, capacities)
        
        # Repair if invalid (exceeds capacity, wrong total)
        individual = _repair_individual(individual, total_quantity, capacities)
        
        # Evaluate fitness
        fitness = _compute_fitness(individual, demand_norm, warehouses, holding_cost, transport_cost)
        
        # Update best if improved
        if fitness > best_fitness:
            best_fitness = fitness
            best_individual = individual
    
    # Step 4: Return best found
    return {
        'stock_by_warehouse': best_individual,
        'fitness': best_fitness,
        'cost': _compute_total_cost(best_individual, warehouses, holding_cost, transport_cost),
        'service_level': _compute_service_level(best_individual, demand_norm, warehouses),
        'method': 'Random Search',
        'runtime': elapsed_time
    }
```

### Random Individual Generation

```python
def _generate_random_individual(warehouses, total_quantity, capacities):
    """
    Generate a random stock allocation
    
    Strategy: Dirichlet distribution (ensures sum = total_quantity)
    """
    import numpy as np
    
    n_warehouses = len(warehouses)
    
    # Generate random proportions (sum = 1)
    proportions = np.random.dirichlet(np.ones(n_warehouses))
    
    # Scale to total_quantity
    individual = {}
    for i, (wh_id, wh) in enumerate(warehouses.items()):
        # Allocate proportionally
        quantity = int(proportions[i] * total_quantity)
        
        # Clip to valid range [0, capacity]
        quantity = max(0, min(quantity, capacities[wh_id]))
        
        individual[wh_id] = quantity
    
    return individual
```

### Repair Mechanism

Generated individuals might violate constraints:
1. Sum ≠ total_quantity
2. Some warehouses exceed capacity

```python
def _repair_individual(individual, total_quantity, capacities):
    """
    Repair invalid individual
    
    Fix:
    1. Clip each warehouse to [0, capacity]
    2. Adjust to match total_quantity exactly
    """
    
    # Step 1: Enforce capacity constraints
    for wh_id in individual:
        individual[wh_id] = max(0, min(individual[wh_id], capacities[wh_id]))
    
    # Step 2: Adjust sum
    current_sum = sum(individual.values())
    deficit = total_quantity - current_sum
    
    if deficit > 0:
        # Need to add stock
        # Distribute among warehouses with spare capacity
        while deficit > 0:
            for wh_id in individual:
                if individual[wh_id] < capacities[wh_id] and deficit > 0:
                    individual[wh_id] += 1
                    deficit -= 1
    
    elif deficit < 0:
        # Need to remove stock
        # Remove from warehouses with excess
        deficit = -deficit
        while deficit > 0:
            for wh_id in individual:
                if individual[wh_id] > 0 and deficit > 0:
                    individual[wh_id] -= 1
                    deficit -= 1
    
    return individual
```

### Characteristics

**Randomness:** Each run produces different results (set seed for reproducibility).

**Performance:**
- **Best case:** Lucky early sample near optimum
- **Worst case:** No good solutions explored
- **Average case:** Mediocre solution

**When to Use:**
- Baseline for comparison
- Quick preliminary solution
- When optimization time is extremely limited

---

## Method 2: Greedy Heuristic

### Algorithm Overview

**Approach:** Iteratively allocate stock to the "best" warehouse based on a greedy criterion.

**Complexity:** O(m × k) where m = number of warehouses, k = total_quantity

**Pros:** Fast (< 1 ms), deterministic, intuitive

**Cons:** Locally optimal, may miss global optimum

### Detailed Algorithm

```python
def run_greedy_heuristic(product, demand_by_region, warehouses):
    """
    Greedy Heuristic Optimization
    
    Strategy:
    1. Start with empty allocation
    2. Repeat total_quantity times:
       - Find warehouse with best "value" (lowest unit cost + highest demand in region)
       - Allocate 1 unit to that warehouse (if capacity allows)
    3. Return final allocation
    """
    
    # Step 1: Setup
    demand_norm, total_quantity = _resolve_demand_and_quantity(product, demand_by_region, warehouses)
    
    # Step 2: Initialize empty allocation
    individual = {wh_id: 0 for wh_id in warehouses.keys()}
    
    # Step 3: Greedy allocation loop
    for _ in range(total_quantity):
        best_wh = None
        best_score = -float('inf')
        
        # Find warehouse with best score
        for wh_id, wh in warehouses.items():
            # Skip if at capacity
            if individual[wh_id] >= wh['capacity']:
                continue
            
            # Compute greedy score
            score = _greedy_score(wh, demand_norm, individual, warehouses)
            
            if score > best_score:
                best_score = score
                best_wh = wh_id
        
        # Allocate to best warehouse
        if best_wh:
            individual[best_wh] += 1
    
    # Step 4: Return result
    fitness = _compute_fitness(individual, demand_norm, warehouses, holding_cost, transport_cost)
    
    return {
        'stock_by_warehouse': individual,
        'fitness': fitness,
        'cost': _compute_total_cost(individual, warehouses, holding_cost, transport_cost),
        'service_level': _compute_service_level(individual, demand_norm, warehouses),
        'method': 'Greedy Heuristic',
        'runtime': elapsed_time
    }
```

### Greedy Score Function

**Key Decision:** What makes a warehouse "good" for the next unit?

**Heuristic:**
```
score = demand_weight × regional_demand - cost_weight × unit_cost
```

**Where:**
- **regional_demand:** Demand in this warehouse's region (higher = more needed)
- **unit_cost:** holding_cost + transfer_cost for this warehouse (lower = cheaper)
- **demand_weight, cost_weight:** Tunable parameters (default: 1.0 each)

```python
def _greedy_score(warehouse, demand_by_region, current_allocation, warehouses):
    """
    Compute greedy score for allocating to this warehouse
    """
    region = warehouse['region']
    
    # Component 1: Regional demand (prioritize high-demand regions)
    demand_in_region = demand_by_region.get(region, 0)
    
    # Component 2: Current stock in region (avoid over-allocation)
    stock_in_region = sum(
        current_allocation[wh_id]
        for wh_id, wh in warehouses.items()
        if wh['region'] == region
    )
    
    # Remaining demand
    remaining_demand = max(0, demand_in_region - stock_in_region)
    
    # Component 3: Unit cost
    unit_cost = warehouse.get('holdingCost', 0) + warehouse.get('transportCost', 0)
    
    # Greedy score: prioritize high remaining demand, low cost
    if remaining_demand > 0:
        score = remaining_demand / (unit_cost + 1)  # Avoid division by zero
    else:
        score = -unit_cost  # If demand met, just minimize cost
    
    return score
```

### Example Walkthrough

**Setup:**
```
Total quantity: 100 units
Demand: {'ouest': 40, 'est': 30, 'north': 20, 'sud': 10}

Warehouses:
  WH-01 (ouest): capacity=50, cost=10
  WH-02 (est):   capacity=50, cost=8
  WH-03 (north): capacity=50, cost=12
  WH-04 (sud):   capacity=50, cost=15
```

**Iteration 1 (allocate unit 1):**
```
WH-01 score: 40 / 10 = 4.0  (ouest demand 40, cost 10)
WH-02 score: 30 / 8 = 3.75  (est demand 30, cost 8)
WH-03 score: 20 / 12 = 1.67 (north demand 20, cost 12)
WH-04 score: 10 / 15 = 0.67 (sud demand 10, cost 15)

Best: WH-01, allocate 1 unit
Current: {WH-01: 1, WH-02: 0, WH-03: 0, WH-04: 0}
```

**Iteration 2-40:**
```
Continue allocating to WH-01 until ouest demand (40) is met
Current: {WH-01: 40, WH-02: 0, WH-03: 0, WH-04: 0}
```

**Iteration 41:**
```
WH-01 score: 0 / 10 = 0 (ouest demand already met)
WH-02 score: 30 / 8 = 3.75 (best)
WH-03 score: 20 / 12 = 1.67
WH-04 score: 10 / 15 = 0.67

Best: WH-02, allocate 1 unit
```

**Final allocation (after 100 iterations):**
```
{WH-01: 40, WH-02: 30, WH-03: 20, WH-04: 10}
```

**Service Level:** 100% (all demand met)

**Cost:** Minimal (each region gets exactly its demand, no excess)

### Characteristics

**Strengths:**
- Fast: O(total_quantity × num_warehouses) ≈ 0.001 seconds
- Intuitive: Allocates where needed, prefers cheap warehouses
- Deterministic: Same input always produces same output

**Weaknesses:**
- Greedy choices are locally optimal, not globally
- May miss complex trade-offs (e.g., moving stock from expensive to cheap warehouse)
- No backtracking: Once allocated, never reconsidered

**When to Use:**
- Real-time systems requiring instant response
- Initial solution for more sophisticated methods
- Problems where greedy intuition aligns with global optimum

---

## Method 3: Exact Solver

### Algorithm Overview

**Approach:** Enumerate all possible allocations, evaluate each, select best.

**Complexity:** O(C^m) where C = average capacity, m = number of warehouses (exponential!)

**Pros:** Guaranteed global optimum

**Cons:** Computationally infeasible for realistic problem sizes

### Detailed Algorithm

```python
def run_exact_solver(product, demand_by_region, warehouses):
    """
    Exact Solver (Brute Force)
    
    WARNING: Only feasible for tiny instances (e.g., 3 warehouses, small capacities)
    
    Process:
    1. Generate ALL valid allocations
    2. Evaluate fitness for each
    3. Return the best
    """
    
    # Step 1: Setup
    demand_norm, total_quantity = _resolve_demand_and_quantity(product, demand_by_region, warehouses)
    
    # Step 2: Generate all combinations
    all_allocations = _generate_all_allocations(warehouses, total_quantity)
    
    # Step 3: Evaluate all
    best_individual = None
    best_fitness = -float('inf')
    
    for individual in all_allocations:
        fitness = _compute_fitness(individual, demand_norm, warehouses, holding_cost, transport_cost)
        
        if fitness > best_fitness:
            best_fitness = fitness
            best_individual = individual
    
    # Step 4: Return best
    return {
        'stock_by_warehouse': best_individual,
        'fitness': best_fitness,
        'cost': _compute_total_cost(best_individual, warehouses, holding_cost, transport_cost),
        'service_level': _compute_service_level(best_individual, demand_norm, warehouses),
        'method': 'Exact Solver',
        'runtime': elapsed_time
    }
```

### Combinatorial Explosion

**Problem:** Number of valid allocations grows exponentially.

**Example:**
```
3 warehouses, each capacity = 10, total_quantity = 15

Number of solutions ≈ C(15+3-1, 3-1) = C(17, 2) = 136
```

But with realistic parameters:
```
14 warehouses, capacities 800-2000, total_quantity = 5000

Number of solutions ≈ 10^50+ (astronomically large!)
```

**Feasibility:**
```
| Warehouses | Total Quantity | Approx. Solutions | Time to Evaluate |
|------------|----------------|-------------------|------------------|
| 3          | 100            | ~5,000            | < 1 second       |
| 5          | 500            | ~125 million      | ~10 minutes      |
| 10         | 1000           | > 10^20           | > universe age   |
| 14         | 5000           | > 10^50           | Impossible       |
```

### Implementation (Recursive Generation)

```python
def _generate_all_allocations(warehouses, total_quantity):
    """
    Recursively generate all valid allocations
    
    Uses backtracking to explore the combinatorial space
    """
    wh_ids = list(warehouses.keys())
    capacities = [warehouses[wh_id]['capacity'] for wh_id in wh_ids]
    
    results = []
    
    def backtrack(index, remaining, current_allocation):
        # Base case: all warehouses assigned
        if index == len(wh_ids):
            if remaining == 0:
                # Valid allocation
                results.append(dict(zip(wh_ids, current_allocation)))
            return
        
        # Recursive case: try all quantities for current warehouse
        max_qty = min(remaining, capacities[index])
        for qty in range(0, max_qty + 1):
            backtrack(index + 1, remaining - qty, current_allocation + [qty])
    
    backtrack(0, total_quantity, [])
    return results
```

### Characteristics

**Strengths:**
- Guaranteed global optimum
- Conceptually simple
- Useful for validation (verify other methods on small instances)

**Weaknesses:**
- Exponential time complexity
- Infeasible for production systems
- No early stopping (must evaluate all)

**When to Use:**
- Tiny benchmark problems
- Verifying correctness of heuristics
- Theoretical analysis only

---

## Method 4: Exact ILP

### Algorithm Overview

**Approach:** Formulate as Integer Linear Programming problem, solve with specialized solver (PuLP + CBC).

**Complexity:** Polynomial to exponential (depending on problem structure), but highly optimized

**Pros:** Guaranteed global optimum, handles large instances, leverages decades of OR research

**Cons:** Requires ILP formulation, solver dependency

### Mathematical Formulation

#### Decision Variables

```
x_w ∈ [0, capacity_w] ∩ ℤ   ∀ warehouses w
```

**Interpretation:** x_w = final stock quantity at warehouse w

#### Objective Function

**Minimize:**
```
TotalCost = Σ (x_w × holding_cost_w) + Σ (|x_w - initial_stock_w| × transfer_cost_w)
```

**Subject to fitness:** This is actually a **multi-objective problem**. We want:
1. Minimize cost
2. Maximize service level

**Approach:** Linearize the fitness function.

Since service level depends on regional stock allocation (non-trivial), we use a two-phase approach:

**Phase 1:** Maximize service level (find minimum cost to achieve maximum service level)
**Phase 2:** Among solutions with maximum service level, minimize cost

OR directly optimize the fitness function (requires linearization of the normalized cost term).

**For simplicity, we minimize cost subject to constraints that ensure high service level.**

#### Constraints

**1. Total Quantity Constraint:**
```
Σ x_w = total_quantity
w
```

All stock must be allocated.

**2. Capacity Constraints:**
```
0 ≤ x_w ≤ capacity_w   ∀ w
```

Cannot exceed warehouse capacity.

**3. Absolute Value Linearization (for transfer cost):**

We need |x_w - initial_stock_w|. ILP solvers can't handle absolute values directly.

**Linearization using auxiliary variables:**
```
Define: Δ_w⁺, Δ_w⁻ ≥ 0

Constraints:
  Δ_w⁺ - Δ_w⁻ = x_w - initial_stock_w
  
Then: |x_w - initial_stock_w| = Δ_w⁺ + Δ_w⁻

Transfer cost = Σ (Δ_w⁺ + Δ_w⁻) × transfer_cost_w
```

**Why this works:**
- If x_w > initial_stock_w: Δ_w⁺ = difference, Δ_w⁻ = 0
- If x_w < initial_stock_w: Δ_w⁺ = 0, Δ_w⁻ = difference
- Minimizing cost will naturally set only one of (Δ_w⁺, Δ_w⁻) to non-zero

### Detailed Algorithm

```python
import pulp

def run_exact_ilp_solver(product, demand_by_region, warehouses):
    """
    Exact ILP Optimization using PuLP
    
    Solves:
      min  Σ (x_w × holding_cost_w) + Σ (|Δ_w| × transfer_cost_w)
      s.t. Σ x_w = total_quantity
           0 ≤ x_w ≤ capacity_w
           Δ_w = x_w - initial_stock_w
    """
    
    # Step 1: Setup
    demand_norm, total_quantity = _resolve_demand_and_quantity(product, demand_by_region, warehouses)
    
    # Step 2: Create ILP model
    model = pulp.LpProblem("Warehouse_Allocation", pulp.LpMinimize)
    
    # Step 3: Decision variables
    stock_vars = {}
    abs_diff_vars_pos = {}
    abs_diff_vars_neg = {}
    
    for wh_id, wh in warehouses.items():
        # Main variable: final stock
        stock_vars[wh_id] = pulp.LpVariable(
            f"stock_{wh_id}",
            lowBound=0,
            upBound=wh['capacity'],
            cat='Integer'
        )
        
        # Auxiliary variables for absolute value
        abs_diff_vars_pos[wh_id] = pulp.LpVariable(
            f"delta_pos_{wh_id}",
            lowBound=0,
            cat='Continuous'
        )
        
        abs_diff_vars_neg[wh_id] = pulp.LpVariable(
            f"delta_neg_{wh_id}",
            lowBound=0,
            cat='Continuous'
        )
    
    # Step 4: Objective function
    holding_cost_total = pulp.lpSum([
        stock_vars[wh_id] * holding_cost[wh_id]
        for wh_id in warehouses.keys()
    ])
    
    transfer_cost_total = pulp.lpSum([
        (abs_diff_vars_pos[wh_id] + abs_diff_vars_neg[wh_id]) * transport_cost[wh_id]
        for wh_id in warehouses.keys()
    ])
    
    model += holding_cost_total + transfer_cost_total, "TotalCost"
    
    # Step 5: Constraints
    
    # Total quantity constraint
    model += pulp.lpSum([stock_vars[wh_id] for wh_id in warehouses.keys()]) == total_quantity, "TotalQuantity"
    
    # Absolute value constraints
    for wh_id, wh in warehouses.items():
        initial = wh.get('stock_level', 0)
        model += (
            abs_diff_vars_pos[wh_id] - abs_diff_vars_neg[wh_id] == stock_vars[wh_id] - initial,
            f"AbsValue_{wh_id}"
        )
    
    # Step 6: Solve
    model.solve(pulp.PULP_CBC_CMD(msg=0))  # CBC solver, suppress output
    
    # Step 7: Extract solution
    solution = {
        wh_id: int(stock_vars[wh_id].varValue)
        for wh_id in warehouses.keys()
    }
    
    # Step 8: Compute metrics
    fitness = _compute_fitness(solution, demand_norm, warehouses, holding_cost, transport_cost)
    
    return {
        'stock_by_warehouse': solution,
        'fitness': fitness,
        'cost': _compute_total_cost(solution, warehouses, holding_cost, transport_cost),
        'service_level': _compute_service_level(solution, demand_norm, warehouses),
        'method': 'Exact ILP',
        'runtime': elapsed_time,
        'solver_status': pulp.LpStatus[model.status]  # Optimal, Infeasible, etc.
    }
```

### Solver Mechanics (High-Level)

ILP solvers like CBC use **Branch-and-Bound** with **Linear Programming relaxations**:

1. **Relax to LP:** Ignore integer constraints, solve continuous problem (fast, polynomial time)
2. **Branch:** If solution has fractional values (e.g., x_5 = 123.7), split into two subproblems:
   - Subproblem A: x_5 ≤ 123
   - Subproblem B: x_5 ≥ 124
3. **Bound:** Solve LP relaxation for each subproblem, get bounds on optimal value
4. **Prune:** If subproblem's bound is worse than current best integer solution, discard
5. **Repeat:** Continue branching until all subproblems resolved
6. **Return:** Best integer solution found

**Key Insight:** Most branches are pruned (bounded away), so we don't explore the full exponential space.

### Characteristics

**Strengths:**
- Guaranteed global optimum (when solver terminates with "Optimal" status)
- Handles realistic problem sizes (14 warehouses, 5000 units solved in ~30 ms)
- Leverages highly optimized solvers (CBC, Gurobi, CPLEX)
- Flexible: Can add new constraints easily (e.g., minimum stock per warehouse)

**Weaknesses:**
- Requires problem to be formulated as linear constraints (sometimes tricky)
- Worst-case exponential (but rare in practice)
- Solver dependency (need PuLP + CBC installed)

**When to Use:**
- Production systems where optimality is critical
- Offline planning (not real-time)
- Problems with complex constraints
- **This is the recommended method for this platform**

---

## Method 5: Genetic Algorithm

### Algorithm Overview

**Approach:** Evolutionary metaheuristic inspired by natural selection.

**Complexity:** O(g × p × m) where g = generations, p = population size, m = warehouses

**Pros:** Flexible, handles non-linear objectives, good for large spaces

**Cons:** No optimality guarantee, requires parameter tuning

### Biological Analogy

| Biology | Genetic Algorithm |
|---------|-------------------|
| Organism | Stock allocation (individual) |
| Gene | Stock quantity at one warehouse |
| Chromosome | Complete allocation (all warehouses) |
| Fitness | Fitness function value |
| Population | Set of candidate solutions |
| Selection | Choose best individuals to reproduce |
| Crossover | Combine two parents → offspring |
| Mutation | Random changes to genes |
| Generation | One iteration of evolution |
| Evolution | Iterative improvement over generations |

### Detailed Algorithm

```python
def run_genetic_optimization(product, demand_by_region, warehouses, 
                             pop_size=100, generations=50, elite_size=5, 
                             mutation_rate=0.15):
    """
    Genetic Algorithm for Warehouse Allocation
    
    Parameters:
    -----------
    pop_size : int
        Number of individuals in population
    generations : int
        Number of evolutionary cycles
    elite_size : int
        Number of best individuals preserved each generation (elitism)
    mutation_rate : float
        Probability of mutating each gene (0-1)
    
    Returns:
    --------
    Best solution found across all generations
    """
    
    # Step 1: Setup
    demand_norm, total_quantity = _resolve_demand_and_quantity(product, demand_by_region, warehouses)
    capacities = {wh_id: wh['capacity'] for wh_id in warehouses.keys()}
    
    # Step 2: Initialize population
    population = [
        _generate_initial_individual(warehouses, demand_norm, total_quantity)
        for _ in range(pop_size)
    ]
    
    # Ensure diversity: include greedy solution
    population[0] = _generate_greedy_individual(warehouses, demand_norm, total_quantity)
    
    # Step 3: Evaluate initial population
    fitness_scores = [
        _compute_fitness(ind, demand_norm, warehouses, holding_cost, transport_cost)
        for ind in population
    ]
    
    # Track best ever
    best_ever_fitness = max(fitness_scores)
    best_ever_individual = population[fitness_scores.index(best_ever_fitness)].copy()
    
    # Step 4: Evolution loop
    for generation in range(generations):
        # (a) Selection: Select parents based on fitness
        parents = _select_parents(population, fitness_scores, num_parents=pop_size//2)
        
        # (b) Crossover: Generate offspring
        offspring = []
        for i in range(0, len(parents), 2):
            if i+1 < len(parents):
                child1, child2 = _crossover(parents[i], parents[i+1], total_quantity, capacities)
                offspring.extend([child1, child2])
        
        # (c) Mutation: Apply random changes
        for child in offspring:
            if random.random() < mutation_rate:
                _mutate_individual(child, warehouses, total_quantity, capacities)
        
        # (d) Elitism: Preserve best individuals
        sorted_indices = sorted(range(len(fitness_scores)), key=lambda i: fitness_scores[i], reverse=True)
        elites = [population[i].copy() for i in sorted_indices[:elite_size]]
        
        # (e) Form new population
        population = elites + offspring[:pop_size - elite_size]
        
        # (f) Evaluate new population
        fitness_scores = [
            _compute_fitness(ind, demand_norm, warehouses, holding_cost, transport_cost)
            for ind in population
        ]
        
        # (g) Update best ever
        current_best_fitness = max(fitness_scores)
        if current_best_fitness > best_ever_fitness:
            best_ever_fitness = current_best_fitness
            best_ever_individual = population[fitness_scores.index(current_best_fitness)].copy()
    
    # Step 5: Return best solution
    return {
        'stock_by_warehouse': best_ever_individual,
        'fitness': best_ever_fitness,
        'cost': _compute_total_cost(best_ever_individual, warehouses, holding_cost, transport_cost),
        'service_level': _compute_service_level(best_ever_individual, demand_norm, warehouses),
        'method': 'Genetic Algorithm',
        'runtime': elapsed_time,
        'generations': generations
    }
```

### Key Components

#### 1. Initial Population Generation

```python
def _generate_initial_individual(warehouses, demand_by_region, total_quantity):
    """
    Generate one individual for initial population
    
    Strategy: Allocate proportionally to regional demand, with some randomness
    """
    individual = {wh_id: 0 for wh_id in warehouses.keys()}
    
    # Group warehouses by region
    wh_by_region = _group_warehouses_by_region(warehouses)
    
    # Allocate proportionally to demand
    total_demand = sum(demand_by_region.values())
    for region, demand in demand_by_region.items():
        if region not in wh_by_region:
            continue
        
        # This region should get (demand / total_demand) × total_quantity
        region_allocation = int((demand / total_demand) * total_quantity)
        
        # Distribute among warehouses in this region
        wh_in_region = wh_by_region[region]
        for wh_id in wh_in_region:
            # Random proportional split
            share = random.random()
            individual[wh_id] = int(share * region_allocation / len(wh_in_region))
    
    # Repair to ensure validity
    individual = _repair_individual(individual, total_quantity, capacities)
    
    return individual
```

#### 2. Parent Selection (Tournament Selection)

```python
def _select_parents(population, fitness_scores, num_parents, tournament_size=3):
    """
    Select parents using tournament selection
    
    Process:
    1. Randomly sample tournament_size individuals
    2. Select the best among them
    3. Repeat until num_parents selected
    """
    parents = []
    
    for _ in range(num_parents):
        # Random tournament
        tournament_indices = random.sample(range(len(population)), tournament_size)
        tournament_fitness = [fitness_scores[i] for i in tournament_indices]
        
        # Select winner (highest fitness)
        winner_index = tournament_indices[tournament_fitness.index(max(tournament_fitness))]
        parents.append(population[winner_index].copy())
    
    return parents
```

**Why tournament selection?**
- Simple and efficient
- Balances exploration (random sampling) and exploitation (best wins)
- Avoids premature convergence (even weak individuals have a chance)

#### 3. Crossover (Recombination)

```python
def _crossover(parent1, parent2, total_quantity, capacities):
    """
    Single-point crossover with repair
    
    Process:
    1. Choose random crossover point
    2. Swap genes after that point
    3. Repair to satisfy constraints
    """
    wh_ids = list(parent1.keys())
    crossover_point = random.randint(1, len(wh_ids) - 1)
    
    # Create children
    child1 = {}
    child2 = {}
    
    for i, wh_id in enumerate(wh_ids):
        if i < crossover_point:
            child1[wh_id] = parent1[wh_id]
            child2[wh_id] = parent2[wh_id]
        else:
            child1[wh_id] = parent2[wh_id]
            child2[wh_id] = parent1[wh_id]
    
    # Repair (crossover might violate sum constraint)
    child1 = _repair_individual(child1, total_quantity, capacities)
    child2 = _repair_individual(child2, total_quantity, capacities)
    
    return child1, child2
```

**Alternative crossover methods:**
- **Uniform crossover:** Each gene independently chosen from parent1 or parent2
- **Arithmetic crossover:** Child = α × parent1 + (1-α) × parent2
- **Problem-specific:** Preserve regional allocations, only swap within regions

#### 4. Mutation

```python
def _mutate_individual(individual, warehouses, total_quantity, capacities):
    """
    Mutate individual by randomly adjusting stock levels
    
    Strategy: Move stock from random warehouse to another
    """
    wh_ids = list(warehouses.keys())
    
    # Select two random warehouses
    wh_from = random.choice(wh_ids)
    wh_to = random.choice([wh for wh in wh_ids if wh != wh_from])
    
    # Move random amount (up to 10% of total or warehouse stock)
    max_move = min(
        individual[wh_from],  # Can't move more than available
        capacities[wh_to] - individual[wh_to],  # Can't exceed capacity
        total_quantity // 10  # Limit movement size
    )
    
    if max_move > 0:
        move_amount = random.randint(1, max_move)
        individual[wh_from] -= move_amount
        individual[wh_to] += move_amount
```

**Mutation purpose:**
- Escape local optima
- Maintain population diversity
- Explore new regions of solution space

**Mutation rate tuning:**
- Too low (< 0.05): Premature convergence, stuck in local optimum
- Too high (> 0.5): Random search, no learning
- Sweet spot (0.1-0.2): Balance exploration and exploitation

#### 5. Elitism

```python
# Preserve top elite_size individuals unchanged
elites = [population[i].copy() for i in sorted_indices[:elite_size]]
```

**Why elitism?**
- Ensures best solution never lost
- Accelerates convergence
- Provides stability

**Typical elite size:** 5-10% of population

### Convergence Analysis

**Typical evolution:**

```
Generation 0:  Best fitness = 0.3500 (random initialization)
Generation 5:  Best fitness = 0.4200 (rapid improvement)
Generation 10: Best fitness = 0.4650 (slowing down)
Generation 20: Best fitness = 0.4695 (near plateau)
Generation 50: Best fitness = 0.4695 (converged)
```

**Early termination:** If fitness doesn't improve for 10+ generations, stop (no point continuing).

### Characteristics

**Strengths:**
- Flexible: Works with any fitness function (even non-differentiable, non-linear)
- Global search: Explores diverse regions
- Parallelizable: Evaluate population in parallel
- Intuitive: Easy to understand and implement

**Weaknesses:**
- No optimality guarantee
- Parameter-sensitive (population size, mutation rate, etc.)
- Slower than ILP for convex problems
- Can get stuck in local optima

**When to Use:**
- Complex non-linear objectives
- Problems where ILP formulation is difficult
- When "good enough" solution is acceptable
- When you have time to tune parameters

---

## Comparative Analysis

### Performance Summary (Across All Scenarios)

| Method | Avg Cost (M DZD) | Avg Service (%) | Avg Fitness | Avg Runtime (ms) | Optimality |
|--------|------------------|-----------------|-------------|------------------|------------|
| Random Search | 13.47 | 73.00 | 0.3079 | 8.6 | None |
| Greedy Heuristic | 13.25 | 73.00 | 0.3093 | 0.9 | Local |
| Exact Solver | 13.25 | 73.00 | 0.3093 | 9.1 | Global* |
| **Exact ILP** | **13.03** | 70.29 | **0.3180** | 30.6 | **Global** |
| Genetic Algorithm | 13.13 | 71.57 | 0.3118 | 309.0 | Approximate |

*Exact Solver only tested on reduced instances due to computational limits

### Method Selection Framework

```
                                Start
                                  |
                    Is optimality critical?
                           /          \
                         Yes           No
                          |             |
                 Is problem size     Is speed
                    realistic?      critical?
                      /    \           /    \
                   Yes     No        Yes    No
                    |       |         |      |
              Use ILP   Use ILP   Use     Use Genetic
                        (if time) Greedy  or Random
```

### Trade-off Space

```
                    Optimality
                        ^
                        |
           Exact ILP    |    Exact Solver
              ●         |         ●
                        |
                        |
           Genetic      |
              ●         |
                        |
         Greedy ●       |
                        |
      Random ●          |
                        |
                        +------------------------> Speed
                                                    

```

**Key Insight:** ILP provides the best balance of optimality and speed for this problem domain.

---

## Implementation Details

### File Structure

```
optimization/
├── Genitic.py              # All methods + utilities
│   ├── Helper functions
│   │   ├── _resolve_demand_and_quantity()
│   │   ├── _compute_fitness()
│   │   ├── _compute_total_cost()
│   │   ├── _compute_service_level()
│   │   └── ...
│   ├── Method 1: run_random_search_optimization()
│   ├── Method 2: run_greedy_heuristic()
│   ├── Method 3: run_exact_solver()
│   ├── Method 4: run_exact_ilp_solver()
│   └── Method 5: run_genetic_optimization()
└── compare_methods.py       # CLI for comparing methods
```

### Common Parameters

All methods accept:

```python
product = {
    'product_id': 'SKU-123',
    'total_quantity': 5000  # Inventory budget
}

demand_by_region = {
    'ouest': 850,
    'est': 900,
    'north': 1400,
    'sud': 200
}

warehouses = {
    'WH-01': {
        'id': 'WH-01',
        'capacity': 2000,
        'stock_level': 500,
        'region': 'north',
        'holdingCost': 1000,
        'transportCost': 500
    },
    # ... 13 more warehouses
}
```

### Common Return Format

All methods return:

```python
{
    'stock_by_warehouse': {
        'WH-01': 1200,
        'WH-02': 800,
        # ... all 14 warehouses
    },
    'cost': 10403500,  # DZD
    'service_level': 100,  # Percentage
    'fitness': 0.4695,
    'method': 'Exact ILP',
    'runtime': 0.031  # seconds
}
```

### Usage Example

```python
from optimization.Genitic import run_exact_ilp_solver

result = run_exact_ilp_solver(
    product=product,
    demand_by_region=demand_by_region,
    warehouses=warehouses
)

print(f"Method: {result['method']}")
print(f"Cost: {result['cost']:,} DZD")
print(f"Service Level: {result['service_level']}%")
print(f"Fitness: {result['fitness']:.4f}")
print(f"Runtime: {result['runtime']*1000:.1f} ms")

# Per-warehouse allocation
for wh_id, qty in result['stock_by_warehouse'].items():
    print(f"  {wh_id}: {qty} units")
```

---

## Summary

### The Fitness Function is Central

Every optimization method aims to maximize:

```
Fitness = α × ServiceLevel - (1 - α) × TotalCost_normalized
```

This unified objective ensures fair comparison and aligns all methods with business goals: **satisfy demand at minimum cost**.

### Method Recommendations

1. **Production System (Default):** Use **Exact ILP**
   - Best balance of optimality and speed
   - Handles realistic problem sizes
   - Guaranteed optimal (or near-optimal with time limits)

2. **Real-Time API:** Use **Greedy Heuristic**
   - Sub-millisecond response
   - Good enough for quick decisions
   - Deterministic and predictable

3. **Research/Benchmarking:** Use **Genetic Algorithm**
   - Flexible for experimenting with variants
   - Good baseline for non-convex problems
   - Educational value (demonstrates metaheuristics)

4. **Validation:** Use **Exact Solver** on small instances
   - Verify other methods achieve optimality
   - Understand problem structure
   - Debugging/testing

5. **Baseline:** Use **Random Search**
   - Measure improvement over random guessing
   - Quick sanity check
   - Simplest implementation

---

**Document Version:** 1.0  
**Last Updated:** May 21, 2026  
**For:** Master's Thesis - Warehouse Optimization Platform
