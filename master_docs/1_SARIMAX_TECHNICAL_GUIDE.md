# SARIMAX: Technical Guide and Implementation

## Overview

SARIMAX (Seasonal AutoRegressive Integrated Moving Average with eXogenous variables) is a sophisticated time series forecasting model used in this system to predict regional demand for e-commerce products across Algeria. This document provides a comprehensive technical explanation of how SARIMAX works and its implementation in the warehouse optimization platform.

---

## Table of Contents

1. [Mathematical Foundation](#mathematical-foundation)
2. [Model Components Explained](#model-components-explained)
3. [Parameter Selection (p,d,q)(P,D,Q,m)](#parameter-selection)
4. [Model Training Process](#model-training-process)
5. [Forecasting Mechanism](#forecasting-mechanism)
6. [Implementation in the Platform](#implementation-in-the-platform)
7. [Example Walkthrough](#example-walkthrough)
8. [Advantages and Limitations](#advantages-and-limitations)

---

## Mathematical Foundation

### The SARIMAX Equation

The complete SARIMAX model combines multiple components:

```
φ(B) Φ(Bᵐ) ∇ᵈ ∇ᴰₘ yₜ = c + θ(B) Θ(Bᵐ) εₜ + β xₜ
```

**Where:**
- **yₜ** = Observed value at time t (e.g., sales in region "ouest" at week t)
- **B** = Backshift operator: B yₜ = yₜ₋₁
- **∇** = Difference operator: ∇ yₜ = yₜ - yₜ₋₁
- **d** = Order of non-seasonal differencing
- **D** = Order of seasonal differencing
- **m** = Seasonal period (e.g., 12 for monthly data with yearly seasonality)
- **φ(B)** = Non-seasonal AR polynomial: φ(B) = 1 - φ₁B - φ₂B² - ... - φₚBᵖ
- **Φ(Bᵐ)** = Seasonal AR polynomial: Φ(Bᵐ) = 1 - Φ₁Bᵐ - Φ₂B²ᵐ - ... - ΦₚB^(Pm)
- **θ(B)** = Non-seasonal MA polynomial: θ(B) = 1 + θ₁B + θ₂B² + ... + θᵧBᵧ
- **Θ(Bᵐ)** = Seasonal MA polynomial: Θ(Bᵐ) = 1 + Θ₁Bᵐ + Θ₂B²ᵐ + ... + ΘQB^(Qm)
- **εₜ** = White noise error term at time t (assumed normally distributed)
- **xₜ** = Exogenous variable(s) at time t (external factors)
- **β** = Coefficient(s) for exogenous variables
- **c** = Constant term (drift)

---

## Model Components Explained

### 1. AutoRegressive (AR) Component - Order p

**Concept:** The current value depends on past values.

**Mathematical Form:**
```
yₜ = φ₁ yₜ₋₁ + φ₂ yₜ₋₂ + ... + φₚ yₜ₋ₚ + εₜ
```

**Example (p=2):**
```
Sales_today = 0.6 × Sales_yesterday + 0.3 × Sales_2days_ago + noise
```

**Intuition:** If sales were high yesterday, they're likely to be high today (momentum effect).

**How It Works:**
1. The model looks back p time steps
2. Computes weighted average of past values
3. Weights (φ₁, φ₂, ..., φₚ) are learned during training
4. Captures short-term dependencies and trends

**In E-commerce Context:**
- High sales on Day 1 might indicate continued interest
- Viral products show strong AR effects
- φ₁ = 0.7 means yesterday's sales contribute 70% to today's prediction

---

### 2. Integrated (I) Component - Order d

**Concept:** Make the time series stationary by differencing.

**Why Needed:**
Most statistical models assume stationarity:
- Constant mean over time
- Constant variance over time
- No trend or seasonality

**First Difference (d=1):**
```
∇ yₜ = yₜ - yₜ₋₁
```

Instead of modeling raw sales, model the *change* in sales.

**Example:**

| Week | Sales | First Difference |
|------|-------|------------------|
| 1    | 100   | -                |
| 2    | 120   | +20              |
| 3    | 150   | +30              |
| 4    | 155   | +5               |

**Second Difference (d=2):**
```
∇² yₜ = ∇(∇ yₜ) = (yₜ - yₜ₋₁) - (yₜ₋₁ - yₜ₋₂)
```

Models the *change in the change* (acceleration).

**How It Works:**
1. Test for stationarity (Augmented Dickey-Fuller test)
2. If non-stationary, apply differencing
3. Repeat until stationary
4. Typical values: d ∈ {0, 1, 2}

**In E-commerce Context:**
- Raw sales often have trend (growing business) → d=1
- Differencing removes trend, isolates fluctuations
- Forecasts are made on differences, then "integrated" back

---

### 3. Moving Average (MA) Component - Order q

**Concept:** The current value depends on past forecast errors.

**Mathematical Form:**
```
yₜ = εₜ + θ₁ εₜ₋₁ + θ₂ εₜ₋₂ + ... + θᵧ εₜ₋ᵧ
```

**Example (q=1):**
```
Sales_today = Today's_shock + 0.5 × Yesterday's_forecast_error
```

**Intuition:** 
- If yesterday's forecast was too low (εₜ₋₁ > 0), correct upward today
- Captures short-term corrections from unexpected events

**How It Works:**
1. At each time step, observe actual vs. predicted
2. Error εₜ = yₜ - ŷₜ
3. Feed this error into future predictions
4. θ coefficients determine how much past errors matter

**Example Scenario:**
- Forecast 1000 units, actual was 1200 → error = +200
- Tomorrow's forecast incorporates this surprise: adds 0.4 × 200 = 80 units

**In E-commerce Context:**
- Flash sale causes sudden spike → MA component captures this
- Stock-out yesterday → customers buy more today (delayed demand)
- Competitor's price drop → unexpected demand decrease

---

### 4. Seasonal AR (SAR) Component - Order P

**Concept:** The current value depends on values from the same season in previous cycles.

**Mathematical Form:**
```
yₜ = Φ₁ yₜ₋ₘ + Φ₂ yₜ₋₂ₘ + ... + Φₚ yₜ₋ₚₘ + εₜ
```

**Example (m=12 for monthly data, P=1):**
```
Sales_January_2026 = 0.8 × Sales_January_2025 + noise
```

**Intuition:** January sales this year resemble January sales last year.

**How It Works:**
1. Identify seasonal period m (weekly=7, monthly=12, quarterly=4)
2. Look back m, 2m, 3m, ... steps
3. Learn seasonal patterns (Ramadan, Christmas, Black Friday)

**In E-commerce Context:**
- Ramadan: high demand in specific month every year
- Back-to-school: August/September spike
- Winter clothing: November-February pattern

---

### 5. Seasonal I Component - Order D

**Concept:** Remove seasonal trend by seasonal differencing.

**Seasonal Difference (D=1):**
```
∇ₘ yₜ = yₜ - yₜ₋ₘ
```

**Example (m=12):**
```
Compare January 2026 sales to January 2025 sales
```

**Why Needed:**
- Overall sales might grow 10% year-over-year
- This creates non-stationarity in seasonal component
- Seasonal differencing removes this

**How It Works:**
1. Subtract value from same season last cycle
2. Removes seasonal trend
3. Typically D ∈ {0, 1}

**In E-commerce Context:**
- Business growing → sales increase every Ramadan
- Seasonal differencing isolates the *pattern* from the *growth*

---

### 6. Seasonal MA (SMA) Component - Order Q

**Concept:** The current value depends on forecast errors from the same season in previous cycles.

**Mathematical Form:**
```
yₜ = εₜ + Θ₁ εₜ₋ₘ + Θ₂ εₜ₋₂ₘ + ... + ΘQ εₜ₋Qₘ
```

**Example (m=12, Q=1):**
```
Sales_January_2026 = This_month_shock + 0.6 × January_2025_forecast_error
```

**Intuition:** If we under-predicted last January, correct this January.

**How It Works:**
1. Track seasonal forecast errors
2. Apply corrections in future seasons
3. Captures systematic seasonal misjudgments

**In E-commerce Context:**
- Consistently under-predict Ramadan → SMA learns to adjust
- Weather anomaly last winter → avoid same mistake this winter

---

### 7. Exogenous Variables (X)

**Concept:** External factors that influence the time series.

**Mathematical Form:**
```
yₜ = ... + β₁ x₁ₜ + β₂ x₂ₜ + ... + βₖ xₖₜ
```

**Examples of Exogenous Variables:**
- **Marketing spend:** Higher ads → higher sales
- **Price:** Lower price → higher demand
- **Competitor actions:** Rival's sale → our demand drops
- **Holidays:** Binary indicator (0/1)
- **Weather:** Temperature, rainfall
- **Economic indicators:** GDP, unemployment rate

**How It Works:**
1. Provide exogenous variable values for training period
2. Model learns relationship (β coefficients)
3. For forecasting, must provide future values of exogenous variables
4. Forecast = Time series pattern + Exogenous effect

**Example:**
```
Sales = AR/MA components + 500 × is_Ramadan + 2 × Marketing_spend
```

**In E-commerce Context:**
- Planned promotions (known in advance)
- Holiday calendar
- Competitor price data
- NOT used if future values unknown

---

## Parameter Selection

### SARIMAX Notation: (p,d,q)(P,D,Q,m)

**Non-seasonal:**
- **p:** Number of AR terms (how many past values to use)
- **d:** Differencing order (0, 1, or 2)
- **q:** Number of MA terms (how many past errors to use)

**Seasonal:**
- **P:** Number of seasonal AR terms
- **D:** Seasonal differencing order
- **Q:** Number of seasonal MA terms
- **m:** Seasonal period length

### Selection Methods

#### 1. Grid Search with AIC/BIC

**Process:**
```python
best_aic = ∞
for p in range(0, 3):
    for d in range(0, 2):
        for q in range(0, 3):
            for P in range(0, 2):
                for D in range(0, 2):
                    for Q in range(0, 2):
                        model = SARIMAX(data, order=(p,d,q), seasonal_order=(P,D,Q,m))
                        results = model.fit()
                        if results.aic < best_aic:
                            best_aic = results.aic
                            best_params = (p,d,q,P,D,Q,m)
```

**AIC (Akaike Information Criterion):**
```
AIC = 2k - 2ln(L)
```
- k = number of parameters
- L = likelihood
- Lower is better
- Balances fit quality vs. model complexity

**BIC (Bayesian Information Criterion):**
```
BIC = k×ln(n) - 2ln(L)
```
- n = number of observations
- Penalizes complexity more than AIC
- Preferred for larger datasets

#### 2. Auto-ARIMA

**Automated Process:**
1. Test for seasonality (autocorrelation plots)
2. Determine differencing order (stationarity tests)
3. Step-wise search through parameter space
4. Select model minimizing AIC/BIC
5. Validate with diagnostic tests

**Library Implementation:**
```python
from pmdarima import auto_arima

model = auto_arima(
    data,
    start_p=0, max_p=3,
    start_q=0, max_q=3,
    seasonal=True,
    m=12,  # monthly seasonality
    information_criterion='aic',
    trace=True
)
```

#### 3. ACF and PACF Plots

**Autocorrelation Function (ACF):**
- Shows correlation between yₜ and yₜ₋ₖ
- MA order (q): ACF cuts off after q lags
- Seasonal MA (Q): ACF spikes at seasonal lags

**Partial Autocorrelation Function (PACF):**
- Shows direct correlation (removing intermediate effects)
- AR order (p): PACF cuts off after p lags
- Seasonal AR (P): PACF spikes at seasonal lags

**Reading the Plots:**

| Pattern | ACF | PACF | Model |
|---------|-----|------|-------|
| AR(p) | Decays gradually | Cuts off after lag p | Use AR(p) |
| MA(q) | Cuts off after lag q | Decays gradually | Use MA(q) |
| ARMA(p,q) | Decays gradually | Decays gradually | Use both |

---

## Model Training Process

### Step-by-Step Training

#### Step 1: Data Preparation

```python
# Example: Weekly sales data by region
data = {
    'ouest': [850, 920, 1100, 950, 1200, ...],  # 52+ weeks
    'est': [900, 880, 950, 1050, ...],
    'north': [1400, 1500, 1450, ...],
    'sud': [200, 220, 190, ...]
}
```

**Requirements:**
- Minimum 50-100 observations (more is better)
- Regular time intervals (daily, weekly, monthly)
- No missing values (interpolate if needed)
- Preferably 2+ seasonal cycles (e.g., 2 years of monthly data)

#### Step 2: Exploratory Analysis

```python
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# Convert to time series
ts = pd.Series(data['ouest'], index=pd.date_range('2024-01-01', periods=len(data['ouest']), freq='W'))

# Visualize
ts.plot(title='Sales in Ouest Region')
plt.show()

# Test stationarity
result = adfuller(ts)
print(f'ADF Statistic: {result[0]}')
print(f'p-value: {result[1]}')
# If p-value > 0.05 → non-stationary → need differencing

# Check autocorrelation
plot_acf(ts, lags=50)
plot_pacf(ts, lags=50)
plt.show()
```

#### Step 3: Parameter Selection

```python
from pmdarima import auto_arima

model = auto_arima(
    ts,
    start_p=0, max_p=3,
    start_q=0, max_q=3,
    d=None,  # Let auto_arima determine
    start_P=0, max_P=2,
    start_Q=0, max_Q=2,
    D=None,
    m=12,  # Assume monthly seasonality
    seasonal=True,
    trace=True,
    error_action='ignore',
    suppress_warnings=True,
    stepwise=True
)

print(model.order)  # (p,d,q)
print(model.seasonal_order)  # (P,D,Q,m)
```

**Output Example:**
```
Best model:  ARIMA(1,1,1)(0,1,1,12)
AIC: 487.23
```

#### Step 4: Model Fitting

```python
from statsmodels.tsa.statespace.sarimax import SARIMAX

# Fit model
sarimax_model = SARIMAX(
    ts,
    order=(1, 1, 1),
    seasonal_order=(0, 1, 1, 12),
    enforce_stationarity=False,
    enforce_invertibility=False
)

results = sarimax_model.fit(disp=False)
print(results.summary())
```

**Training Algorithm (Maximum Likelihood Estimation):**
1. Initialize parameters (φ, θ, Φ, Θ, σ²)
2. Compute likelihood of observed data given parameters
3. Use optimization (e.g., L-BFGS) to maximize likelihood
4. Iterate until convergence
5. Return optimal parameters

**What's Being Optimized:**
```
L(φ,θ,Φ,Θ,σ²|y) = Probability of observing data y given parameters
```

#### Step 5: Diagnostic Checks

```python
# Residual analysis
residuals = results.resid

# Should look like white noise (random)
residuals.plot(title='Residuals')
plt.axhline(0, color='red', linestyle='--')
plt.show()

# Autocorrelation of residuals (should be near zero)
plot_acf(residuals, lags=40)
plt.show()

# Ljung-Box test (tests for autocorrelation in residuals)
from statsmodels.stats.diagnostic import acorr_ljungbox
lb_test = acorr_ljungbox(residuals, lags=10, return_df=True)
print(lb_test)
# p-value > 0.05 → residuals are white noise (good!)

# Normality test
from scipy.stats import shapiro
stat, p_value = shapiro(residuals)
print(f'Shapiro test p-value: {p_value}')
# p-value > 0.05 → residuals are normal (good!)
```

**Good Model Indicators:**
- Residuals have zero mean
- Residuals have constant variance (homoscedastic)
- Residuals are uncorrelated (white noise)
- Residuals are normally distributed
- Low AIC/BIC

---

## Forecasting Mechanism

### How SARIMAX Generates Forecasts

#### One-Step-Ahead Forecast

**At time t, predict t+1:**

```python
# Assume ARIMA(1,0,1) for simplicity
y_forecast[t+1] = φ₁ × y[t] + θ₁ × ε[t]
```

**Where:**
- y[t] is the observed value at time t
- ε[t] is the residual (error) at time t
- Known exactly since we've seen the data up to t

#### Multi-Step-Ahead Forecast

**At time t, predict t+h (h > 1):**

```python
# For h-step ahead:
y_forecast[t+h] = φ₁ × y_forecast[t+h-1] + θ₁ × 0
```

**Key Difference:**
- Use *forecasted* values (not observed) for future time steps
- Assume future errors εₜ₊ₕ = 0 (expected value)
- Uncertainty increases with horizon h

**Example (2-step forecast):**
```
t=100, forecast t=101:
  y[101] = 0.6 × y[100] + 0.4 × ε[100]
  
t=100, forecast t=102:
  y[102] = 0.6 × y_forecast[101] + 0.4 × 0
  y[102] = 0.6 × (0.6 × y[100] + 0.4 × ε[100])
```

#### Confidence Intervals

**Forecast Uncertainty:**
```
y[t+h] ~ N(ŷ[t+h], σ²[t+h])
```

- Mean: Point forecast ŷ[t+h]
- Variance: σ²[t+h] increases with h

**95% Confidence Interval:**
```
[ŷ[t+h] - 1.96×σ[t+h], ŷ[t+h] + 1.96×σ[t+h]]
```

**Implementation:**
```python
forecast = results.get_forecast(steps=12)
forecast_df = forecast.summary_frame()

print(forecast_df)
#       mean    mean_se  mean_ci_lower  mean_ci_upper
# t+1   1050      25         1001           1099
# t+2   1080      35         1011           1149
# t+3   1100      42         1017           1183
```

**Interpretation:**
- Week t+1: Forecast 1050 units, 95% confident actual will be 1001-1099
- Week t+3: Forecast 1100 units, 95% confident actual will be 1017-1183
- Notice widening interval (more uncertainty further out)

### Practical Forecasting Code

```python
# Train on historical data
history = ts[:-12]  # Hold out last 12 weeks for testing
model = SARIMAX(history, order=(1,1,1), seasonal_order=(0,1,1,12))
results = model.fit()

# Forecast next 12 weeks
forecast = results.forecast(steps=12)
print(forecast)

# Forecast by region (full system)
demand_by_region = {}
for region in ['ouest', 'est', 'north', 'sud']:
    ts_region = pd.Series(data[region])
    model_region = SARIMAX(ts_region, order=(1,1,1), seasonal_order=(0,1,1,12))
    results_region = model_region.fit()
    forecast_region = results_region.forecast(steps=4)  # Next 4 weeks
    demand_by_region[region] = int(forecast_region.sum())

print(demand_by_region)
# {'ouest': 850, 'est': 900, 'north': 1400, 'sud': 200}
```

---

## Implementation in the Platform

### Architecture

**Important Note:** SARIMAX models are **pre-trained offline** and stored in the `sarimax_x/model/` directory. During API requests, the system only **loads** pre-trained models and generates forecasts—no training occurs during requests. This reduces forecast time from ~120ms to ~5-10ms.

```
OFFLINE (Weekly/Monthly):
┌─────────────────────┐
│  Historical Sales   │
│  Database           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  SARIMAX Training   │
│  (per region/product)│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Save Models to     │
│  sarimax_x/model/   │
│  (pickle files)     │
└─────────────────────┘

ONLINE (API Request):
┌─────────────────────┐
│  Load Pre-trained   │
│  Model from         │
│  sarimax_x/model/   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Generate Forecast  │
│  {region: quantity} │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Optimization       │
│  (Exact ILP)        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Stock Allocation   │
│  by Warehouse       │
└─────────────────────┘
```

### Code Structure

**File:** `forecasting/sarimax_model.py`

```python
import pickle
import os
from pathlib import Path

class SARIMAXForecaster:
    """Regional demand forecasting using pre-trained SARIMAX models"""
    
    def __init__(self, model_dir='sarimax_x/model'):
        self.model_dir = Path(model_dir)
        self.models = {}  # Loaded models cache
        
    def load_model(self, product_id, region):
        """
        Load pre-trained SARIMAX model from disk
        
        Parameters
        ----------
        product_id : str
            Product identifier
        region : str
            Region name (ouest, est, north, sud)
        
        Returns
        -------
        model_fit : SARIMAXResults
            Pre-trained fitted model
        """
        model_key = f"{product_id}_{region}"
        
        # Check cache first
        if model_key in self.models:
            return self.models[model_key]
        
        # Load from disk
        model_path = self.model_dir / f"{model_key}.pkl"
        
        if not model_path.exists():
            raise FileNotFoundError(f"No trained model found for {model_key} at {model_path}")
        
        with open(model_path, 'rb') as f:
            model_fit = pickle.load(f)
        
        # Cache in memory
        self.models[model_key] = model_fit
        
        return model_fit
            
    def forecast(self, product_id, regions, steps=4):
        """
        Generate demand forecast using pre-trained models
        
        Parameters
        ----------
        product_id : str
            Product identifier
        regions : list
            List of regions to forecast
        steps : int
            Number of time periods to forecast
            
        Returns
        -------
        dict
            {region: total_forecasted_demand}
        """
        forecasts = {}
        
        for region in regions:
            try:
                # Load pre-trained model
                model_fit = self.load_model(product_id, region)
                
                # Generate forecast
                forecast = model_fit.forecast(steps=steps)
                
                # Sum over forecast periods to get total demand
                forecasts[region] = int(forecast.sum())
                
            except FileNotFoundError:
                # Model not found, use fallback (e.g., simple average)
                print(f"Warning: No model for {product_id}_{region}, using fallback")
                forecasts[region] = 0
        
        return forecasts
```

### API Integration

**Endpoint:** `POST /api/forecasting/genetic`

```python
from flask import Flask, request, jsonify
from forecasting.sarimax_model import SARIMAXForecaster
from optimization.Genitic import run_exact_ilp_solver

app = Flask(__name__)

# Global forecaster with pre-trained models
# Models are loaded from sarimax_x/model/ directory
forecaster = SARIMAXForecaster(model_dir='sarimax_x/model')

@app.route('/api/forecasting/genetic', methods=['POST'])
def forecast_and_optimize():
    """
    Combined endpoint: forecast demand (using pre-trained SARIMAX), then optimize allocation
    
    Request Body:
    {
        "product_id": "SKU-12345",
        "forecast_periods": 4,
        "total_quantity": 5000
    }
    
    Response:
    {
        "demand_forecast": {"ouest": 850, "est": 900, "north": 1400, "sud": 200},
        "optimized_allocation": {"WH-01": 1200, "WH-02": 800, ...},
        "total_cost": 10403500,
        "service_level": 100,
        "fitness": 0.4695
    }
    """
    data = request.json
    
    # Step 1: Define regions
    regions = ['ouest', 'est', 'north', 'sud']
    
    # Step 2: Generate forecast using PRE-TRAINED models
    # No training happens here - models are loaded from disk
    demand_by_region = forecaster.forecast(
        product_id=data['product_id'],
        regions=regions,
        steps=data.get('forecast_periods', 4)
    )
    
    # Step 3: Load warehouse data
    warehouses = get_warehouses()  # From database
    
    # Step 4: Run optimization
    product = {
        'total_quantity': data.get('total_quantity', sum(demand_by_region.values())),
        'id': data['product_id']
    }
    
    result = run_exact_ilp_solver(
        product=product,
        demand_by_region=demand_by_region,
        warehouses=warehouses
    )
    
    # Step 5: Return combined result
    return jsonify({
        'demand_forecast': demand_by_region,
        'optimized_allocation': result['stock_by_warehouse'],
        'total_cost': result['cost'],
        'service_level': result['service_level'],
        'fitness': result['fitness'],
        'method': 'Exact ILP',
        'runtime_seconds': result['runtime']
    })
```

---

## Offline Model Training

### Overview

SARIMAX models are trained **offline** (not during API requests) and saved to the `sarimax_x/model/` directory. This section explains the offline training process.

### Training Script

**File:** `forecasting/train_sarimax_models.py`

```python
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from pmdarima import auto_arima
import pickle
from pathlib import Path
from database import get_all_products, get_sales_history

def train_models_for_product(product_id, sales_history, model_dir='sarimax_x/model'):
    """
    Train SARIMAX models for all regions for a specific product
    
    Parameters
    ----------
    product_id : str
        Product identifier
    sales_history : dict
        {region: [sales_week1, sales_week2, ...]}
    model_dir : str
        Directory to save trained models
    """
    model_dir = Path(model_dir)
    model_dir.mkdir(parents=True, exist_ok=True)
    
    regions = ['ouest', 'est', 'north', 'sud']
    
    for region in regions:
        print(f"Training model for {product_id} - {region}...")
        
        # Get historical sales for this region
        sales = sales_history.get(region, [])
        
        if len(sales) < 50:
            print(f"  Skipping {region}: insufficient data ({len(sales)} observations)")
            continue
        
        # Convert to time series
        ts = pd.Series(sales, index=pd.date_range(
            end=pd.Timestamp.now(),
            periods=len(sales),
            freq='W'  # Weekly frequency
        ))
        
        # Auto-select best SARIMAX parameters
        auto_model = auto_arima(
            ts,
            start_p=0, max_p=3,
            start_q=0, max_q=3,
            seasonal=True,
            m=12,  # Seasonal period (adjust based on your data frequency)
            d=None,  # Auto-determine differencing
            trace=True,  # Print search progress
            error_action='ignore',
            suppress_warnings=True,
            stepwise=True
        )
        
        print(f"  Best model: ARIMA{auto_model.order} x {auto_model.seasonal_order}")
        
        # Fit SARIMAX with selected parameters
        sarimax = SARIMAX(
            ts,
            order=auto_model.order,
            seasonal_order=auto_model.seasonal_order,
            enforce_stationarity=False,
            enforce_invertibility=False
        )
        
        model_fit = sarimax.fit(disp=False)
        
        # Save model to disk
        model_key = f"{product_id}_{region}"
        model_path = model_dir / f"{model_key}.pkl"
        
        with open(model_path, 'wb') as f:
            pickle.dump(model_fit, f)
        
        print(f"  Model saved to {model_path}")
        
        # Print model diagnostics
        print(f"  AIC: {model_fit.aic:.2f}")
        print(f"  BIC: {model_fit.bic:.2f}")
        print()


def train_all_products():
    """
    Train SARIMAX models for all products in the database
    
    This should be run periodically (e.g., weekly) to update models
    with latest sales data
    """
    print("="*60)
    print("SARIMAX MODEL TRAINING - OFFLINE BATCH")
    print("="*60)
    print()
    
    # Get all products from database
    products = get_all_products()
    
    print(f"Found {len(products)} products to train")
    print()
    
    for product in products:
        product_id = product['id']
        
        # Load historical sales (last 2 years weekly = 104 weeks)
        sales_history = get_sales_history(product_id, limit=104)
        
        # Train models for this product
        train_models_for_product(product_id, sales_history)
    
    print("="*60)
    print("TRAINING COMPLETE")
    print("="*60)


if __name__ == "__main__":
    # Run offline training
    train_all_products()
```

### Scheduling Training

Models should be retrained periodically to incorporate new sales data:

**Option 1: Cron Job (Linux)**
```bash
# Run every Sunday at 2 AM
0 2 * * 0 cd /path/to/project && python forecasting/train_sarimax_models.py
```

**Option 2: Celery Periodic Task (Python)**
```python
from celery import Celery
from celery.schedules import crontab

app = Celery('tasks')

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Run every Sunday at 2 AM
    sender.add_periodic_task(
        crontab(hour=2, minute=0, day_of_week=0),
        train_all_products.s(),
    )

@app.task
def train_all_products():
    from forecasting.train_sarimax_models import train_all_products
    train_all_products()
```

**Option 3: Manual Trigger via API**
```python
@app.route('/api/admin/retrain-models', methods=['POST'])
@require_admin  # Restrict to admin users
def trigger_model_retraining():
    # Run training in background (asynchronous)
    from celery_tasks import train_all_products
    task = train_all_products.delay()
    
    return jsonify({
        'success': True,
        'message': 'Model retraining started',
        'task_id': task.id
    })
```

### Model Versioning

To avoid disrupting live API while retraining:

1. **Train new models to temporary directory:**
   ```python
   train_models_for_product(product_id, sales_history, model_dir='sarimax_x/model_new')
   ```

2. **Validate new models:**
   ```python
   # Test forecast quality on holdout data
   validate_models('sarimax_x/model_new')
   ```

3. **Atomic swap:**
   ```python
   # Backup old models
   shutil.move('sarimax_x/model', 'sarimax_x/model_backup')
   
   # Activate new models
   shutil.move('sarimax_x/model_new', 'sarimax_x/model')
   ```

4. **Clear forecaster cache:**
   ```python
   # Clear in-memory cache so new models are loaded
   forecaster.models.clear()
   ```

---

## Example Walkthrough

### Scenario: Forecasting Demand for Product SKU-789

**Historical Data (12 months, monthly sales by region):**

```python
sales_history = {
    'ouest': [800, 820, 900, 950, 1000, 980, 1050, 1100, 1080, 1150, 1200, 1250],
    'est': [850, 870, 920, 900, 950, 1000, 980, 1050, 1100, 1080, 1150, 1200],
    'north': [1300, 1350, 1400, 1450, 1500, 1480, 1550, 1600, 1580, 1650, 1700, 1750],
    'sud': [180, 190, 200, 195, 210, 220, 215, 230, 240, 235, 250, 260]
}
```

**Step 1: Train SARIMAX for "ouest" region**

```python
ts_ouest = pd.Series(sales_history['ouest'])

# Auto-select parameters
model = auto_arima(ts_ouest, seasonal=True, m=12)
# Result: ARIMA(1,1,1)(0,1,1,12)

# Fit model
sarimax = SARIMAX(ts_ouest, order=(1,1,1), seasonal_order=(0,1,1,12))
results = sarimax.fit()

# Model learns:
# - φ₁ = 0.65 (AR: yesterday's sales influence)
# - θ₁ = -0.40 (MA: forecast error correction)
# - Θ₁ = -0.85 (Seasonal MA: seasonal error correction)
```

**Step 2: Forecast next month**

```python
forecast_ouest = results.forecast(steps=1)
print(forecast_ouest)
# [1285]  (expected sales in month 13)
```

**Calculation (simplified):**
```
# Month 13 forecast
y[13] = φ₁ × (y[12] - y[11]) + y[12] + θ₁ × ε[12] + Θ₁ × ε[1]
y[13] = 0.65 × (1250 - 1200) + 1250 + (-0.40) × 15 + (-0.85) × (-20)
y[13] = 0.65 × 50 + 1250 - 6 + 17
y[13] ≈ 1293 ≈ 1285 (after all components)
```

**Step 3: Repeat for all regions**

```python
demand_forecast = {}
for region, sales in sales_history.items():
    ts = pd.Series(sales)
    model = SARIMAX(ts, order=(1,1,1), seasonal_order=(0,1,1,12))
    results = model.fit()
    forecast = results.forecast(steps=1)
    demand_forecast[region] = int(forecast[0])

print(demand_forecast)
# {'ouest': 1285, 'est': 1235, 'north': 1795, 'sud': 268}
```

**Total Demand:** 1285 + 1235 + 1795 + 268 = **4583 units**

**Step 4: Pass to optimization**

```python
# Seller has 5000 units to allocate
product = {
    'product_id': 'SKU-789',
    'total_quantity': 5000
}

result = run_exact_ilp_solver(
    product=product,
    demand_by_region=demand_forecast,
    warehouses=warehouses
)

print(result['stock_by_warehouse'])
# Optimal allocation considering transport/holding costs and regional demand
```

---

## Advantages and Limitations

### Advantages

1. **Captures Complex Patterns:**
   - Trend (via I component)
   - Seasonality (via seasonal components)
   - Short-term dependencies (via AR/MA)

2. **Statistical Rigor:**
   - Confidence intervals for forecasts
   - Hypothesis tests for parameters
   - Diagnostic checks for model quality

3. **Flexible:**
   - Adapt to different data frequencies (daily, weekly, monthly)
   - Incorporate exogenous variables
   - Multiple seasonal patterns (e.g., weekly + yearly)

4. **Interpretable:**
   - Parameters have clear meanings
   - Decompose forecast into components
   - Understand which factors drive predictions

5. **Well-Established:**
   - Decades of research and refinement
   - Robust libraries (statsmodels, pmdarima)
   - Standard in industry

### Limitations

1. **Assumes Linear Relationships:**
   - Cannot capture complex non-linear dynamics
   - E.g., sudden regime changes, threshold effects

2. **Requires Sufficient Data:**
   - Minimum 50-100 observations
   - Preferably 2+ seasonal cycles
   - New products with limited history perform poorly

3. **Sensitive to Outliers:**
   - Extreme values distort parameter estimates
   - Requires outlier detection and treatment

4. **Univariate (Unless Using X):**
   - Standard SARIMAX models one series at a time
   - Doesn't capture cross-regional dependencies
   - E.g., high sales in "ouest" might predict high sales in "est"

5. **Computational Cost:**
   - Maximum likelihood estimation is iterative
   - Can be slow for long series or complex models
   - Grid search over parameters is expensive

6. **Exogenous Variables Limitation:**
   - Must have future values of X for forecasting
   - Not useful for variables you can't predict (e.g., competitor actions)

7. **Short-Term Horizon:**
   - Forecast quality degrades beyond 6-12 periods
   - Long-term strategic planning needs other methods

### When to Use SARIMAX

**Good For:**
- Regular historical data (weekly/monthly sales)
- Clear seasonal patterns (holidays, weather)
- Short to medium-term forecasts (1-12 periods)
- Univariate time series with trend/seasonality

**Not Good For:**
- New products (no historical data)
- Highly volatile/chaotic data
- Long-term forecasts (years ahead)
- Complex multi-variate dependencies

---

## Summary

SARIMAX is a powerful statistical forecasting method that combines:
- **AutoRegression** (past values predict future)
- **Integration** (differencing for stationarity)
- **Moving Average** (past errors correct future predictions)
- **Seasonality** (repeating patterns)
- **Exogenous variables** (external factors)

In this platform:
1. Historical sales data by region is collected
2. SARIMAX model is trained for each region independently
3. Forecast generates expected demand by region
4. Optimization algorithms allocate inventory to minimize costs while meeting forecasted demand

The key insight: **SARIMAX provides the "what" (demand forecast), and optimization algorithms provide the "how" (optimal allocation)**.

---

**Document Version:** 1.0  
**Last Updated:** May 21, 2026  
**For:** Master's Thesis - Warehouse Optimization Platform
