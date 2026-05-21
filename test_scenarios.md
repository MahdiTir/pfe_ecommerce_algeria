# Optimization Test Scenarios

## Test Configuration

### Warehouse Distribution (14 warehouses total)

**North Region (4 warehouses):**
- Total Capacity: 18,500 units
- Total Initial Stock: 9,500 units
- Transport Cost Range: 220-300 DZD/unit
- Holding Cost Range: 700-850 DZD/unit

**Est Region (3 warehouses):**
- Total Capacity: 13,000 units
- Total Initial Stock: 6,300 units
- Transport Cost Range: 300-350 DZD/unit
- Holding Cost Range: 550-650 DZD/unit

**Ouest Region (3 warehouses):**
- Total Capacity: 10,500 units
- Total Initial Stock: 5,200 units
- Transport Cost Range: 380-420 DZD/unit
- Holding Cost Range: 850-950 DZD/unit

**Sud Region (4 warehouses):**
- Total Capacity: 9,500 units
- Total Initial Stock: 4,750 units
- Transport Cost Range: 430-500 DZD/unit
- Holding Cost Range: 950-1200 DZD/unit

**Total System:**
- Total Capacity: 51,500 units
- Total Initial Stock: 25,750 units

## Test Scenarios & Results

### Scenario 1: Low Demand (Under Initial Stock)
**Demand:** ouest:850, est:900, north:1,400, sud:200 (Total: 3,350 units)

**Results:**
- All methods achieve 100% service level
- Total allocation: 3,350 units (exactly matching demand)
- Cost range: 10,073,500 - 10,079,500 DZD
- Best methods: Greedy, Exact Solver, ILP, Genetic (all tied at 10,073,500 DZD)
- Fitness: 0.4779

**Key Insight:** When demand is well below stock, all methods converge to similar solutions focusing on minimizing holding and transport costs.

---

### Scenario 2: Medium Demand (Below Capacity)
**Demand:** ouest:2,500, est:3,000, north:5,000, sud:1,500 (Total: 12,000 units)

**Results:**
- All methods achieve 100% service level
- Total allocation: 12,000 units
- Cost range: 13,569,000 - 15,280,000 DZD
- **Performance ranking:**
  1. ILP & Genetic: ~13,569,000 DZD (best) ✅
  2. Greedy & Exact Solver: 15,029,000 DZD
  3. Random Search: 15,280,000 DZD (worst)
- Fitness: ILP/Genetic = 0.4182, Others = 0.4100-0.4119

**Key Insight:** Method quality becomes apparent. ILP and Genetic Algorithm find 10% cheaper solutions by better optimizing warehouse selection and allocation distribution.

---

### Scenario 3: High Demand (Near/At Capacity)
**Demand:** ouest:5,000, est:6,000, north:10,000, sud:4,000 (Total: 25,000 units)

**Results:**
- Service level varies by method (77%-100%)
- Total allocation: 18,500 - 25,000 units
- Cost range: 20,394,000 - 22,630,000 DZD
- **Performance ranking:**
  1. ILP: 20,394,000 DZD, 100% service (best) ✅
  2. Genetic: 20,397,430 DZD, 100% service ✅
  3. Greedy/Exact: 22,630,000 DZD, 79% service
  4. Random: 22,480,000 DZD, 77% service
- Fitness: ILP/Genetic = 0.316, Others = 0.228-0.236

**Key Insight:** Under capacity pressure, sophisticated methods (ILP, Genetic) significantly outperform simpler heuristics. They achieve full demand satisfaction while cheaper methods fail to meet demand in all regions.

---

## Method Comparison Summary

### Random Search
- **Speed:** ⚡⚡⚡ Very Fast (0.007-0.008s)
- **Quality:** ⭐⭐ Poor to Moderate
- **Best Use:** Quick baseline, simple problems
- **Weakness:** Inconsistent, misses optimal solutions

### Greedy Heuristic
- **Speed:** ⚡⚡⚡⚡ Fastest (0.000-0.001s)
- **Quality:** ⭐⭐⭐ Good
- **Best Use:** Fast approximations, real-time decisions
- **Weakness:** Local optima, suboptimal under constraints

### Exact Solver
- **Speed:** ⚡⚡⚡ Fast (0.003-0.010s)
- **Quality:** ⭐⭐⭐ Good (same as Greedy in these tests)
- **Best Use:** Small to medium instances with region-based allocation
- **Weakness:** Doesn't explore full solution space

### Exact ILP (Integer Linear Programming)
- **Speed:** ⚡⚡ Moderate (0.036-0.121s)
- **Quality:** ⭐⭐⭐⭐⭐ Excellent
- **Best Use:** High-stakes decisions requiring optimal solutions
- **Strength:** Mathematically optimal, handles complex constraints

### Genetic Algorithm
- **Speed:** ⚡ Slower (0.269-0.351s)
- **Quality:** ⭐⭐⭐⭐⭐ Excellent (near-optimal)
- **Best Use:** Very large problems where ILP is too slow
- **Strength:** Scalable, flexible, near-optimal solutions

---

## Recommendations

1. **For Production Planning (Offline):** Use **ILP** for guaranteed optimal solutions
2. **For Real-Time Operations:** Use **Greedy Heuristic** for speed
3. **For Very Large Scale:** Use **Genetic Algorithm** when ILP becomes too slow
4. **For Validation:** Use **Exact Solver** to verify other methods on smaller instances

---

## Cost Structure Insights

From the test results:
- **Holding costs dominate** in low-demand scenarios (70-80% of total cost)
- **Transport costs matter most** when reallocating from high-stock regions
- **Sud region is most expensive** (highest holding + transport costs)
- **North region is cheapest** (good balance of costs and capacity)
- **ILP/Genetic save 10-20%** on costs by intelligent warehouse selection

---

## Testing Command

Run custom demand scenarios:
```bash
python -m optimization.compare_methods --demand "ouest:X,est:Y,north:Z,sud:W"
```

Example:
```bash
python -m optimization.compare_methods --demand "ouest:2500,est:3000,north:5000,sud:1500"
```
