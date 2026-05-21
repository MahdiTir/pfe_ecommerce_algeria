# Usage Cases — Quick Reference

## Command

```bash
cd e:\Projects\pfe_ecommerce_algeria

python -m optimization.compare_methods \
  --demand "ouest:X,est:Y,north:Z,sud:W" \
  --quantity N \
  [--config FILE.json] \
  [--warehouse-detail]
```

| Flag | Meaning |
|------|---------|
| `--demand` / `-d` | SARIMAX forecast per region (customer need) |
| `--quantity` / `-q` | Total units to put in warehouses (seller budget) |
| `--config` / `-c` | Warehouse JSON (default: `reduced_14_warehouses.json`) |
| `--warehouse-detail` / `-w` | Show how much per warehouse |

**Rule:** `quantity` is how much to distribute; `demand` is what customers need. They are independent.

---

## A. Standard cases (`reduced_14_warehouses.json`)

### 1. Over-stocked (safety buffer)
Demand 3,350 → Quantity **5,000** (+49% buffer)

```bash
python -m optimization.compare_methods --demand "ouest:850,est:900,north:1400,sud:200" --quantity 5000
```

| Best (ILP) | Cost | Service | Allocation |
|------------|------|---------|------------|
| ILP | 10,403,500 DZD | 100% | ouest:850, **est:2550**, north:1400, sud:200 |

Extra stock goes to cheap **est** region.

---

### 2. Just-in-time (quantity = demand)
Demand 3,350 → Quantity **3,350**

```bash
python -m optimization.compare_methods --demand "ouest:850,est:900,north:1400,sud:200" --quantity 3350
```

| All methods | Cost | Service |
|-------------|------|---------|
| All tied | 10,073,500 DZD | 100% |

---

### 3. Under-stocked (prioritize regions)
Demand 3,350 → Quantity **2,000** (−40%)

```bash
python -m optimization.compare_methods --demand "ouest:850,est:900,north:1400,sud:200" --quantity 2000
```

| Method | Cost | Service | Strategy |
|--------|------|---------|----------|
| ILP | 9,450,000 DZD | 45% | est:900, north:1100, ouest/sud:0 |
| Others | ~9,572,000 DZD | 60% | Spread thin on all 4 regions |

---

### 4. Medium demand + buffer
Demand 12,000 → Quantity **15,000** (+25%)

```bash
python -m optimization.compare_methods --demand "ouest:2500,est:3000,north:5000,sud:1500" --quantity 15000
```

| Method | Cost | Service |
|--------|------|---------|
| **ILP** | **14,493,000 DZD** | 100% |
| Genetic | 14,982,800 DZD | 100% |
| Greedy | 18,129,250 DZD | 100% |
| Random | 18,997,000 DZD | 100% |

ILP buffer: +3,000 in **est** (6000 vs 3000 demand).

---

## B. Real-world business scenarios

### Conservative retailer (~30% buffer)
```bash
python -m optimization.compare_methods --demand "ouest:1000,est:1500,north:2000,sud:500" --quantity 6500
```

### Lean manufacturer (exact stock)
```bash
python -m optimization.compare_methods --demand "ouest:1000,est:1500,north:2000,sud:500" --quantity 5000
```

### Budget startup (40% shortage)
```bash
python -m optimization.compare_methods --demand "ouest:1000,est:1500,north:2000,sud:500" --quantity 3000
```

---

## C. Edge cases (`edge_case_14_warehouses.json`)

North-heavy (6 WH), thin ouest (2 WH), expensive sud.

### E1 — Demand >> quantity
```bash
python -m optimization.compare_methods --config edge_case_14_warehouses.json \
  --demand "ouest:6000,est:5000,north:9000,sud:4000" --quantity 11000 --warehouse-detail
```

| ILP | 12,175,000 DZD | 42% | Uses W_E1, W_E2, W_E3, W_N1_HUB, W_N6_DEPOT |

### E2 — Ouest demand > ouest capacity (8k demand, 5k max in ouest)
```bash
python -m optimization.compare_methods --config edge_case_14_warehouses.json \
  --demand "ouest:8000,est:4000,north:12000,sud:3000" --quantity 14000 --warehouse-detail
```

| ILP | 13,775,000 DZD | 46% | ouest:0 — floods north cluster |

### E3 — Moderate shortage
```bash
python -m optimization.compare_methods --config edge_case_14_warehouses.json \
  --demand "ouest:3000,est:2500,north:4000,sud:1500" --quantity 5500 --warehouse-detail
```

---

## D. Extreme unbalanced (`extreme_test_warehouses.json`)

No ouest warehouses (0 in region). 6 WH total.

```bash
python -m optimization.compare_methods --config extreme_test_warehouses.json \
  --demand "ouest:5000,est:4000,north:8000,sud:3000" --quantity 10000 --warehouse-detail
```

---

## Which method when?

| Situation | Use |
|-----------|-----|
| Production / best plan | **Exact ILP** |
| Fast UI / live tool | **Greedy Heuristic** |
| Huge problem, ILP slow | **Genetic Algorithm** |
| Sanity check | **Exact Solver** or Random |

---

## Config files

| File | Warehouses | Edge |
|------|------------|------|
| `reduced_14_warehouses.json` | 14, balanced | Default tests |
| `edge_case_14_warehouses.json` | 14, north-heavy | Ouest bottleneck |
| `extreme_test_warehouses.json` | 6, no ouest | Missing region |

Full details: `USAGE_GUIDE.md`, `EDGE_CASES_AND_RESULTS.md`
