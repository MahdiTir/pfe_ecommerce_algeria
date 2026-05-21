# Warehouse Optimization - Usage Guide

## Understanding the Two Key Parameters

### 1. **Demand Forecast** (`--demand`)
- **Source:** SARIMAX time series forecasting model
- **Meaning:** Expected customer demand per region
- **Purpose:** Tells the optimizer WHERE customers need products
- **Example:** `"ouest:850,est:900,north:1400,sud:200"` means customers need 850 units in ouest, 900 in est, etc.

### 2. **Inventory Budget** (`--quantity`)
- **Source:** Business decision / budget constraint
- **Meaning:** Total units the seller wants to store across all warehouses
- **Purpose:** Tells the optimizer HOW MUCH inventory to distribute
- **Example:** `5000` means distribute 5,000 units total

## Key Concept: They Are Independent!

```
Demand ≠ Quantity
```

- **If Quantity > Demand:** Over-stocking (buffer inventory, safety stock)
- **If Quantity = Demand:** Just-in-time inventory
- **If Quantity < Demand:** Under-stocking (stockouts, prioritize regions)

## Usage Examples

### Example 1: Over-Stocked (Safety Buffer)
```bash
python -m optimization.compare_methods \
  --demand "ouest:850,est:900,north:1400,sud:200" \
  --quantity 5000
```

**Result:**
- **Demand:** 3,350 units needed by customers
- **Allocating:** 5,000 units (49% more than demand)
- **Effect:** Extra 1,650 units distributed as safety stock
- **Service Level:** 100% (all regions covered)
- **Cost:** Higher holding costs due to extra inventory

```
| Method            |    Total Cost | Service Level | Stock Distribution        |
| ILP (Best)        | 10,403,500 DZD |         100% | ouest:850, est:2550, north:1400, sud:200 |
| Others            | 10,685,990 DZD |         100% | ouest:1269, est:1343, north:2090, sud:298 |
```

**Analysis:** ILP puts extra inventory (1,700 units) entirely in "est" region (cheapest holding cost)

---

### Example 2: Just-in-Time
```bash
python -m optimization.compare_methods \
  --demand "ouest:850,est:900,north:1400,sud:200" \
  --quantity 3350
```

**Result:**
- **Demand:** 3,350 units needed
- **Allocating:** 3,350 units (exact match)
- **Effect:** No buffer, perfect alignment
- **Service Level:** 100%
- **Cost:** Minimal (no excess inventory)

```
| Method            |    Total Cost | Service Level | Stock Distribution        |
| All Methods       | 10,073,500 DZD |         100% | ouest:850, est:900, north:1400, sud:200 |
```

**Analysis:** All methods converge - allocate exactly what's needed per region

---

### Example 3: Under-Stocked (Capacity Constraint)
```bash
python -m optimization.compare_methods \
  --demand "ouest:850,est:900,north:1400,sud:200" \
  --quantity 2000
```

**Result:**
- **Demand:** 3,350 units needed
- **Allocating:** 2,000 units (40% shortage)
- **Effect:** Must prioritize regions, some will be under-served
- **Service Level:** 45%-60% (depends on method)
- **Cost:** Lower overall, but opportunity cost from lost sales

```
| Method            |    Total Cost | Service Level | Stock Distribution        |
| ILP               | 9,450,000 DZD |          45% | ouest:0, est:900, north:1100, sud:0 |
| Others            | 9,572,440 DZD |          60% | ouest:508, est:537, north:836, sud:119 |
```

**Analysis:** 
- **ILP Strategy:** Focus scarce inventory on 2 regions, fully satisfy est, partially satisfy north
- **Other Methods:** Spread thin across all 4 regions proportionally

---

### Example 4: Medium Demand with Moderate Budget
```bash
python -m optimization.compare_methods \
  --demand "ouest:2500,est:3000,north:5000,sud:1500" \
  --quantity 15000
```

**Result:**
- **Demand:** 12,000 units needed
- **Allocating:** 15,000 units (25% buffer)
- **Service Level:** 100%
- **Cost Variation:** 14.5M - 19M DZD (method quality matters!)

```
| Method            |    Total Cost | Service Level | Stock Distribution        |
| ILP (Best)        | 14,493,000 DZD |         100% | ouest:2500, est:6000, north:5000, sud:1500 |
| Genetic           | 14,982,710 DZD |         100% | ouest:3125, est:3750, north:6250, sud:1875 |
| Greedy            | 18,129,250 DZD |         100% | ouest:3125, est:4000, north:6000, sud:1875 |
| Random            | 18,997,000 DZD |         100% | ouest:2500, est:3000, north:5000, sud:1500 |
```

