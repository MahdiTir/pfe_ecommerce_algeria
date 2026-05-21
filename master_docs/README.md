# Master's Thesis Documentation

## Overview

This folder contains comprehensive technical documentation for the E-commerce Warehouse Optimization Platform for Algeria. These documents are designed to support your master's thesis by providing detailed explanations of all system components, algorithms, and implementation details.

---

## Document Structure

### Document 1: SARIMAX Technical Guide
**File:** `1_SARIMAX_TECHNICAL_GUIDE.md`

**Purpose:** Complete technical explanation of the SARIMAX forecasting model

**Contents:**
- Mathematical foundation (AR, I, MA, Seasonal components)
- Model components explained in detail
- Parameter selection methods (AIC, BIC, Auto-ARIMA)
- Model training process
- Forecasting mechanism with examples
- **Implementation approach:** Pre-trained models stored in `sarimax_x/model/`
- Offline training procedures
- Advantages and limitations

**Key Insight:** Models are trained offline and loaded during API requests, reducing response time from ~120ms to ~5-10ms.

**Use For:**
- Explaining demand forecasting methodology in thesis
- Understanding time series forecasting
- Documenting model training procedures
- Citations in methodology chapter

---

### Document 2: Optimization Methods Technical Documentation
**File:** `2_OPTIMIZATION_METHODS_TECHNICAL.md`

**Purpose:** Comprehensive explanation of all five optimization algorithms

**Contents:**
- **The Fitness Function** (central concept):
  - `Fitness = α × ServiceLevel - (1-α) × TotalCost_normalized`
  - Multi-objective optimization balancing service and cost
  - Role in guiding all optimization methods
- Cost components (holding cost + transfer cost)
- Service level calculation
- Five methods in detail:
  1. Random Search (baseline)
  2. Greedy Heuristic (fast, local optimum)
  3. Exact Solver (brute force, small instances)
  4. **Exact ILP** (recommended, globally optimal)
  5. Genetic Algorithm (metaheuristic)
- Comparative analysis
- Implementation details

**Key Insight:** Exact ILP provides the best balance of optimality and speed (~30ms runtime with guaranteed optimal solutions).

**Use For:**
- Methodology chapter (optimization algorithms)
- Results chapter (method comparison)
- Explaining fitness function and cost calculation
- Justifying method selection (ILP)

---

### Document 3: API Integration (Forecasting + ILP)
**File:** `3_API_INTEGRATION_FORECASTING_ILP.md`

**Purpose:** Explains how SARIMAX and Exact ILP integrate in the API

**Contents:**
- System architecture overview
- API endpoint design (`POST /api/forecasting/genetic`)
- Complete data flow (request → forecast → optimize → response)
- **Forecasting stage:** Loading pre-trained SARIMAX models from `sarimax_x/model/`
- **Optimization stage:** Running Exact ILP solver
- Integration logic with complete code examples
- Error handling strategies
- Performance considerations (caching, async processing)
- Example request/response

**Key Insight:** The endpoint name is `/forecasting/genetic` for backward compatibility, but actually uses **Exact ILP** as the default optimization method.

**Timing Breakdown (Updated):**
- Request validation: 2 ms
- Database queries: 50 ms
- Load SARIMAX model: 5 ms
- Generate forecast: 5 ms
- ILP optimization: 31 ms
- Post-processing: 2 ms
- **Total: ~95 ms**

**Use For:**
- System integration chapter
- API documentation
- Explaining end-to-end process
- Performance analysis

---

### Document 4: Platform Process Flow
**File:** `4_PLATFORM_PROCESS_FLOW.md`

**Purpose:** End-to-end user journey and system architecture

**Contents:**
- Complete system architecture (all layers)
- Technology stack
- User journey (persona: Operations Manager named Sarah)
- Frontend flow (login → dashboard → optimization → results)
- Backend processing (detailed API handlers)
- Database operations (schema, queries)
- Results visualization (charts, tables, recommendations)
- Deployment architecture (Docker, Kubernetes)
- Security and authentication (JWT)
- Monitoring and logging
- Complete example walkthrough

