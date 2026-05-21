# Platform Process Flow: End-to-End User Journey

## Overview

This document describes the complete process flow of the warehouse optimization platform, from user interaction on the frontend through backend processing to results presentation. It covers the user journey, system architecture, data flow, and implementation details for a production-ready e-commerce warehouse optimization system.

---

## Table of Contents

1. [System Architecture Overview](#system-architecture-overview)
2. [User Journey](#user-journey)
3. [Frontend Flow](#frontend-flow)
4. [Backend Processing](#backend-processing)
5. [Database Operations](#database-operations)
6. [Results Visualization](#results-visualization)
7. [Deployment Architecture](#deployment-architecture)
8. [Security and Authentication](#security-and-authentication)
9. [Monitoring and Logging](#monitoring-and-logging)
10. [Example Walkthrough](#example-walkthrough)

---

## System Architecture Overview

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         USER LAYER                               │
│  ┌────────────────────┐  ┌────────────────────┐                 │
│  │  Web Dashboard     │  │  Mobile App        │                 │
│  │  (React/Vue)       │  │  (React Native)    │                 │
│  └─────────┬──────────┘  └──────────┬─────────┘                 │
└────────────┼─────────────────────────┼───────────────────────────┘
             │                         │
             └─────────┬───────────────┘
                       │ HTTPS / WebSocket
                       │
┌──────────────────────▼───────────────────────────────────────────┐
│                    PRESENTATION LAYER                            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  API Gateway (NGINX / Kong / AWS API Gateway)            │  │
│  │  - Authentication                                         │  │
│  │  - Rate Limiting                                          │  │
│  │  - Load Balancing                                         │  │
│  └───────────────────────┬───────────────────────────────────┘  │
└────────────────────────────┼────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    APPLICATION LAYER                            │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Flask/FastAPI REST API Server                         │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │    │
│  │  │  Auth Module │  │  Product API │  │  Warehouse   │ │    │
│  │  │              │  │              │  │  API         │ │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │    │
│  │  ┌──────────────────────────────────────────────────┐ │    │
│  │  │  Forecasting + Optimization API                  │ │    │
│  │  │  /api/forecasting/genetic                        │ │    │
│  │  └──────────────────────────────────────────────────┘ │    │
│  └────────────────────────────────────────────────────────┘    │
└────────────────────────────┬───────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │  SARIMAX         │  │  Exact ILP       │  │  Result      │ │
│  │  Forecasting     │→ │  Optimization    │→ │  Processor   │ │
│  │  Service         │  │  Service         │  │              │ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘ │
└────────────────────────────┬───────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                        DATA LAYER                               │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │  PostgreSQL DB   │  │  Redis Cache     │  │  File Storage│ │
│  │  - Products      │  │  - Sessions      │  │  - SARIMAX   │ │
│  │  - Warehouses    │  │  - Forecasts     │  │    Models    │ │
│  │  - Sales History │  │  - Results       │  │  - Reports   │ │
│  │  - Users         │  │                  │  │              │ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | React / Vue.js | Interactive UI |
| **Mobile** | React Native | Cross-platform mobile app |
| **API Gateway** | NGINX / Kong | Routing, auth, rate limiting |
| **Backend** | Flask / FastAPI (Python) | REST API, business logic |
| **Forecasting** | statsmodels (SARIMAX) | Demand prediction |
| **Optimization** | PuLP + CBC Solver | Exact ILP optimization |
| **Database** | PostgreSQL | Relational data storage |
| **Cache** | Redis | Session and result caching |
| **Storage** | AWS S3 / MinIO | Model and report storage |
| **Message Queue** | Celery + RabbitMQ | Async task processing |
| **Monitoring** | Prometheus + Grafana | Metrics and dashboards |
| **Logging** | ELK Stack (Elasticsearch, Logstash, Kibana) | Centralized logging |
| **Deployment** | Docker + Kubernetes | Container orchestration |

---

## User Journey

### Persona: E-commerce Operations Manager

**Name:** Sarah  
**Goal:** Optimize warehouse stock allocation for a popular product based on regional demand forecast  
**Context:** Weekly planning cycle, preparing for upcoming month

### Journey Steps

1. **Login** → Authenticate to the platform
2. **Dashboard** → View current inventory status
3. **Product Selection** → Choose product to optimize
4. **Forecast Request** → Initiate demand forecast + optimization
5. **Review Results** → Analyze recommendations
6. **Approval** → Accept or modify allocation plan
7. **Execution** → System updates warehouse stock levels
8. **Monitoring** → Track actual vs. forecasted performance

---

## Frontend Flow

### 1. Login Page

**URL:** `/login`

**Components:**
```jsx
<LoginPage>
  <Logo />
  <LoginForm>
    <EmailInput />
    <PasswordInput />
    <RememberMeCheckbox />
    <LoginButton />
    <ForgotPasswordLink />
  </LoginForm>
</LoginPage>
```

**User Actions:**
1. Enter email and password
2. Click "Login"
3. Frontend sends POST request to `/api/auth/login`
4. Backend validates credentials
5. Backend returns JWT token
6. Frontend stores token in localStorage
7. Redirect to dashboard

**API Call:**
```javascript
const login = async (email, password) => {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ email, password })
  });
  
  const data = await response.json();
  
  if (data.success) {
    localStorage.setItem('token', data.token);
    localStorage.setItem('user', JSON.stringify(data.user));
    window.location.href = '/dashboard';
  } else {
    alert(data.error);
  }
};
```

---

### 2. Dashboard Page

**URL:** `/dashboard`

**Layout:**
```
┌────────────────────────────────────────────────────────────┐
│  HEADER: Logo | Welcome, Sarah | Notifications | Logout   │
├────────────────────────────────────────────────────────────┤
│ SIDEBAR       │  MAIN CONTENT                             │
│ - Dashboard   │  ┌──────────────────────────────────────┐ │
│ - Products    │  │  Inventory Overview                  │ │
│ - Warehouses  │  │  ┌────────┐ ┌────────┐ ┌────────┐   │ │
│ - Forecasts   │  │  │ Total  │ │ Active │ │ Alerts │   │ │
│ - Reports     │  │  │ Stock  │ │Products│ │        │   │ │
│ - Settings    │  │  │ 45,230 │ │  127   │ │   3    │   │ │
│               │  │  └────────┘ └────────┘ └────────┘   │ │
│               │  └──────────────────────────────────────┘ │
│               │  ┌──────────────────────────────────────┐ │
│               │  │  Recent Optimizations                │ │
│               │  │  [Table: Product | Date | Status]    │ │
│               │  └──────────────────────────────────────┘ │
│               │  ┌──────────────────────────────────────┐ │
│               │  │  Quick Actions                       │ │
│               │  │  [Button: New Optimization]          │ │
│               │  │  [Button: View Reports]              │ │
│               │  └──────────────────────────────────────┘ │
└───────────────┴────────────────────────────────────────────┘
```

**Data Loading:**
```javascript
useEffect(() => {
  const fetchDashboardData = async () => {
    const token = localStorage.getItem('token');
    
    const response = await fetch('/api/dashboard', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    const data = await response.json();
    
    setTotalStock(data.total_stock);
    setActiveProducts(data.active_products);
    setAlerts(data.alerts);
    setRecentOptimizations(data.recent_optimizations);
  };
  
  fetchDashboardData();
}, []);
```

---

### 3. Product Selection Page

**URL:** `/products`

**Layout:**
```
┌────────────────────────────────────────────────────────────┐
│  HEADER: Products Management                              │
├────────────────────────────────────────────────────────────┤
│  [Search: _________] [Filter: Category ▼] [+ Add Product] │
├────────────────────────────────────────────────────────────┤
│  Product List (Table)                                     │
│  ┌─────┬──────────┬──────────┬────────┬─────────────────┐ │
│  │ SKU │ Name     │ Category │ Stock  │ Actions         │ │
│  ├─────┼──────────┼──────────┼────────┼─────────────────┤ │
│  │ 123 │ Laptop   │ Tech     │ 1,250  │ [View] [Optimize]│
│  │ 456 │ Phone    │ Tech     │ 3,400  │ [View] [Optimize]│
│  │ 789 │ Headset  │ Audio    │ 5,600  │ [View] [Optimize]│
│  └─────┴──────────┴──────────┴────────┴─────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

**User Actions:**
1. Browse product list
2. Use search/filter to find specific product
3. Click "Optimize" button for product SKU-789 (Headset)
4. Navigate to optimization page

**Code:**
```javascript
const ProductList = () => {
  const [products, setProducts] = useState([]);
  
  const handleOptimize = (productId) => {
    // Navigate to optimization page
    navigate(`/optimize/${productId}`);
  };
  
  return (
    <Table>
      {products.map(product => (
        <TableRow key={product.id}>
          <TableCell>{product.sku}</TableCell>
          <TableCell>{product.name}</TableCell>
          <TableCell>{product.category}</TableCell>
          <TableCell>{product.stock}</TableCell>
          <TableCell>
            <Button onClick={() => navigate(`/products/${product.id}`)}>
              View
            </Button>
            <Button 
              onClick={() => handleOptimize(product.id)}
              variant="primary"
            >
              Optimize
            </Button>
          </TableCell>
        </TableRow>
      ))}
    </Table>
  );
};
```

---

### 4. Optimization Page

**URL:** `/optimize/:productId`

**Layout:**
```
┌────────────────────────────────────────────────────────────┐
│  HEADER: Optimize Stock Allocation - SKU-789 Headset      │
├────────────────────────────────────────────────────────────┤
│  STEP 1: Configuration                                    │
│  ┌────────────────────────────────────────────────────┐   │
│  │ Forecast Periods: [4     ▼] weeks                 │   │
│  │ Total Quantity:   [5000  ] units (optional)        │   │
│  │ Optimization:     [Exact ILP ▼]                    │   │
│  │ Priority:         [⚖️ Balanced ▼] (Service vs Cost)│   │
│  │                                                    │   │
│  │ [Button: Run Optimization]                         │   │
│  └────────────────────────────────────────────────────┘   │
│                                                           │
│  STEP 2: Processing (Loading State)                      │
│  ┌────────────────────────────────────────────────────┐   │
│  │ 🔄 Forecasting demand... (120ms)                   │   │
│  │ ✅ Demand forecast complete                        │   │
│  │                                                    │   │
│  │ 🔄 Optimizing allocation... (31ms)                 │   │
│  │ ✅ Optimization complete                           │   │
│  │                                                    │   │
│  │ Progress: [████████████████████████] 100%          │   │
│  └────────────────────────────────────────────────────┘   │
│                                                           │
│  STEP 3: Results (see below)                             │
└────────────────────────────────────────────────────────────┘
```

**User Actions:**
1. Configure optimization parameters
2. Click "Run Optimization"
3. Wait for processing (with real-time status updates)
4. Review results

**Frontend Code:**
```javascript
const OptimizationPage = () => {
  const { productId } = useParams();
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('');
  const [result, setResult] = useState(null);
  
  const [config, setConfig] = useState({
    forecast_periods: 4,
    total_quantity: null,
    optimization_method: 'ilp',
    alpha: 0.5
  });
  
  const handleOptimize = async () => {
    setLoading(true);
    setStatus('Initiating request...');
    
    try {
      const token = localStorage.getItem('token');
      
      const response = await fetch('/api/forecasting/genetic', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          product_id: productId,
          ...config
        })
      });
      
      if (!response.ok) {
        throw new Error('Optimization failed');
      }
      
      // For real-time updates, use WebSocket or polling
      // Here we'll use simple polling
      const jobId = await response.json().job_id;
      
      // Poll for results
      const pollInterval = setInterval(async () => {
        const statusResponse = await fetch(`/api/jobs/${jobId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        const statusData = await statusResponse.json();
        
        setStatus(statusData.status);
        
        if (statusData.status === 'completed') {
          clearInterval(pollInterval);
          setResult(statusData.result);
          setLoading(false);
        } else if (statusData.status === 'failed') {
          clearInterval(pollInterval);
          setLoading(false);
          alert('Optimization failed: ' + statusData.error);
        }
      }, 500);
      
    } catch (error) {
      setLoading(false);
      alert('Error: ' + error.message);
    }
  };
  
  return (
    <Container>
      <ConfigurationForm
        config={config}
        onChange={setConfig}
        onSubmit={handleOptimize}
      />
      
      {loading && (
        <LoadingStatus status={status} />
      )}
      
      {result && (
        <ResultsDisplay result={result} />
      )}
    </Container>
  );
};
```

---

### 5. Results Display

**Layout:**
```
┌────────────────────────────────────────────────────────────┐
│  Optimization Results - SKU-789 Headset                    │
├────────────────────────────────────────────────────────────┤
│  Summary                                                   │
│  ┌─────────────┬─────────────┬─────────────┬────────────┐ │
│  │ Total Cost  │ Service     │ Fitness     │ Runtime    │ │
│  │ 10,403,500  │ 100%        │ 0.4695      │ 31 ms      │ │
│  │ DZD         │             │             │            │ │
│  └─────────────┴─────────────┴─────────────┴────────────┘ │
├────────────────────────────────────────────────────────────┤
│  Demand Forecast by Region                                │
│  ┌────────────────────────────────────────────────────┐   │
│  │  [Bar Chart]                                       │   │
│  │   North: ████████████████ 1400                     │   │
│  │   Est:   ████████████ 900                          │   │
│  │   Ouest: ███████████ 850                           │   │
│  │   Sud:   ███ 200                                   │   │
│  └────────────────────────────────────────────────────┘   │
├────────────────────────────────────────────────────────────┤
│  Recommended Warehouse Allocation                         │
│  ┌───────┬────────┬─────────┬────────┬─────────────────┐ │
│  │ WH    │ Region │ Current │ New    │ Change          │ │
│  ├───────┼────────┼─────────┼────────┼─────────────────┤ │
│  │ WH-01 │ North  │ 500     │ 1,200  │ +700 ↑          │ │
│  │ WH-02 │ Ouest  │ 400     │ 850    │ +450 ↑          │ │
│  │ WH-03 │ North  │ 800     │ 1,500  │ +700 ↑          │ │
│  │ WH-04 │ Est    │ 200     │ 300    │ +100 ↑          │ │
│  │ WH-05 │ Ouest  │ 500     │ 0      │ -500 ↓          │ │
│  │ ...   │ ...    │ ...     │ ...    │ ...             │ │
│  └───────┴────────┴─────────┴────────┴─────────────────┘ │
├────────────────────────────────────────────────────────────┤
│  Top Recommendations                                      │
│  1. WH-03 (North): Increase by 700 units                  │
│     → High-demand region, low holding cost                │
│                                                           │
│  2. WH-05 (Ouest): Decrease by 500 units                  │
│     → High holding cost, better alternatives available    │
│                                                           │
│  3. WH-02 (Ouest): Increase by 450 units                  │
│     → Meet regional demand, moderate cost                 │
├────────────────────────────────────────────────────────────┤
│  Actions                                                  │
│  [Button: Approve & Execute]  [Button: Modify]  [Button: Export Report]
└────────────────────────────────────────────────────────────┘
```

**Components:**
```javascript
const ResultsDisplay = ({ result }) => {
  return (
    <ResultsContainer>
      {/* Summary Cards */}
      <SummarySection>
        <MetricCard
          title="Total Cost"
          value={`${result.optimization.total_cost.toLocaleString()} DZD`}
          trend="down"
          trendValue="2.6%"
        />
        <MetricCard
          title="Service Level"
          value={`${result.optimization.service_level}%`}
          trend="neutral"
        />
        <MetricCard
          title="Fitness Score"
          value={result.optimization.fitness.toFixed(4)}
          trend="up"
        />
        <MetricCard
          title="Runtime"
          value={`${(result.optimization.runtime_seconds * 1000).toFixed(0)} ms`}
          icon="⚡"
        />
      </SummarySection>
      
      {/* Demand Forecast Chart */}
      <ForecastSection>
        <h3>Demand Forecast by Region</h3>
        <BarChart
          data={result.forecast.demand_by_region}
          colors={['#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']}
        />
      </ForecastSection>
      
      {/* Allocation Table */}
      <AllocationSection>
        <h3>Recommended Warehouse Allocation</h3>
        <AllocationTable
          currentStock={currentStock}  // From props
          optimizedStock={result.optimization.stock_by_warehouse}
          warehouses={warehouses}  // From props
        />
      </AllocationSection>
      
      {/* Recommendations */}
      <RecommendationsSection>
        <h3>Top Recommendations</h3>
        {result.recommendations.map((rec, idx) => (
          <RecommendationCard key={idx} recommendation={rec} />
        ))}
      </RecommendationsSection>
      
      {/* Action Buttons */}
      <ActionSection>
        <Button variant="primary" onClick={handleApprove}>
          Approve & Execute
        </Button>
        <Button variant="secondary" onClick={handleModify}>
          Modify
        </Button>
        <Button variant="outline" onClick={handleExport}>
          Export Report
        </Button>
      </ActionSection>
    </ResultsContainer>
  );
};
```

---

### 6. Approval and Execution

**User Action:** Click "Approve & Execute"

**Confirmation Modal:**
```
┌────────────────────────────────────────────────────────────┐
│  Confirm Stock Allocation                                  │
├────────────────────────────────────────────────────────────┤
│  You are about to update stock levels for 14 warehouses.  │
│                                                            │
│  This action will:                                         │
│  • Update warehouse inventory in the system                │
│  • Generate transfer orders for stock movement             │
│  • Notify warehouse managers                               │
│  • Record this decision for audit trail                    │
│                                                            │
│  Are you sure you want to proceed?                         │
│                                                            │
│  [Button: Cancel]  [Button: Confirm]                       │
└────────────────────────────────────────────────────────────┘
```

**Frontend Code:**
```javascript
const handleApprove = async () => {
  const confirmed = await showConfirmDialog({
    title: 'Confirm Stock Allocation',
    message: 'You are about to update stock levels...',
    confirmText: 'Confirm',
    cancelText: 'Cancel'
  });
  
  if (!confirmed) return;
  
  try {
    const token = localStorage.getItem('token');
    
    const response = await fetch('/api/optimization/approve', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        product_id: productId,
        optimization_result_id: result.result_id,
        approved_by: user.id
      })
    });
    
    const data = await response.json();
    
    if (data.success) {
      showSuccessToast('Stock allocation approved and executed');
      navigate('/dashboard');
    } else {
      showErrorToast(data.error);
    }
  } catch (error) {
    showErrorToast('Failed to approve allocation');
  }
};
```

---

## Backend Processing

### API Endpoint Handler

**File:** `api/routes/forecasting.py`

```python
from flask import Blueprint, request, jsonify
from services.auth_service import require_auth
from services.forecasting_service import SARIMAXForecaster
from services.optimization_service import OptimizationService
from services.database_service import DatabaseService
import time

bp = Blueprint('forecasting', __name__)

forecaster = SARIMAXForecaster()
optimizer = OptimizationService(default_method='ilp')
db = DatabaseService()

@bp.route('/api/forecasting/genetic', methods=['POST'])
@require_auth  # Decorator for JWT authentication
def forecast_and_optimize(current_user):
    """
    Main endpoint for forecasting + optimization
    """
    start_time = time.time()
    
    try:
        data = request.json
        product_id = data['product_id']
        
        # Log request
        logger.info(f"Optimization request: user={current_user.id}, product={product_id}")
        
        # ===== STEP 1: Load Data =====
        sales_history = db.get_sales_history(product_id, limit=104)
        warehouses = db.get_warehouses()
        product_info = db.get_product(product_id)
        
        if not product_info:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        # ===== STEP 2: SARIMAX Forecasting =====
        regions = ['ouest', 'est', 'north', 'sud']
        demand_by_region = forecaster.train_and_forecast(
            product_id=product_id,
            sales_history=sales_history,
            regions=regions,
            forecast_periods=data.get('forecast_periods', 4)
        )
        
        # ===== STEP 3: Optimization =====
        total_quantity = data.get('total_quantity') or (
            sum(wh.get('stock_level', 0) for wh in warehouses.values()) +
            sum(demand_by_region.values())
        )
        
        product_dict = {
            'product_id': product_id,
            'total_quantity': total_quantity
        }
        
        optimization_result = optimizer.optimize(
            product=product_dict,
            demand_by_region=demand_by_region,
            warehouses=warehouses,
            method=data.get('optimization_method', 'ilp'),
            alpha=data.get('alpha', 0.5)
        )
        
        # ===== STEP 4: Post-Process =====
        recommendations = generate_recommendations(
            current_stock={wh_id: wh.get('stock_level', 0) for wh_id, wh in warehouses.items()},
            optimized_stock=optimization_result['stock_by_warehouse'],
            warehouses=warehouses,
            demand_by_region=demand_by_region
        )
        
        # ===== STEP 5: Save to Database =====
        result_id = db.save_optimization_result(
            user_id=current_user.id,
            product_id=product_id,
            demand_forecast=demand_by_region,
            optimization_result=optimization_result,
            recommendations=recommendations,
            status='pending_approval'
        )
        
        # ===== STEP 6: Construct Response =====
        response = {
            'success': True,
            'result_id': result_id,
            'product_id': product_id,
            'forecast': {
                'demand_by_region': demand_by_region,
                'total_forecast': sum(demand_by_region.values()),
                'forecast_periods': data.get('forecast_periods', 4),
                'forecast_timestamp': pd.Timestamp.now().isoformat()
            },
            'optimization': {
                'method': optimization_result['method'],
                'stock_by_warehouse': optimization_result['stock_by_warehouse'],
                'total_cost': optimization_result['cost'],
                'cost_breakdown': {
                    'holding_cost': compute_holding_cost(optimization_result['stock_by_warehouse'], warehouses),
                    'transfer_cost': compute_transfer_cost(optimization_result['stock_by_warehouse'], warehouses)
                },
                'service_level': optimization_result['service_level'],
                'fitness': optimization_result['fitness'],
                'runtime_seconds': optimization_result['runtime'],
                'solver_status': optimization_result.get('solver_status', 'N/A')
            },
            'recommendations': recommendations[:10],
            'metadata': {
                'request_id': f"req-{int(time.time()*1000)}",
                'processing_time_ms': int((time.time() - start_time) * 1000),
                'api_version': '2.1'
            }
        }
        
        # Log success
        logger.info(f"Optimization complete: result_id={result_id}, time={response['metadata']['processing_time_ms']}ms")
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Optimization error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'details': str(e) if app.debug else None
        }), 500


@bp.route('/api/optimization/approve', methods=['POST'])
@require_auth
def approve_optimization(current_user):
    """
    Approve and execute optimization result
    """
    try:
        data = request.json
        result_id = data['optimization_result_id']
        
        # Load optimization result
        result = db.get_optimization_result(result_id)
        
        if not result:
            return jsonify({'success': False, 'error': 'Result not found'}), 404
        
        if result['user_id'] != current_user.id and not current_user.is_admin:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Execute: Update warehouse stock levels
        for wh_id, new_stock in result['optimized_allocation'].items():
            db.update_warehouse_stock(wh_id, result['product_id'], new_stock)
        
        # Generate transfer orders
        transfer_orders = []
        for wh_id, new_stock in result['optimized_allocation'].items():
            current_stock = db.get_warehouse_stock(wh_id, result['product_id'])
            change = new_stock - current_stock
            
            if change != 0:
                order_id = db.create_transfer_order(
                    warehouse_id=wh_id,
                    product_id=result['product_id'],
                    quantity=abs(change),
                    direction='inbound' if change > 0 else 'outbound',
                    created_by=current_user.id
                )
                transfer_orders.append(order_id)
        
        # Update result status
        db.update_optimization_result_status(result_id, 'executed')
        
        # Notify warehouse managers
        notify_warehouse_managers(transfer_orders)
        
        # Log action
        db.log_action(
            user_id=current_user.id,
            action='approve_optimization',
            details={'result_id': result_id, 'transfer_orders': transfer_orders}
        )
        
        return jsonify({
            'success': True,
            'result_id': result_id,
            'transfer_orders_created': len(transfer_orders),
            'message': 'Optimization approved and executed successfully'
        }), 200
    
    except Exception as e:
        logger.error(f"Approval error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Failed to execute optimization'
        }), 500
```

---

## Database Operations

### Schema Design

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

-- Products table
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Warehouses table
CREATE TABLE warehouses (
    id VARCHAR(50) PRIMARY KEY,
    region VARCHAR(50) NOT NULL,
    capacity INTEGER NOT NULL,
    holding_cost DECIMAL(10, 2),
    transport_cost DECIMAL(10, 2),
    address TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Sales history table
CREATE TABLE sales_history (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id),
    region VARCHAR(50),
    sale_date DATE NOT NULL,
    quantity INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Optimization results table
CREATE TABLE optimization_results (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    product_id INTEGER REFERENCES products(id),
    demand_forecast JSONB,  -- {region: quantity}
    optimized_allocation JSONB,  -- {warehouse_id: quantity}
    total_cost DECIMAL(12, 2),
    service_level DECIMAL(5, 2),
    fitness DECIMAL(10, 6),
    method VARCHAR(50),
    status VARCHAR(50) DEFAULT 'pending_approval',  -- pending_approval, executed, rejected
    created_at TIMESTAMP DEFAULT NOW(),
    approved_at TIMESTAMP,
    approved_by INTEGER REFERENCES users(id)
);

-- Transfer orders table
CREATE TABLE transfer_orders (
    id SERIAL PRIMARY KEY,
    warehouse_id VARCHAR(50) REFERENCES warehouses(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    direction VARCHAR(20),  -- inbound, outbound
    status VARCHAR(50) DEFAULT 'pending',  -- pending, in_progress, completed, cancelled
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Audit log table
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100),
    details JSONB,
    ip_address VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Key Queries

```python
class DatabaseService:
    def get_sales_history(self, product_id, limit=104):
        """
        Fetch historical sales data for a product, grouped by region
        """
        query = """
        SELECT region, sale_date, SUM(quantity) as total_quantity
        FROM sales_history
        WHERE product_id = %s
        GROUP BY region, sale_date
        ORDER BY region, sale_date DESC
        LIMIT %s
        """
        
        result = self.execute_query(query, (product_id, limit))
        
        # Organize by region
        sales_by_region = {}
        for row in result:
            region = row['region']
            if region not in sales_by_region:
                sales_by_region[region] = []
            sales_by_region[region].append(row['total_quantity'])
        
        return sales_by_region
    
    def save_optimization_result(self, user_id, product_id, demand_forecast, 
                                 optimization_result, recommendations, status='pending_approval'):
        """
        Save optimization result to database
        """
        query = """
        INSERT INTO optimization_results 
        (user_id, product_id, demand_forecast, optimized_allocation, 
         total_cost, service_level, fitness, method, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        
        result = self.execute_query(query, (
            user_id,
            product_id,
            json.dumps(demand_forecast),
            json.dumps(optimization_result['stock_by_warehouse']),
            optimization_result['cost'],
            optimization_result['service_level'],
            optimization_result['fitness'],
            optimization_result['method'],
            status
        ))
        
        return result[0]['id']
```

---

## Results Visualization

### Interactive Charts

```javascript
import { Bar, Line, Scatter } from 'react-chartjs-2';

const ForecastChart = ({ demandByRegion }) => {
  const data = {
    labels: Object.keys(demandByRegion),
    datasets: [{
      label: 'Forecasted Demand',
      data: Object.values(demandByRegion),
      backgroundColor: ['#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
    }]
  };
  
  return <Bar data={data} options={chartOptions} />;
};

const AllocationTable = ({ currentStock, optimizedStock, warehouses }) => {
  const rows = Object.keys(optimizedStock).map(whId => {
    const current = currentStock[whId] || 0;
    const optimized = optimizedStock[whId];
    const change = optimized - current;
    
    return {
      id: whId,
      region: warehouses[whId].region,
      current,
      optimized,
      change,
      changePercent: current > 0 ? (change / current) * 100 : 0
    };
  });
  
  // Sort by absolute change (most significant first)
  rows.sort((a, b) => Math.abs(b.change) - Math.abs(a.change));
  
  return (
    <Table>
      <TableHead>
        <TableRow>
          <TableCell>Warehouse</TableCell>
          <TableCell>Region</TableCell>
          <TableCell>Current</TableCell>
          <TableCell>Optimized</TableCell>
          <TableCell>Change</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {rows.map(row => (
          <TableRow key={row.id} highlight={Math.abs(row.change) > 100}>
            <TableCell>{row.id}</TableCell>
            <TableCell>
              <RegionBadge region={row.region} />
            </TableCell>
            <TableCell>{row.current.toLocaleString()}</TableCell>
            <TableCell>{row.optimized.toLocaleString()}</TableCell>
            <TableCell>
              <ChangeIndicator
                value={row.change}
                percent={row.changePercent}
              />
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
};

const ChangeIndicator = ({ value, percent }) => {
  const isPositive = value > 0;
  const color = isPositive ? 'green' : value < 0 ? 'red' : 'gray';
  const icon = isPositive ? '↑' : value < 0 ? '↓' : '→';
  
  return (
    <span style={{ color }}>
      {value > 0 ? '+' : ''}{value.toLocaleString()} ({percent.toFixed(1)}%) {icon}
    </span>
  );
};
```

---

## Deployment Architecture

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  # Frontend
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://api:5000
    depends_on:
      - api
  
  # API Server
  api:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/warehouse_opt
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      - postgres
      - redis
    volumes:
      - ./cache:/app/cache
  
  # PostgreSQL Database
  postgres:
    image: postgres:14
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=warehouse_opt
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  # Redis Cache
  redis:
    image: redis:7
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
  
  # Celery Worker (for async tasks)
  celery:
    build: ./backend
    command: celery -A app.celery worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/warehouse_opt
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis

volumes:
  postgres_data:
  redis_data:
```

---

## Security and Authentication

### JWT Authentication

```python
import jwt
from functools import wraps
from flask import request, jsonify

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Missing authorization token'}), 401
        
        try:
            # Remove 'Bearer ' prefix
            token = token.split(' ')[1]
            
            # Decode JWT
            payload = jwt.decode(token, app.config['JWT_SECRET'], algorithms=['HS256'])
            
            # Load user
            user = db.get_user(payload['user_id'])
            
            if not user:
                return jsonify({'error': 'User not found'}), 401
            
            # Pass user to route handler
            return f(user, *args, **kwargs)
        
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
    
    return decorated_function
```

---

## Monitoring and Logging

### Logging Configuration

```python
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
logger = logging.getLogger('warehouse_optimization')
logger.setLevel(logging.INFO)

# File handler (with rotation)
file_handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=10
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(
    '%(levelname)s: %(message)s'
))
logger.addHandler(console_handler)

# Usage in API
logger.info(f"Optimization request: user={user_id}, product={product_id}")
logger.error(f"Optimization failed: {str(e)}", exc_info=True)
```

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, generate_latest

# Define metrics
optimization_requests = Counter(
    'optimization_requests_total',
    'Total optimization requests',
    ['method', 'status']
)

optimization_duration = Histogram(
    'optimization_duration_seconds',
    'Optimization duration',
    ['method']
)

# Instrument code
@optimization_duration.labels(method='ilp').time()
def run_optimization(...):
    result = run_exact_ilp_solver(...)
    optimization_requests.labels(method='ilp', status='success').inc()
    return result

# Metrics endpoint
@app.route('/metrics')
def metrics():
    return generate_latest()
```

---

## Example Walkthrough

### Complete End-to-End Flow

**Scenario:** Sarah wants to optimize stock for product SKU-789 (Headphones)

1. **Login:** Sarah enters credentials → JWT token issued → Redirect to dashboard
2. **Navigate:** Dashboard → Products → Search "SKU-789" → Click "Optimize"
3. **Configure:** Forecast 4 weeks, use Exact ILP, balanced priority (α=0.5)
4. **Request:** Frontend POST to `/api/forecasting/genetic`
5. **Backend Processing:**
   - Fetch historical sales (104 weeks)
   - Train SARIMAX models (one per region)
   - Generate forecast: {ouest: 850, est: 900, north: 1400, sud: 200}
   - Run Exact ILP optimization with 5000 total units
   - Compute optimal allocation: {WH-01: 1200, WH-02: 850, ...}
   - Calculate metrics: Cost=10,403,500 DZD, Service=100%, Fitness=0.4695
   - Save to database with status="pending_approval"
   - Return results to frontend
6. **Display Results:** Frontend renders charts, tables, recommendations
7. **Review:** Sarah analyzes results, satisfied with 100% service level and 2.6% cost savings
8. **Approve:** Click "Approve & Execute" → Confirmation modal → Click "Confirm"
9. **Execution:**
   - Backend updates warehouse stock levels in database
   - Generates 8 transfer orders (for warehouses with changes > 10 units)
   - Sends email notifications to warehouse managers
   - Updates optimization result status to "executed"
   - Logs action in audit trail
10. **Confirmation:** Frontend shows success toast → Redirect to dashboard
11. **Monitoring:** Over next 4 weeks, Sarah tracks actual sales vs. forecast on dashboard

---

## Summary

### Platform Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| Frontend | React | User interface |
| API | Flask/FastAPI | REST endpoints |
| Forecasting | SARIMAX (statsmodels) | Demand prediction |
| Optimization | Exact ILP (PuLP + CBC) | Stock allocation |
| Database | PostgreSQL | Data persistence |
| Cache | Redis | Performance |
| Queue | Celery + RabbitMQ | Async tasks |
| Monitoring | Prometheus + Grafana | Metrics |
| Logging | ELK Stack | Centralized logs |
| Deployment | Docker + Kubernetes | Orchestration |

### Key Benefits

1. **End-to-End Automation:** From forecast to execution in minutes
2. **Optimal Decisions:** Exact ILP guarantees best cost-service trade-off
3. **Transparency:** Clear visualizations and recommendations
4. **Auditability:** Complete trail of decisions and approvals
5. **Scalability:** Containerized architecture supports growth
6. **Maintainability:** Modular design with clear separation of concerns

---

**Document Version:** 1.0  
**Last Updated:** May 21, 2026  
**For:** Master's Thesis - Warehouse Optimization Platform