**Key Insight:** ILP saves **4.5M DZD (24%)** by putting 3,000 extra units in cheap "est" region

---

## Real-World Scenarios

### Scenario A: Conservative Retailer
**Goal:** Never stockout, willing to pay for safety buffer

```bash
python -m optimization.compare_methods \
  --demand "ouest:1000,est:1500,north:2000,sud:500" \
  --quantity 6500  # 30% buffer
```

### Scenario B: Lean Manufacturer
**Goal:** Minimize inventory costs, trust forecast

```bash
python -m optimization.compare_methods \
  --demand "ouest:1000,est:1500,north:2000,sud:500" \
  --quantity 5000  # exact demand
```

### Scenario C: Budget-Constrained Startup
**Goal:** Limited capital, must prioritize

```bash
python -m optimization.compare_methods \
  --demand "ouest:1000,est:1500,north:2000,sud:500" \
  --quantity 3000  # 40% shortage, prioritize high-demand regions
```

---

## Command Line Reference

### Basic Usage
```bash
python -m optimization.compare_methods [OPTIONS]
```

### Options

#### `--demand` or `-d`
Format: `"region1:value1,region2:value2,..."`

Example:
```bash
--demand "ouest:850,est:900,north:1400,sud:200"
```

#### `--quantity` or `-q`
Format: Integer

Example:
```bash
--quantity 5000
```

**If not specified:** Uses `current_stock + total_demand` as default

---

## Interpreting Results

### Columns Explained

| Column | Meaning |
|--------|---------|
| **Method** | Optimization algorithm used |
| **Total Cost** | Holding cost + Transport cost (in DZD) |
| **Service Level** | % of demand satisfied (average across regions) |
| **Fitness** | Combined score (higher = better) |
| **Runtime** | Execution time in seconds |
| **Stock by Region** | Final allocation per region |

### Service Level Calculation
```
Service Level = Average of (min(allocated/demand, 1.0) per region)

Example:
- ouest: 850/850 = 100%
- est: 900/900 = 100%
- north: 1400/1400 = 100%
- sud: 200/200 = 100%
→ Service Level = 100%

Counter-example (under-stocked):
- ouest: 0/850 = 0%
- est: 900/900 = 100%
- north: 1100/1400 = 79%
- sud: 0/200 = 0%
→ Service Level = 45%
```

---

## Method Selection Guide

| Scenario | Best Method | Why |
|----------|-------------|-----|
| **Production planning** | ILP | Mathematically optimal |
| **Real-time decisions** | Greedy | Fastest (< 1ms) |
| **Very large scale** | Genetic | Scalable, near-optimal |
| **Quick estimate** | Random | Fast approximation |
| **Validation/Testing** | Exact Solver | Verify other methods |

---

## Cost Optimization Tips

1. **Use ILP or Genetic** when quantity significantly exceeds demand
   - These methods excel at placing buffer inventory in cheap locations

2. **All methods converge** when quantity equals demand exactly
   - Use fastest method (Greedy) in this case

3. **Under constraints**, ILP makes better prioritization decisions
   - Focuses limited inventory where it matters most

4. **Holding costs dominate** - favor warehouses with low holding costs for buffer stock

5. **Transport costs matter** when redistributing from initial stock levels

---

## Integration with SARIMAX

In production workflow:

```python
# 1. Get demand forecast from SARIMAX
demand_forecast = sarimax_model.predict(horizon=30)
# Example output: {"ouest": 850, "est": 900, "north": 1400, "sud": 200}

# 2. Determine inventory budget (business decision)
total_inventory_budget = 5000  # seller decides

# 3. Run optimization
python -m optimization.compare_methods \
  --demand "ouest:850,est:900,north:1400,sud:200" \
  --quantity 5000

# 4. Get optimal allocation per warehouse
# Use ILP result for production planning
```

---

## Testing Different Strategies

### Conservative (High Safety Stock)
```bash
for qty in 4000 5000 6000 7000; do
  echo "Testing with $qty units"
  python -m optimization.compare_methods \
    --demand "ouest:850,est:900,north:1400,sud:200" \
    --quantity $qty
done
```

### Lean (Tight Inventory)
```bash
for qty in 2000 2500 3000 3350; do
  echo "Testing with $qty units"
  python -m optimization.compare_methods \
    --demand "ouest:850,est:900,north:1400,sud:200" \
    --quantity $qty
done
```

---

## Summary

✅ **Demand** = Customer needs (from forecast)  
✅ **Quantity** = Inventory budget (business decision)  
✅ Optimization distributes **Quantity** to best satisfy **Demand**  
✅ Trade-off: Cost vs Service Level  
✅ Use ILP for optimal decisions, Greedy for speed