**Key Insight:** Production-ready architecture supporting full workflow from user request to warehouse execution.

**Use For:**
- System design chapter
- User interface screenshots
- Deployment documentation
- Complete system overview

---

## Quick Reference Table

| Topic | Document | Key Sections |
|-------|----------|--------------|
| **Demand Forecasting** | Doc 1 | Mathematical Foundation, Forecasting Mechanism |
| **Offline Model Training** | Doc 1 | Offline Model Training section |
| **Fitness Function** | Doc 2 | The Fitness Function (pages 1-5) |
| **Cost Calculation** | Doc 2 | Cost Components |
| **ILP Formulation** | Doc 2 | Method 4: Exact ILP |
| **Method Comparison** | Doc 2 | Comparative Analysis |
| **API Design** | Doc 3 | API Endpoint Design, Data Flow |
| **Integration Logic** | Doc 3 | Integration Logic section |
| **User Interface** | Doc 4 | Frontend Flow, Results Display |
| **System Architecture** | Doc 4 | System Architecture Overview |
| **Deployment** | Doc 4 | Deployment Architecture |

---

## How to Use These Documents

### For Thesis Writing

1. **Introduction Chapter:**
   - Use Doc 4 (System Architecture Overview) for high-level system description

2. **Literature Review:**
   - Cite SARIMAX methodology from Doc 1
   - Reference ILP formulation from Doc 2

3. **Methodology Chapter:**
   - **Section 3.1 (Forecasting):** Use Doc 1
   - **Section 3.2 (Optimization):** Use Doc 2 (all five methods)
   - **Section 3.3 (Integration):** Use Doc 3

4. **System Design Chapter:**
   - Use Doc 4 for architecture diagrams and technology choices

5. **Implementation Chapter:**
   - Use code examples from all documents
   - Reference offline training from Doc 1
   - Reference API handlers from Doc 3

6. **Results Chapter:**
   - Use method comparison from Doc 2
   - Use performance metrics from Doc 3 (timing breakdown)
   - Use thesis figures from `../thesis_figures/` folder

7. **Discussion Chapter:**
   - Use "Advantages and Limitations" sections from Docs 1 & 2
   - Use "Performance Considerations" from Doc 3

---

## Key Technical Clarifications

### SARIMAX Model Usage

**Important:** The system does NOT train SARIMAX models during API requests. Models are:
1. Trained **offline** (weekly/monthly) using historical sales data
2. Saved to `sarimax_x/model/` directory as pickle files
3. **Loaded** during API requests for forecasting only

**Benefits:**
- Reduces API response time by ~150ms
- Avoids computational overhead during peak traffic
- Allows controlled model updates without disrupting service

**Model Files:**
- Format: `{product_id}_{region}.pkl` (e.g., `SKU-123_ouest.pkl`)
- One model per product-region combination
- Updated via scheduled batch job or manual trigger

### Optimization Method Selection

**Default Method:** Exact ILP (despite endpoint name `/forecasting/genetic`)

**Why ILP?**
- Guaranteed global optimum (provably best solution)
- Fast enough for production (~30ms)
- Handles complex constraints naturally
- Robust commercial solvers (CBC, Gurobi)

**Other Methods:**
- Included for research comparison and benchmarking
- Genetic Algorithm: Good alternative if ILP fails
- Greedy Heuristic: Ultra-fast fallback (< 1ms)

### Performance Metrics (Updated)

With pre-trained SARIMAX models:
- **Total API Response Time:** ~95ms (down from ~245ms)
- **Forecast Time:** ~10ms (down from ~120ms)
- **Optimization Time:** ~31ms (unchanged)
- **Throughput:** ~10 requests/second per instance

---

## Thesis Figures

Professional figures for your thesis are available in:
```
../thesis_figures/
```

See `../THESIS_FIGURES_GUIDE.md` for detailed descriptions and usage recommendations.

