# API Integration: SARIMAX Forecasting + Exact ILP Optimization

## Overview

This document explains how the SARIMAX forecasting module and Exact ILP optimization method integrate within the API to provide end-to-end warehouse allocation recommendations. The system follows a **two-stage pipeline**: first forecasting regional demand, then optimizing stock allocation to minimize costs while meeting that demand.

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [API Endpoint Design](#api-endpoint-design)
3. [Data Flow](#data-flow)
4. [Forecasting Stage (SARIMAX)](#forecasting-stage-sarimax)
5. [Optimization Stage (Exact ILP)](#optimization-stage-exact-ilp)
6. [Integration Logic](#integration-logic)
7. [Error Handling](#error-handling)
8. [Performance Considerations](#performance-considerations)
9. [Example Request/Response](#example-request-response)
10. [Alternative Configurations](#alternative-configurations)

---

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      CLIENT APPLICATION                         │
│  (Web Dashboard, Mobile App, or External System)                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP POST
                             │ /api/forecasting/genetic
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API GATEWAY                              │
│  (Flask/Django/FastAPI)                                         │
└─────────────────┬──────────────────────────┬────────────────────┘
                  │                          │
        ┌─────────▼────────┐       ┌────────▼──────────┐
        │  FORECASTING     │       │  OPTIMIZATION     │
        │  SERVICE         │       │  SERVICE          │
        │  (SARIMAX)       │       │  (Exact ILP)      │
        └─────────┬────────┘       └────────┬──────────┘
                  │                          │
                  │ demand_by_region         │ allocation
                  │                          │
        ┌─────────▼──────────────────────────▼──────────┐
        │            DATABASE LAYER                     │
        │  - Historical Sales Data                      │
        │  - Warehouse Configuration                    │
        │  - Product Catalog                            │
        │  - Optimization Results (cached)              │
        └───────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Technology |
|-----------|----------------|------------|
| **Client** | User interface, API requests | React, Vue, Mobile App |
| **API Gateway** | Route requests, authentication, validation | Flask, FastAPI, Django |
| **Forecasting Service** | Generate demand forecasts using SARIMAX | Python (statsmodels) |
| **Optimization Service** | Compute optimal allocation using Exact ILP | Python (PuLP + CBC) |
| **Database** | Store historical data, configs, results | PostgreSQL, MongoDB |

---

## API Endpoint Design

### Primary Endpoint

**Endpoint:** `POST /api/forecasting/genetic`

**Note:** Despite the name "genetic" (for backward compatibility), this endpoint now uses **Exact ILP** optimization, which provides guaranteed optimal solutions.

**Purpose:** Forecast regional demand and optimize warehouse stock allocation in a single request.

### Request Specification

```json
{
  "product_id": "SKU-12345",
  "forecast_periods": 4,
  "total_quantity": 5000,
  "use_cached_forecast": false,
  "optimization_method": "ilp",
  "alpha": 0.5
}
```

**Parameters:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `product_id` | string | Yes | - | Unique product identifier |
| `forecast_periods` | integer | No | 4 | Number of periods to forecast (weeks/months) |
| `total_quantity` | integer | No | Auto | Inventory budget to allocate. If omitted, uses current_stock + forecasted_demand |
| `use_cached_forecast` | boolean | No | false | Use previously cached forecast (faster) |
| `optimization_method` | string | No | "ilp" | Optimization method: "ilp", "genetic", "greedy", "random" |
| `alpha` | float | No | 0.5 | Fitness function weight (0-1): service vs cost trade-off |

### Response Specification

```json
{
  "success": true,
  "product_id": "SKU-12345",
  "forecast": {
    "demand_by_region": {
      "ouest": 850,
      "est": 900,
      "north": 1400,
      "sud": 200
    },
    "total_forecast": 3350,
    "forecast_periods": 4,
    "forecast_timestamp": "2026-05-21T18:30:00Z"
  },
  "optimization": {
    "method": "Exact ILP",
    "stock_by_warehouse": {
      "WH-01": 1200,
      "WH-02": 850,
      "WH-03": 1500,
      "WH-04": 300,
      "WH-05": 0,
      "WH-06": 800,
      "WH-07": 650,
      "WH-08": 0,
      "WH-09": 500,
      "WH-10": 0,
      "WH-11": 0,
      "WH-12": 200,
      "WH-13": 0,
      "WH-14": 0
    },
    "total_cost": 10403500,
    "cost_breakdown": {
      "holding_cost": 9845000,
      "transfer_cost": 558500
    },
    "service_level": 100,
    "fitness": 0.4695,
    "runtime_seconds": 0.031,
    "solver_status": "Optimal"
  },
  "recommendations": [
    {
      "warehouse_id": "WH-03",
      "action": "Increase stock",
      "quantity_change": +700,
      "reason": "High-demand north region, low holding cost"
    },
    {
      "warehouse_id": "WH-05",
      "action": "Decrease stock",
      "quantity_change": -500,
      "reason": "High holding cost, low regional demand"
    }
  ],
  "metadata": {
    "request_id": "req-7f3a9b2c",
    "processing_time_ms": 245,
    "api_version": "2.1"
  }
}
```

---

## Data Flow

### Step-by-Step Flow

```
1. Client Request
   ↓
2. API Gateway
   ├─ Authentication
   ├─ Input Validation
   └─ Route to Handler
   ↓
3. Load Historical Data
   ├─ Fetch sales history for product_id
   ├─ Fetch warehouse configuration
   └─ Fetch current stock levels
   ↓
4. SARIMAX Forecasting
   ├─ Train model (or load cached)
   ├─ Generate demand forecast by region
   └─ Return: demand_by_region = {region: quantity}
   ↓
5. Prepare Optimization Inputs
   ├─ demand_by_region (from step 4)
   ├─ total_quantity (from request or computed)
   ├─ warehouses (from database)
   └─ Construct product dict
   ↓
6. Exact ILP Optimization
   ├─ Formulate ILP model
   ├─ Solve using PuLP + CBC
   ├─ Extract solution
   └─ Return: stock_by_warehouse, cost, service_level, fitness
   ↓
7. Post-Processing
   ├─ Generate recommendations
   ├─ Compute additional metrics
   └─ Cache results
   ↓
8. Construct Response
   ↓
9. Return to Client
```

### Timing Breakdown (Typical)

**Note:** SARIMAX models are pre-trained and stored in `sarimax_x/model/` directory. The system loads these models instead of training during requests.

| Stage | Typical Time | Percentage |
|-------|--------------|------------|
| Request validation | 2 ms | 2% |
| Database queries | 50 ms | 53% |
| Load SARIMAX model | 5 ms | 5% |
| Generate forecast | 5 ms | 5% |
| ILP optimization | 31 ms | 33% |
| Post-processing | 2 ms | 2% |
| Response formatting | 0 ms | 0% |
| **Total** | **~95 ms** | **100%** |

**Performance Note:** By using pre-trained models instead of training on each request, we reduced total response time from ~245ms to ~95ms (61% improvement).

---

## Forecasting Stage (SARIMAX)

### Implementation

**Important:** SARIMAX models are **pre-trained offline** and stored in `sarimax_x/model/` directory. The API only loads and uses these models for forecasting—no training occurs during API requests.

**File:** `forecasting/sarimax_service.py`

```python
import pickle
import os
from pathlib import Path

class SARIMAXForecaster:
    """
    SARIMAX-based demand forecasting service using pre-trained models
    """
    
    def __init__(self, model_dir='sarimax_x/model'):
        """
        Initialize forecaster with path to pre-trained models
        
        Parameters
        ----------
        model_dir : str
            Path to directory containing pre-trained model files
        """
        self.model_dir = Path(model_dir)
        self.models = {}  # In-memory cache of loaded models
        
        if not self.model_dir.exists():
            raise FileNotFoundError(f"Model directory not found: {self.model_dir}")
    
    def load_model(self, product_id, region):
        """
        Load a pre-trained SARIMAX model from disk
        
        Parameters
        ----------
        product_id : str
            Product identifier
        region : str
            Region name (ouest, est, north, sud)
        
        Returns
        -------
        model_fit : SARIMAXResults
            Pre-trained fitted model ready for forecasting
        """
        model_key = f"{product_id}_{region}"
        
        # Check in-memory cache first (for performance)
        if model_key in self.models:
            return self.models[model_key]
        
        # Load from disk
        model_path = self.model_dir / f"{model_key}.pkl"
        
        if not model_path.exists():
            raise FileNotFoundError(
                f"No trained model found for {product_id} in region {region}. "
                f"Expected file: {model_path}"
            )
        
        # Load pickled model
        with open(model_path, 'rb') as f:
            model_fit = pickle.load(f)
        
        # Cache in memory for subsequent requests
        self.models[model_key] = model_fit
        
        return model_fit
    
    def forecast(self, product_id, regions, forecast_periods=4):
        """
        Generate demand forecast using pre-trained models
        
        Parameters
        ----------
        product_id : str
            Product identifier
        regions : list
            List of region names to forecast
        forecast_periods : int
            Number of periods to forecast (e.g., 4 weeks)
        
        Returns
        -------
        dict
            {region: total_forecasted_demand}
        """
        demand_by_region = {}
        
        for region in regions:
            try:
                # Load pre-trained model (from cache or disk)
                model_fit = self.load_model(product_id, region)
                
                # Generate forecast (FAST - no training!)
                forecast = model_fit.forecast(steps=forecast_periods)
                
                # Sum over forecast periods to get total demand
                total_demand = int(forecast.sum())
                demand_by_region[region] = max(0, total_demand)  # Ensure non-negative
                
            except FileNotFoundError as e:
                # Model not found for this product-region combination
                print(f"Warning: {e}")
                # Fallback: use zero demand or simple heuristic
                demand_by_region[region] = 0
        
        return demand_by_region
    
    def preload_models(self, product_id):
        """
        Preload all regional models for a product into memory
        Useful for warming up the cache at startup
        
        Parameters
        ----------
        product_id : str
            Product identifier
        """
        regions = ['ouest', 'est', 'north', 'sud']
        
        for region in regions:
            try:
                self.load_model(product_id, region)
            except FileNotFoundError:
                pass  # Skip if model doesn't exist
```

### Integration in API

```python
from forecasting.sarimax_service import SARIMAXForecaster

# Global forecaster instance pointing to pre-trained models directory
forecaster = SARIMAXForecaster(model_dir='sarimax_x/model')

@app.route('/api/forecasting/genetic', methods=['POST'])
def forecast_and_optimize():
    data = request.json
    
    # Define regions
    regions = ['ouest', 'est', 'north', 'sud']
    
    # Generate forecast using PRE-TRAINED models
    # No historical sales needed - models are already trained!
    demand_by_region = forecaster.forecast(
        product_id=data['product_id'],
        regions=regions,
        forecast_periods=data.get('forecast_periods', 4)
    )
    
    # Continue to optimization stage...
```

### Forecast Quality Metrics

After forecasting, compute quality metrics (optional):

```python
def evaluate_forecast_quality(model_fit, test_data):
    """
    Evaluate forecast accuracy using holdout data
    
    Metrics:
    - RMSE (Root Mean Squared Error)
    - MAPE (Mean Absolute Percentage Error)
    - Coverage (% of actuals within 95% CI)
    """
    forecast = model_fit.forecast(steps=len(test_data))
    
    # RMSE
    rmse = np.sqrt(np.mean((forecast - test_data)**2))
    
    # MAPE
    mape = np.mean(np.abs((test_data - forecast) / test_data)) * 100
    
    # Coverage
    forecast_obj = model_fit.get_forecast(steps=len(test_data))
    ci = forecast_obj.conf_int()
    coverage = np.mean((test_data >= ci.iloc[:, 0]) & (test_data <= ci.iloc[:, 1])) * 100
    
    return {
        'rmse': rmse,
        'mape': mape,
        'coverage': coverage
    }
```

Include in response (optional):
```json
"forecast_quality": {
  "rmse": 45.2,
  "mape": 8.3,
  "coverage": 94.2
}
```

---

## Optimization Stage (Exact ILP)

### Implementation

**File:** `optimization/ilp_service.py`

```python
from optimization.Genitic import run_exact_ilp_solver

class OptimizationService:
    """
    Wrapper for optimization methods
    """
    
    def __init__(self, default_method='ilp'):
        self.default_method = default_method
    
    def optimize(self, product, demand_by_region, warehouses, method=None, alpha=0.5):
        """
        Run optimization using specified method
        
        Parameters
        ----------
        product : dict
            {'product_id': str, 'total_quantity': int}
        demand_by_region : dict
            {region: forecasted_demand}
        warehouses : dict
            {warehouse_id: {capacity, stock_level, region, costs, ...}}
        method : str, optional
            'ilp', 'genetic', 'greedy', 'random'
        alpha : float
            Fitness function weight (0-1)
        
        Returns
        -------
        dict
            Optimization result with stock allocation and metrics
        """
        method = method or self.default_method
        
        if method == 'ilp':
            result = run_exact_ilp_solver(
                product=product,
                demand_by_region=demand_by_region,
                warehouses=warehouses
            )
        elif method == 'genetic':
            from optimization.Genitic import run_genetic_optimization
            result = run_genetic_optimization(
                product=product,
                demand_by_region=demand_by_region,
                warehouses=warehouses,
                pop_size=100,
                generations=50
            )
        elif method == 'greedy':
            from optimization.Genitic import run_greedy_heuristic
            result = run_greedy_heuristic(
                product=product,
                demand_by_region=demand_by_region,
                warehouses=warehouses
            )
        elif method == 'random':
            from optimization.Genitic import run_random_search_optimization
            result = run_random_search_optimization(
                product=product,
                demand_by_region=demand_by_region,
                warehouses=warehouses,
                num_iterations=500
            )
        else:
            raise ValueError(f"Unknown optimization method: {method}")
        
        return result
```

### Integration in API

```python
from optimization.ilp_service import OptimizationService

# Global optimizer instance
optimizer = OptimizationService(default_method='ilp')

@app.route('/api/forecasting/genetic', methods=['POST'])
def forecast_and_optimize():
    data = request.json
    
    # ... (forecasting stage from above)
    
    # Load warehouse data
    warehouses = db.get_warehouses()
    # Example: {'WH-01': {'capacity': 2000, 'stock_level': 500, ...}, ...}
    
    # Prepare product dict
    product = {
        'product_id': data['product_id'],
        'total_quantity': data.get('total_quantity') or (
            sum(wh['stock_level'] for wh in warehouses.values()) +
            sum(demand_by_region.values())
        )
    }
    
    # Run optimization
    result = optimizer.optimize(
        product=product,
        demand_by_region=demand_by_region,
        warehouses=warehouses,
        method=data.get('optimization_method', 'ilp'),
        alpha=data.get('alpha', 0.5)
    )
    
    # Continue to response construction...
```

---

## Integration Logic

### Complete API Handler

**File:** `api/routes/forecasting.py`

```python
from flask import Flask, request, jsonify
import time
from forecasting.sarimax_service import SARIMAXForecaster
from optimization.ilp_service import OptimizationService
from database.db_service import DatabaseService

app = Flask(__name__)

# Initialize services
# IMPORTANT: SARIMAX models are pre-trained and stored in sarimax_x/model/
# The forecaster only LOADS these models, no training occurs during API requests
forecaster = SARIMAXForecaster(model_dir='sarimax_x/model')
optimizer = OptimizationService(default_method='ilp')
db = DatabaseService()

@app.route('/api/forecasting/genetic', methods=['POST'])
def forecast_and_optimize():
    """
    Combined endpoint: SARIMAX forecasting + Exact ILP optimization
    
    Despite the endpoint name 'genetic', this now uses Exact ILP by default
    for guaranteed optimal solutions. The name is kept for backward compatibility.
    """
    start_time = time.time()
    
    try:
        # ===================================================================
        # STEP 1: INPUT VALIDATION
        # ===================================================================
        data = request.json
        
        if not data.get('product_id'):
            return jsonify({
                'success': False,
                'error': 'Missing required field: product_id'
            }), 400
        
        product_id = data['product_id']
        forecast_periods = data.get('forecast_periods', 4)
        use_cached = data.get('use_cached_forecast', False)
        optimization_method = data.get('optimization_method', 'ilp')
        alpha = data.get('alpha', 0.5)
        
        # Validate alpha
        if not 0 <= alpha <= 1:
            return jsonify({
                'success': False,
                'error': 'alpha must be between 0 and 1'
            }), 400
        
        # ===================================================================
        # STEP 2: LOAD DATA
        # ===================================================================
        # Check if product exists
        product_info = db.get_product(product_id)
        if not product_info:
            return jsonify({
                'success': False,
                'error': f'Product not found: {product_id}'
            }), 404
        
        # Load warehouse configuration
        warehouses = db.get_warehouses()
        if not warehouses:
            return jsonify({
                'success': False,
                'error': 'No warehouses configured in system'
            }), 500
        
        # ===================================================================
        # STEP 3: SARIMAX FORECASTING (Using Pre-trained Models)
        # ===================================================================
        forecast_start = time.time()
        
        regions = ['ouest', 'est', 'north', 'sud']
        
        if use_cached:
            # Try to use cached forecast
            cached_forecast = db.get_cached_forecast(product_id)
            if cached_forecast:
                demand_by_region = cached_forecast['demand_by_region']
                forecast_timestamp = cached_forecast['timestamp']
            else:
                # No cache available, generate new forecast from pre-trained model
                demand_by_region = forecaster.forecast(
                    product_id=product_id,
                    regions=regions,
                    forecast_periods=forecast_periods
                )
                forecast_timestamp = pd.Timestamp.now().isoformat()
                
                # Cache the forecast
                db.save_forecast_cache(product_id, demand_by_region, forecast_timestamp)
        else:
            # Generate new forecast from pre-trained model
            # Note: No training happens here - model is loaded from sarimax_x/model/
            demand_by_region = forecaster.forecast(
                product_id=product_id,
                regions=regions,
                forecast_periods=forecast_periods
            )
            forecast_timestamp = pd.Timestamp.now().isoformat()
            
            # Cache the forecast
            db.save_forecast_cache(product_id, demand_by_region, forecast_timestamp)
        
        forecast_time = time.time() - forecast_start
        
        # ===================================================================
        # STEP 4: PREPARE OPTIMIZATION INPUTS
        # ===================================================================
        total_forecast = sum(demand_by_region.values())
        current_stock = sum(wh.get('stock_level', 0) for wh in warehouses.values())
        
        # Determine total_quantity
        if 'total_quantity' in data:
            total_quantity = data['total_quantity']
        else:
            # Default: current stock + forecasted demand
            total_quantity = current_stock + total_forecast
        
        product_dict = {
            'product_id': product_id,
            'total_quantity': total_quantity
        }
        
        # ===================================================================
        # STEP 5: EXACT ILP OPTIMIZATION
        # ===================================================================
        opt_start = time.time()
        
        optimization_result = optimizer.optimize(
            product=product_dict,
            demand_by_region=demand_by_region,
            warehouses=warehouses,
            method=optimization_method,
            alpha=alpha
        )
        
        opt_time = time.time() - opt_start
        
        # ===================================================================
        # STEP 6: POST-PROCESSING
        # ===================================================================
        post_start = time.time()
        
        # Generate recommendations (compare current vs. optimized)
        recommendations = []
        for wh_id, optimized_qty in optimization_result['stock_by_warehouse'].items():
            current_qty = warehouses[wh_id].get('stock_level', 0)
            change = optimized_qty - current_qty
            
            if abs(change) > 10:  # Only significant changes
                action = "Increase stock" if change > 0 else "Decrease stock"
                
                # Determine reason
                wh_region = warehouses[wh_id]['region']
                regional_demand = demand_by_region.get(wh_region, 0)
                holding_cost = warehouses[wh_id].get('holdingCost', 0)
                
                if change > 0 and regional_demand > 500:
                    reason = f"High-demand {wh_region} region"
                elif change > 0 and holding_cost < 1200:
                    reason = "Low holding cost warehouse"
                elif change < 0 and holding_cost > 1500:
                    reason = "High holding cost, better alternatives available"
                elif change < 0 and regional_demand < 300:
                    reason = "Low regional demand"
                else:
                    reason = "Cost optimization"
                
                recommendations.append({
                    'warehouse_id': wh_id,
                    'action': action,
                    'quantity_change': change,
                    'reason': reason
                })
        
        # Sort recommendations by absolute change (most significant first)
        recommendations.sort(key=lambda r: abs(r['quantity_change']), reverse=True)
        
        # Compute cost breakdown
        cost_breakdown = {
            'holding_cost': sum(
                optimization_result['stock_by_warehouse'][wh_id] * warehouses[wh_id].get('holdingCost', 0)
                for wh_id in warehouses.keys()
            ),
            'transfer_cost': sum(
                abs(optimization_result['stock_by_warehouse'][wh_id] - warehouses[wh_id].get('stock_level', 0))
                * warehouses[wh_id].get('transportCost', 0)
                for wh_id in warehouses.keys()
            )
        }
        
        post_time = time.time() - post_start
        
        # ===================================================================
        # STEP 7: SAVE RESULTS TO DATABASE
        # ===================================================================
        db.save_optimization_result(
            product_id=product_id,
            demand_forecast=demand_by_region,
            optimization_result=optimization_result,
            recommendations=recommendations,
            metadata={
                'optimization_method': optimization_method,
                'forecast_periods': forecast_periods,
                'alpha': alpha,
                'total_quantity': total_quantity
            }
        )
        
        # ===================================================================
        # STEP 8: CONSTRUCT RESPONSE
        # ===================================================================
        total_time = time.time() - start_time
        
        response = {
            'success': True,
            'product_id': product_id,
            'forecast': {
                'demand_by_region': demand_by_region,
                'total_forecast': total_forecast,
                'forecast_periods': forecast_periods,
                'forecast_timestamp': forecast_timestamp
            },
            'optimization': {
                'method': optimization_result['method'],
                'stock_by_warehouse': optimization_result['stock_by_warehouse'],
                'total_cost': optimization_result['cost'],
                'cost_breakdown': cost_breakdown,
                'service_level': optimization_result['service_level'],
                'fitness': optimization_result['fitness'],
                'runtime_seconds': optimization_result['runtime'],
                'solver_status': optimization_result.get('solver_status', 'N/A')
            },
            'recommendations': recommendations[:10],  # Top 10
            'metadata': {
                'request_id': f"req-{int(time.time()*1000)}",
                'processing_time_ms': int(total_time * 1000),
                'timing_breakdown': {
                    'forecast_ms': int(forecast_time * 1000),
                    'optimization_ms': int(opt_time * 1000),
                    'post_processing_ms': int(post_time * 1000)
                },
                'api_version': '2.1'
            }
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        # Log error (use proper logging in production)
        print(f"Error in forecast_and_optimize: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'details': str(e) if app.debug else 'Contact administrator'
        }), 500
```

---

## Error Handling

### Common Error Scenarios

#### 1. Insufficient Historical Data

**Problem:** SARIMAX requires minimum data for training.

**Detection:**
```python
if len(sales_history.get(region, [])) < 50:
    raise ValueError(f"Insufficient data for {region}: need 50+ observations")
```

**Fallback:**
```python
# Use simple moving average
demand = int(pd.Series(sales).tail(12).mean() * forecast_periods)
```

**Response:**
```json
{
  "success": false,
  "error": "Insufficient historical data",
  "details": "Region 'ouest' has only 30 observations, minimum 50 required"
}
```

#### 2. ILP Solver Failure

**Problem:** ILP solver cannot find solution (infeasible problem).

**Detection:**
```python
if model.status != pulp.LpStatusOptimal:
    raise OptimizationError(f"Solver failed: {pulp.LpStatus[model.status]}")
```

**Fallback:**
```python
# Use Greedy Heuristic as backup
result = run_greedy_heuristic(product, demand_by_region, warehouses)
result['method'] = 'Greedy Heuristic (ILP fallback)'
```

**Response:**
```json
{
  "success": true,
  "optimization": {
    "method": "Greedy Heuristic (ILP fallback)",
    "warning": "ILP solver could not find optimal solution, using heuristic"
  }
}
```

#### 3. Total Quantity Exceeds Capacity

**Problem:** Requested quantity > sum of all warehouse capacities.

**Detection:**
```python
total_capacity = sum(wh['capacity'] for wh in warehouses.values())
if total_quantity > total_capacity:
    raise ValueError(f"Total quantity ({total_quantity}) exceeds total capacity ({total_capacity})")
```

**Automatic Adjustment:**
```python
# Clamp to maximum capacity
total_quantity = min(total_quantity, total_capacity)
warnings.append(f"Total quantity reduced to maximum capacity: {total_capacity}")
```

#### 4. Database Connection Issues

**Problem:** Cannot fetch data from database.

**Handling:**
```python
try:
    sales_history = db.get_sales_history(product_id)
except DatabaseError as e:
    return jsonify({
        'success': False,
        'error': 'Database connection failed',
        'retry_after': 5
    }), 503
```

---

## Performance Considerations

### Caching Strategy

#### 1. Cached SARIMAX Models

**Benefit:** Avoid retraining on every request (saves ~100 ms).

**Implementation:**
```python
# On startup, load all models from disk
forecaster.load_cached_models()

# During request, check cache first
if model_key in self.models:
    model_fit = self.models[model_key]
else:
    # Train and cache
    model_fit = self._train_model(data)
    self.models[model_key] = model_fit
    self._save_model_to_disk(model_key, model_fit)
```

**Invalidation:** Re-train weekly or when new data arrives.

#### 2. Cached Forecasts

**Benefit:** Reuse recent forecasts (saves ~120 ms).

**Implementation:**
```python
if use_cached_forecast:
    cached = db.get_cached_forecast(product_id)
    if cached and (now - cached['timestamp']) < timedelta(hours=24):
        return cached['demand_by_region']
```

**Invalidation:** Expire after 24 hours or on-demand refresh.

#### 3. Cached Warehouse Configuration

**Benefit:** Avoid database query on every request.

**Implementation:**
```python
# In-memory cache with TTL
@lru_cache(maxsize=1)
def get_warehouses_cached():
    return db.get_warehouses()

# Invalidate when warehouse config changes
def on_warehouse_update():
    get_warehouses_cached.cache_clear()
```

### Asynchronous Processing

For batch optimization (multiple products):

```python
import asyncio

async def forecast_and_optimize_batch(product_ids):
    tasks = [
        asyncio.create_task(forecast_and_optimize_async(pid))
        for pid in product_ids
    ]
    return await asyncio.gather(*tasks)
```

**Benefit:** Process 10 products in ~300 ms (vs. 2500 ms sequential).

### Database Query Optimization

```sql
-- Bad: N+1 query problem
for wh_id in warehouse_ids:
    warehouse = SELECT * FROM warehouses WHERE id = wh_id

-- Good: Single query
warehouses = SELECT * FROM warehouses WHERE id IN (warehouse_ids)
```

**Benefit:** Reduces database latency from ~50 ms × N to ~50 ms.

---

## Example Request/Response

### Example 1: Standard Request

**Request:**
```bash
curl -X POST http://api.example.com/api/forecasting/genetic \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "product_id": "SKU-78901",
    "forecast_periods": 4,
    "total_quantity": 5000,
    "optimization_method": "ilp",
    "alpha": 0.5
  }'
```

**Response:**
```json
{
  "success": true,
  "product_id": "SKU-78901",
  "forecast": {
    "demand_by_region": {
      "ouest": 850,
      "est": 900,
      "north": 1400,
      "sud": 200
    },
    "total_forecast": 3350,
    "forecast_periods": 4,
    "forecast_timestamp": "2026-05-21T18:45:30Z"
  },
  "optimization": {
    "method": "Exact ILP",
    "stock_by_warehouse": {
      "WH-01": 1200,
      "WH-02": 850,
      "WH-03": 1500,
      "WH-04": 300,
      "WH-05": 0,
      "WH-06": 800,
      "WH-07": 650,
      "WH-08": 0,
      "WH-09": 500,
      "WH-10": 0,
      "WH-11": 0,
      "WH-12": 200,
      "WH-13": 0,
      "WH-14": 0
    },
    "total_cost": 10403500,
    "cost_breakdown": {
      "holding_cost": 9845000,
      "transfer_cost": 558500
    },
    "service_level": 100,
    "fitness": 0.4695,
    "runtime_seconds": 0.031,
    "solver_status": "Optimal"
  },
  "recommendations": [
    {
      "warehouse_id": "WH-03",
      "action": "Increase stock",
      "quantity_change": 700,
      "reason": "High-demand north region"
    },
    {
      "warehouse_id": "WH-05",
      "action": "Decrease stock",
      "quantity_change": -500,
      "reason": "High holding cost, better alternatives available"
    }
  ],
  "metadata": {
    "request_id": "req-1716313530245",
    "processing_time_ms": 245,
    "timing_breakdown": {
      "forecast_ms": 120,
      "optimization_ms": 31,
      "post_processing_ms": 32
    },
    "api_version": "2.1"
  }
}
```

### Example 2: Cached Forecast

**Request:**
```json
{
  "product_id": "SKU-78901",
  "use_cached_forecast": true,
  "total_quantity": 6000
}
```

**Response:** (Similar to above, but faster)
```json
{
  "metadata": {
    "processing_time_ms": 95,
    "timing_breakdown": {
      "forecast_ms": 5,
      "optimization_ms": 33,
      "post_processing_ms": 30
    }
  }
}
```

---

## Alternative Configurations

### Configuration 1: Cost-Focused (α = 0.3)

**Use Case:** Budget-constrained business, willing to sacrifice some service level.

```json
{
  "product_id": "SKU-78901",
  "alpha": 0.3
}
```

**Expected Result:**
- Lower total cost
- Potentially lower service level (e.g., 85% instead of 100%)
- Stock concentrated in cheapest warehouses

### Configuration 2: Service-Focused (α = 0.7)

**Use Case:** Premium e-commerce, prioritize customer satisfaction.

```json
{
  "product_id": "SKU-78901",
  "alpha": 0.7
}
```

**Expected Result:**
- Higher total cost
- Maximum service level (100%)
- Stock distributed closer to demand centers

### Configuration 3: Compare Multiple Methods

**Request:**
```json
{
  "product_id": "SKU-78901",
  "compare_methods": ["ilp", "genetic", "greedy"]
}
```

**Response:**
```json
{
  "comparison": {
    "ilp": {
      "cost": 10403500,
      "service_level": 100,
      "fitness": 0.4695,
      "runtime_seconds": 0.031
    },
    "genetic": {
      "cost": 10685990,
      "service_level": 100,
      "fitness": 0.4670,
      "runtime_seconds": 0.306
    },
    "greedy": {
      "cost": 10685990,
      "service_level": 100,
      "fitness": 0.4670,
      "runtime_seconds": 0.001
    }
  },
  "recommendation": "ilp",
  "reason": "Best fitness with acceptable runtime"
}
```

---

## Summary

### Key Integration Points

1. **SARIMAX → ILP:** Forecasted demand becomes the input constraint for optimization
2. **Warehouse Data → ILP:** Capacities, costs, and regions define the solution space
3. **Total Quantity → ILP:** Budget constraint that must be satisfied exactly
4. **ILP Output → Recommendations:** Optimized allocation translated into actionable warehouse adjustments

### Why Exact ILP?

The endpoint uses **Exact ILP** as the default optimization method (despite the legacy name `/forecasting/genetic`) because:

1. **Guaranteed Optimality:** ILP finds the provably best solution
2. **Fast Enough:** 30-50 ms runtime is acceptable for planning applications
3. **Handles Constraints:** Naturally incorporates capacity, demand, and cost constraints
4. **Production-Ready:** Robust solvers (CBC) with decades of optimization research

### Typical Usage Pattern

```python
# 1. Client requests forecast + optimization
client.post('/api/forecasting/genetic', data={
    'product_id': 'SKU-123',
    'forecast_periods': 4
})

# 2. API forecasts demand using SARIMAX
demand = sarimax_forecast(sales_history)
# → {'ouest': 850, 'est': 900, 'north': 1400, 'sud': 200}

# 3. API optimizes allocation using Exact ILP
allocation = ilp_optimize(demand, warehouses, quantity=5000)
# → {'WH-01': 1200, 'WH-02': 850, ..., cost: 10403500, service: 100%}

# 4. Client receives combined result
{
    'forecast': demand,
    'optimization': allocation,
    'recommendations': [actions]
}

# 5. Client displays results and allows user to accept/modify
# 6. User confirms → API updates warehouse stock levels in database
```

---

**Document Version:** 1.0  
**Last Updated:** May 21, 2026  
**For:** Master's Thesis - Warehouse Optimization Platform