**Available Figures:**
1. Cost comparison across scenarios
2. Service level achievement
3. Runtime performance
4. Fitness score heatmap
5. ILP cost savings
6. Cost-service trade-off
7. Multi-criteria radar chart
8. Scenario difficulty analysis
9. Performance summary table

All figures available in PNG (300 DPI) and PDF (vector) formats.

---

## Additional Resources

### Code Files Referenced

| Document | Referenced File | Purpose |
|----------|----------------|---------|
| Doc 1 | `forecasting/sarimax_model.py` | SARIMAX forecasting service |
| Doc 1 | `forecasting/train_sarimax_models.py` | Offline training script |
| Doc 2 | `optimization/Genitic.py` | All optimization methods |
| Doc 2 | `optimization/compare_methods.py` | Method comparison CLI |
| Doc 3 | `api/routes/forecasting.py` | API endpoints |
| Doc 4 | Various | Full stack implementation |

### Test Data

Example test scenarios documented in:
- `../test_scenarios.md`
- `../USAGE_CASES.md`
- `../EDGE_CASES_AND_RESULTS.md`

### Warehouse Configurations

Test configurations:
- `../reduced_14_warehouses.json` (standard)
- `../edge_case_14_warehouses.json` (unbalanced)
- `../extreme_test_warehouses.json` (missing region)

---

## Document Statistics

| Document | Pages | Word Count | Key Algorithms | Code Examples |
|----------|-------|------------|----------------|---------------|
| Doc 1    | ~40   | ~15,000    | SARIMAX        | 10+           |
| Doc 2    | ~60   | ~25,000    | 5 methods      | 15+           |
| Doc 3    | ~50   | ~18,000    | Integration    | 12+           |
| Doc 4    | ~55   | ~20,000    | Full stack     | 20+           |
| **Total**| **205**| **~78,000**| **7 total**   | **57+**       |

---

## Citing These Documents

**Internal Citation Format:**
```
[Platform Documentation] "Document Title", Section X.Y, 
E-commerce Warehouse Optimization Platform Technical Documentation, 
May 2026
```

**Example:**
```
The fitness function combines service level and cost with equal weighting 
(α = 0.5) to balance customer satisfaction against operational expenses 
[Platform Documentation, "Optimization Methods Technical", Section 1.1, May 2026].
```

---

## Updates and Maintenance

**Last Updated:** May 21, 2026

**Key Updates in This Version:**
- Clarified that SARIMAX models are pre-trained (not trained during API requests)
- Updated timing breakdowns to reflect pre-trained model performance
- Added offline training procedures
- Specified model storage location (`sarimax_x/model/`)
- Updated API integration examples

**Model Storage:**
- **Location:** `sarimax_x/model/`
- **Format:** Python pickle (`.pkl` files)
- **Naming:** `{product_id}_{region}.pkl`

**Version Control:**
- All documents are version 1.0 (May 21, 2026)
- Future updates will be noted in this section

---

## Questions or Clarifications?

If any section needs clarification or expansion:

1. **Forecasting Questions:** See Document 1
2. **Optimization Questions:** See Document 2
3. **API/Integration Questions:** See Document 3
4. **System Design Questions:** See Document 4

All documents are comprehensive and include:
- Theoretical foundations
- Mathematical formulations
- Implementation details
- Code examples
- Usage guidelines
- Performance metrics

---

## Summary

This documentation provides everything needed for your master's thesis:

✓ **Complete mathematical explanations** (SARIMAX, ILP, Genetic Algorithm)  
✓ **Implementation details** (pre-trained models, API design, database schema)  
✓ **Performance analysis** (timing breakdowns, method comparisons)  
✓ **Professional figures** (9 publication-ready visualizations)  
✓ **Code examples** (57+ complete, runnable examples)  
✓ **System architecture** (full-stack design from frontend to database)  

**Total Documentation:** 205 pages, ~78,000 words

**Ready for:** Literature review, methodology, implementation, results, and discussion chapters

---

**Document Version:** 1.0  
**Last Updated:** May 21, 2026  
**For:** Master's Thesis - E-commerce Warehouse Optimization for Algeria  
**Status:** Complete and ready for thesis use
